import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Time, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, time as dtime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 1. Khởi tạo Engine và Session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Định nghĩa Models (Chỉ định nghĩa 1 lần duy nhất ở đây)
class CardDB(Base):
    __tablename__ = "cards"
    uid = Column(String, primary_key=True, index=True)
    name = Column(String)
    role = Column(String) 
    time_start = Column(Time)
    time_end = Column(Time)
    is_active = Column(Boolean, default=True) # Cột mới xịn xò đây

class LogDB(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now)
    user_name = Column(String)
    action = Column(String)
    status_type = Column(String)

# 3. Hàm tạo bảng (Lệnh create_all đặt ở đây)
def init_db():
    Base.metadata.create_all(bind=engine)

# 4. Dependency cho FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. Hàm Seed dữ liệu (Viết gọn lại)
def seed():
    db = SessionLocal()
    try:
        if not db.query(CardDB).count():
            print("🌱 Đang nạp thẻ mẫu...")
            db.add_all([
                CardDB(uid="27C3E906", name="Quản Lí", role="Master",
                       time_start=dtime(0, 0), time_end=dtime(23, 59), is_active=True),
                CardDB(uid="34322307", name="Trần Thị B (SV)", role="Sinh viên",
                       time_start=dtime(5, 0), time_end=dtime(23, 30), is_active=True),
                CardDB(uid="316BB07B", name="Cô Lan (Lao công)", role="Lao công",
                       time_start=dtime(8, 0), time_end=dtime(17, 0), is_active=True),
            ])
            db.commit()

        if not db.query(LogDB).count():
            print("🌱 Đang nạp log mẫu...")
            db.add_all([
                LogDB(user_name="Hệ thống", action="Khởi tạo cơ sở dữ liệu thành công", status_type="success"),
            ])
            db.commit()
    except Exception as e:
        print(f"❌ Lỗi Seed: {e}")
    finally:
        db.close()

# Chạy khởi tạo ngay khi file được thực thi trực tiếp
if __name__ == "__main__":
    init_db()
    seed()
    print("✅ Database đã sẵn sàng!")