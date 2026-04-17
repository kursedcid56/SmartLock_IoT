from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import desc, text
from sqlalchemy.orm import Session
from datetime import datetime,  time as dtime , timedelta
import serial, time, threading
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from db import CardDB, LogDB, SessionLocal, get_db
from UI import HTML_PAGE
from passlib.context import CryptContext
import utils

router = APIRouter()

load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_HASH = os.getenv("ADMIN_PASSWORD_HASH")

door_status = "Đang khóa 🔒"
is_learning_mode = False  # Biến cờ cho chức năng "Thêm thẻ tự động"

try:
    arduino = serial.Serial("COM8", 9600, timeout=1)
    time.sleep(2)
    print("✅ Đã kết nối Arduino")
except Exception:
    arduino = None
    print("⚠️  Mock Mode (không có Arduino)")


# ── HELPERS ─────────────────────────────────────────────
# ── HELPERS ─────────────────────────────────────────────
def add_log(db: Session, user: str, action: str, stype: str):
    db.add(LogDB(user_name=user, action=action, status_type=stype))
    db.commit()

def open_door(db: Session = None, user: str = "Admin (Web)", action: str = "Mở cửa từ xa qua Dashboard"):
    global door_status
    if arduino and arduino.is_open:
        arduino.write(b'M') # Gửi lệnh mở cửa
        arduino.flush()     # BẮT BUỘC CÓ: Ép gửi ngay lập tức
    if db:
        add_log(db, user, action, "primary")
    door_status = "Đang mở 🔓"

    def reset():
        global door_status
        time.sleep(3)
        door_status = "Đang khóa 🔒"
    threading.Thread(target=reset, daemon=True).start()

def process_card(uid: str):
    db = SessionLocal()
    try:
        card = db.query(CardDB).filter(CardDB.uid == uid).first()
        
        # 1. Nếu không tìm thấy thẻ trong DB
        if not card:
            if arduino and arduino.is_open: 
                arduino.write(b'X') # Gửi X -> Arduino báo "The SAI!"
                arduino.flush()
            return add_log(db, f"Thẻ lạ ({uid})", "Từ chối: Thẻ chưa đăng ký", "danger")

        # 2. MỚI: Nếu thẻ tồn tại nhưng đang bị KHÓA (is_active == False)
        if not card.is_active:
            if arduino and arduino.is_open:
                arduino.write(b'K') # Gửi K -> Arduino báo "THE DANG BI KHOA"
                arduino.flush()
            return add_log(db, card.name, "Từ chối: Thẻ đang bị KHÓA tạm thời", "danger")

        # 3. Kiểm tra giờ giấc (như cũ)
        now = datetime.now().time()
        allowed = card.role == "Master" or (card.time_start <= now <= card.time_end)

        if allowed:
            open_door(db, card.name, f"Vào cửa thành công ({card.role})")
        else:
            if arduino and arduino.is_open: 
                arduino.write(b'T') # Gửi T -> Arduino báo "Sai giờ"
                arduino.flush()
            add_log(db, card.name, f"Từ chối: Vi phạm giờ", "warning")
            
    except Exception as e:
        print(f"Lỗi xử lý thẻ: {e}")
    finally:
        db.close()


# ── LUỒNG LẮNG NGHE ARDUINO & THÊM THẺ TỰ ĐỘNG ──────────
def listen():
    global is_learning_mode
    print("▶️ Đã bật luồng lắng nghe Arduino...") # Dòng này để debug xem luồng đã chạy chưa
    while True:
        try:
            if arduino and arduino.is_open and arduino.in_waiting:
                line = arduino.readline().decode(errors="ignore").strip()
                if line.startswith("UID:"):
                    uid = line.split(":")[1].strip().replace(" ", "")
                    print(f"Bắt được thẻ: {uid}") # In ra Terminal để bạn dễ theo dõi
                    
                    if is_learning_mode:
                        db = SessionLocal()
                        existing_card = db.query(CardDB).filter(CardDB.uid == uid).first()

                        if existing_card:
                            arduino.write(b'E') 
                            arduino.flush()
                            print(f"Thẻ {uid} đã có chủ, không thể thêm mới.")
                        else:
                            new_card = CardDB(
                                uid=uid, 
                                name="Thẻ mới", 
                                role="Sinh viên", 
                                time_start=dtime(0, 0), 
                                time_end=dtime(23, 59)
                            )
                            db.add(new_card)
                            db.commit()
                            arduino.write(b'S')
                            arduino.flush()
                            print(f"Đã thêm thành công thẻ: {uid}")
                        
                        db.close()
                        is_learning_mode = False 
                    else:
                        process_card(uid)
        except Exception as e:
            print(f"Lỗi luồng listen: {e}")
        time.sleep(0.1)

# KHỞI ĐỘNG LUỒNG! (Nếu thiếu dòng này, hàm listen sẽ chết đứng)
if arduino:
    threading.Thread(target=listen, daemon=True).start()
# ── ROUTES API ──────────────────────────────────────────
@router.get("/", response_class=HTMLResponse)
def root():
    return HTML_PAGE

# 1. API Đăng nhập
class LoginModel(BaseModel):
    username: str
    password: str

@router.post("/api/login")
def login(data: LoginModel):
    # DÙNG utils.py Ở ĐÂY NÀY:
    # Trả biến data.password (ví dụ "123456") và ADMIN_HASH vào hàm verify
    is_password_correct = utils.verify(data.password, ADMIN_HASH)
    
    # Ra quyết định dựa vào kết quả của utils
    if data.username == ADMIN_USER and is_password_correct:
        return {"status": "success"}
    else:
       return {"status": "error", "message": "Sai tên đăng nhập hoặc mật khẩu!"}
        
    return {"status": "error", "message": "Sai tài khoản hoặc mật khẩu!"}


@router.post("/api/learning_mode")
def enable_learning_mode():
    global is_learning_mode
    if not arduino or not arduino.is_open:
        raise HTTPException(status_code=503, detail="Mạch offline")
        
    is_learning_mode = True
    try:
        arduino.write(b'L')
        arduino.flush() # Ép dữ liệu đi ngay lập tức qua cổng Serial
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi gửi lệnh")
        
    return {"status": "success", "message": "Hãy quẹt thẻ mới!"}
class CardModel(BaseModel):
    uid: str
    name: str
    role: str
    time_start: str
    time_end: str


@router.post("/api/cards")
def create_card(c: CardModel, db: Session = Depends(get_db)):
    db.merge(CardDB(
        uid=c.uid.strip().upper(), name=c.name, role=c.role,
        time_start=dtime.fromisoformat(c.time_start), time_end=dtime.fromisoformat(c.time_end),
    ))
    db.commit()
    return {"status": "success"}

@router.delete("/api/cards/{uid}")
def delete_card(uid: str, db: Session = Depends(get_db)):
    card = db.query(CardDB).filter(CardDB.uid == uid).first()
    
    # NẾU KHÔNG TÌM THẤY THẺ -> NÉM LỖI 404
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Thẻ {uid} không tồn tại hoặc đã bị xóa trước đó!"
        )
        
    db.delete(card)
    db.commit()
    add_log(db, "Admin", f"Đã khóa/xóa thẻ: {uid}", "danger")
    return {"status": "success"}

@router.post("/api/admin_open")
def admin_open(db: Session = Depends(get_db)):
    # KIỂM TRA PHẦN CỨNG TRƯỚC KHI MỞ CỬA
    if not arduino or not arduino.is_open:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="⚠️ Mạch khóa cửa đang offline, không thể mở từ xa!"
        )
        
    try:
        open_door(db) # Gọi hàm mở cửa
    except Exception as e:
        raise HTTPException(status_code=500, detail="⚠️ Lỗi giao tiếp với phần cứng.")
        
    return {"status": "success"}

@router.get("/api/data")
def get_data(db: Session = Depends(get_db)):
    auto_cleanup_logs(db)
    cards = db.query(CardDB).all()
    logs = db.query(LogDB).order_by(desc(LogDB.timestamp)).limit(15).all()
    return {
        "status": door_status,
        "is_learning": is_learning_mode,
        "cards": [{"uid": c.uid, "name": c.name, "role": c.role, "time_start": str(c.time_start), "time_end": str(c.time_end), "is_active": c.is_active} for c in cards],
        "logs": [{"time": l.timestamp.isoformat(), "user": l.user_name, "action": l.action, "type": l.status_type} for l in logs],
    }

@router.put("/api/cards/{uid}/toggle_lock")
def toggle_lock(uid: str, db: Session = Depends(get_db)):
    card = db.query(CardDB).filter(CardDB.uid == uid).first()
    if not card:
        raise HTTPException(status_code=404, detail="Không tìm thấy thẻ")
    
    # Đảo ngược trạng thái (Đang khóa thành mở, đang mở thành khóa)
    card.is_active = not card.is_active
    db.commit()
    
    action_str = "Đã KHÓA thẻ" if not card.is_active else "Đã MỞ KHÓA thẻ"
    stype = "warning" if not card.is_active else "success"
    add_log(db, "Admin", f"{action_str}: {uid}", stype)
    
    return {"status": "success", "is_active": card.is_active}
def auto_cleanup_logs(session):
    """
    Tự động xóa nhật ký cũ hơn 7 ngày để tối ưu dung lượng.
    Cơ chế này chạy ngầm và không cần sự can thiệp của người dùng.
    """
    try:
        # Tính toán mốc thời gian: Hiện tại trừ đi 7 ngày
        limit_date = datetime.now() - timedelta(days=7)
        
        # Thực hiện xóa các bản ghi có timestamp nhỏ hơn mốc 7 ngày
        session.execute(
            text("DELETE FROM logs WHERE timestamp < :limit"),
            {"limit": limit_date}
        )
        session.commit()
    except Exception as e:
        # Nếu lỗi (ví dụ DB đang lock), bỏ qua để không làm treo hệ thống
        print(f"Lỗi dọn dẹp tự động: {e}")



