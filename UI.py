HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Smart Lock Admin</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
:root {
  --bg: #0f172a; --card: #1e293b; --txt: #f8fafc; --muted: #94a3b8;
  --primary: #3b82f6; --success: #10b981; --danger: #ef4444; --warning: #f59e0b;
  --border: #334155;
}
* { box-sizing: border-box; }
body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--txt); margin: 0; display: flex; flex-direction: column; align-items: center; }

/* Thêm class ẩn hiện cho Login */
.hidden { display: none !important; }
#mainApp { width: 100%; display: flex; flex-direction: column; align-items: center; }

.header { width: 100%; background: var(--card); padding: 20px; text-align: center; border-bottom: 1px solid var(--border); position: relative; }
.header h1 { margin: 0; color: var(--primary); }
.header p  { color: var(--muted); font-size: 14px; margin: 4px 0 0; }
.container { width: 95%; max-width: 1200px; margin-top: 30px; display: grid; grid-template-columns: 1fr 2fr; gap: 20px; }
.col { display: flex; flex-direction: column; gap: 20px; }
.card { background: var(--card); border-radius: 12px; padding: 24px; border: 1px solid var(--border); }
.card h2 { margin: 0 0 20px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }
.fg    { margin-bottom: 15px; }
.row   { display: flex; gap: 10px; }
label  { display: block; font-size: 13px; color: var(--muted); margin-bottom: 4px; }
input, select { background: rgba(0,0,0,.2); border: 1px solid var(--border); color: #fff; padding: 10px; border-radius: 6px; width: 100%; }
input:disabled { opacity: 0.35; cursor: not-allowed; }
.btn       { padding: 10px 15px; border-radius: 6px; border: none; cursor: pointer; font-weight: bold; color: #fff; width: 100%; transition: all 0.2s;}
.btn-blue  { background: var(--primary); }
.btn-green { background: var(--success); }
.btn-warn  { background: var(--warning); color: #000; }
.btn-sm    { background: rgba(239,68,68,.15); color: var(--danger); width: auto; padding: 5px 10px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.tbl-wrap { max-height: 300px; overflow: auto; border-radius: 8px; border: 1px solid var(--border); }
.tbl-wrap.tall { max-height: 400px; }
table  { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid var(--border); }
th     { background: var(--bg); color: var(--primary); font-size: 13px; position: sticky; top: 0; z-index: 10; }
tbody tr:hover { background: rgba(59,130,246,.1); }
.empty { text-align: center; color: var(--muted); }
.badge { padding: 5px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; border: 1px solid transparent; }
.s { background: rgba(16,185,129,.1); color: var(--success); border-color: rgba(16,185,129,.3); }
.d { background: rgba(239,68,68,.1);  color: var(--danger);  border-color: rgba(239,68,68,.3); }
.w { background: rgba(245,158,11,.1); color: var(--warning); border-color: rgba(245,158,11,.3); }
.p { background: rgba(59,130,246,.1); color: var(--primary); border-color: rgba(59,130,246,.3); }
.toast { position: fixed; bottom: 24px; right: 24px; padding: 12px 18px; border-radius: 8px; font-size: 13px; font-weight: bold; z-index: 999; transition: opacity .3s; }
.toast.ok  { background: var(--success); color: #fff; }
.toast.err { background: var(--danger);  color: #fff; }
hr { border-color: var(--border); margin: 25px 0; }

/* Hoạt ảnh nhấp nháy cho nút Thêm thẻ */
@keyframes blinker { 50% { opacity: 0.5; } }
.blinking { animation: blinker 1s linear infinite; background: var(--danger) !important; color: white !important;}
</style>
</head>
<body>

<div id="loginScreen" class="card" style="margin: 100px auto; max-width: 400px; width: 90%;">
  <h2 style="text-align:center; color:var(--primary); border-bottom:none;"><i class="fa-solid fa-lock"></i> ĐĂNG NHẬP ADMIN</h2>
  <div class="fg">
    <label>Tài khoản</label>
    <input id="loginUser" placeholder="Tài khoản...">
  </div>
  <div class="fg">
    <label>Mật khẩu</label>
    <input type="password" id="loginPass" placeholder="Mật khẩu...">
  </div>
  <button class="btn btn-blue" onclick="doLogin()">ĐĂNG NHẬP</button>
</div>

<div id="mainApp" class="hidden">
  <div class="header">
    <h1><i class="fa-solid fa-building-shield"></i> QL Cửa Kí Túc Xá</h1>
    <p>FastAPI + PostgreSQL + FreeRTOS</p>
    <button class="btn-sm" style="position:absolute; right:20px; top:25px; background:transparent; border:1px solid var(--danger)" onclick="doLogout()">
        <i class="fa-solid fa-right-from-bracket"></i> Đăng xuất
    </button>
  </div>

  <div class="container">
    <div class="card">
      <h2><i class="fa-solid fa-address-card"></i> Cấp quyền thẻ mới</h2>
      
      <button class="btn btn-warn" id="learnBtn" onclick="startLearningMode()" style="margin-bottom:20px; font-size: 15px;">
        <i class="fa-solid fa-wifi"></i> QUẸT THẺ VÀO MẠCH ĐỂ THÊM
      </button>
      <div style="text-align:center; color:var(--muted); font-size:12px; margin-bottom:20px;">--- HOẶC THÊM THỦ CÔNG ---</div>

      <div class="fg">
        <label>Mã thẻ UID (VD: 27C3E906)</label>
        <input id="uid" placeholder="Nhập mã UID..." maxlength="20">
      </div>
      <div class="fg">
        <label>Tên người dùng</label>
        <input id="name" placeholder="VD: Sinh viên A">
      </div>
      <div class="fg">
        <label>Vai trò</label>
        <select id="role" onchange="toggleTime()">
          <option value="Sinh viên">Sinh viên (Có giờ giới nghiêm)</option>
          <option value="Lao công">Lao công (Giờ hành chính)</option>
          <option value="Master">Master (24/7)</option>
        </select>
      </div>
      <div class="row fg" id="timeRow">
        <div style="flex:1"><label>Từ:</label><input type="time" id="ts" value="05:00"></div>
        <div style="flex:1"><label>Đến:</label><input type="time" id="te" value="23:30"></div>
      </div>
      <button class="btn btn-blue" id="saveBtn" onclick="addCard()">
        <i class="fa-solid fa-plus"></i> LƯU VÀO DATABASE
      </button>

      <hr>

      <h2><i class="fa-solid fa-flask"></i> Giả lập quẹt thẻ</h2>
      <select id="simCard" class="fg"></select>
      <button class="btn btn-green" id="simBtn" onclick="simulateCard()" style="margin-top:8px">
        <i class="fa-solid fa-laptop-code"></i> QUẸT GIẢ LẬP TRÊN WEB
      </button>
    </div>

    <div class="col">
      <div class="card" style="display:flex;justify-content:space-between;align-items:center;padding:15px 24px">
        <h3 id="doorStatus" style="margin:0;color:var(--primary)">Đang tải...</h3>
        <button class="btn btn-blue" style="width:150px" onclick="openDoor()"><i class="fa-solid fa-unlock"></i> MỞ TỪ XA</button>
      </div>

      <div class="card">
        <h2><i class="fa-solid fa-users"></i> Danh sách thẻ quản lý</h2>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>UID</th><th>Tên</th><th>Vai trò</th><th>Khung giờ</th><th>Hành động</th></tr></thead>
            <tbody id="cardTable"></tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <h2><i class="fa-solid fa-clock-rotate-left"></i> Nhật ký hệ thống</h2>
        <div class="tbl-wrap tall">
          <table>
            <thead><tr><th>Thời gian</th><th>Đối tượng</th><th>Ghi chú</th></tr></thead>
            <tbody id="logTable"></tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
const $ = id => document.getElementById(id);
const badgeMap = { success: "s", danger: "d", warning: "w", primary: "p" };
let pollTimer = null;

function toast(msg, type = "ok") {
  const el = Object.assign(document.createElement("div"), { className: "toast " + type, innerText: msg });
  document.body.appendChild(el);
  setTimeout(() => { el.style.opacity = "0"; setTimeout(() => el.remove(), 300); }, 2500);
}

// --- LOGIC ĐĂNG NHẬP ---
if (localStorage.getItem("isLoggedIn") === "true") {
  $("loginScreen").classList.add("hidden");
  $("mainApp").classList.remove("hidden");
  startPolling();
  fetchData();
}

function doLogin() {
  const u = $("loginUser").value.trim();
  const p = $("loginPass").value.trim();
  
  fetch("/api/login", {
    method: "POST", 
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({username: u, password: p})
  })
  .then(response => response.json()) // Nhận JSON từ server
  .then(data => {
    if(data.status === "success") {
      localStorage.setItem("isLoggedIn", "true");
      location.reload();
    } else {
      // Hiển thị nội dung lỗi từ Backend (message hoặc detail)
      const errorMsg = data.message || data.detail || "Lỗi đăng nhập!";
      toast(errorMsg, "err"); 
    }
  })
  .catch(e => {
    console.error(e);
    toast("Không thể kết nối đến máy chủ!", "err");
  });
}

function doLogout() {
  localStorage.removeItem("isLoggedIn");
  location.reload();
}

// --- LOGIC THÊM THẺ TỰ ĐỘNG ---
function startLearningMode() {
  fetch("/api/learning_mode", { method: "POST" })
    .then(r => r.json())
    .then(d => { toast(d.message); fetchData(); })
    .catch(e => toast("Lỗi kích hoạt: " + e.message, "err"));
}

function toggleTime() {
  const isMaster = $("role").value === "Master";
  $("timeRow").style.opacity = isMaster ? "0.35" : "1";
  $("ts").disabled = isMaster;
  $("te").disabled = isMaster;
}

// Thêm / Cập nhật thủ công
function addCard() {
  const uid  = $("uid").value.trim().replace(/\s/g, "").toUpperCase();
  const name = $("name").value.trim();
  if (!uid || !name) { toast("Thiếu thông tin!", "err"); return; }
  if (!/^[0-9A-F]{4,20}$/.test(uid)) { toast("UID không hợp lệ (phải là hex, 4–20 ký tự)", "err"); return; }
  const isMaster = $("role").value === "Master";
  const body = {
    uid, name,
    role:       $("role").value,
    time_start: isMaster ? "00:00:00" : $("ts").value + ":00",
    time_end:   isMaster ? "23:59:59" : $("te").value + ":00",
  };
  $("saveBtn").disabled = true;
  fetch("/api/cards", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
  .then(r => {
    if (!r.ok) throw new Error("HTTP " + r.status);
    $("uid").value = $("name").value = "";
    
    // Reset nút LƯU sau khi cập nhật thành công
    $("saveBtn").innerHTML = '<i class="fa-solid fa-plus"></i> LƯU VÀO DATABASE';
    $("saveBtn").style.backgroundColor = ""; 

    toast("Đã lưu thẻ thành công!");
    fetchData();
  })
  .catch(e => toast("Lỗi lưu thẻ: " + e.message, "err"))
  .finally(() => { $("saveBtn").disabled = false; });
}

// Báo mất (Loại bỏ)
function deleteCard(uid) {
  if (!confirm("BÁO MẤT THẺ: Bạn có chắc chắn muốn hủy thẻ " + uid + " không?\nCửa sẽ từ chối mở cho thẻ này!")) return;
  fetch("/api/cards/" + uid, { method: "DELETE" })
    .then(r => { if (!r.ok) throw new Error("HTTP " + r.status); toast("Đã hủy thẻ " + uid, "err"); fetchData(); })
    .catch(e => toast("Lỗi báo mất thẻ: " + e.message, "err"));
}

function openDoor() {
  fetch("/api/admin_open", { method: "POST" })
    .then(r => { if (!r.ok) throw new Error("HTTP " + r.status); fetchData(); })
    .catch(e => toast("Lỗi mở cửa: " + e.message, "err"));
}

function simulateCard() {
  const val = $("simCard").value;
  if (!val) { toast("Chưa có thẻ để giả lập!", "err"); return; }
  $("simBtn").disabled = true;
  fetch("/api/simulate/" + val, { method: "POST" })
    .then(r => { if (!r.ok) throw new Error("HTTP " + r.status); fetchData(); })
    .catch(e => toast("Lỗi giả lập: " + e.message, "err"))
    .finally(() => { $("simBtn").disabled = false; });
}

function safeDate(raw) {
  const d = new Date(raw);
  return isNaN(d) ? raw : d.toLocaleString("vi-VN");
}

function fetchData() {
  // Bỏ qua fetch nếu chưa đăng nhập
  if (localStorage.getItem("isLoggedIn") !== "true") return;

  fetch("/api/data")
    .then(r => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then(d => {
      $("doorStatus").innerText = "Trạng thái cửa: " + d.status;
      
      // Xử lý nút Quẹt thẻ tự động
      let lBtn = $("learnBtn");
      if (d.is_learning) {
          lBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> ĐANG CHỜ BẠN QUẸT THẺ...';
          lBtn.classList.add("blinking");
          lBtn.disabled = true;
      } else {
          lBtn.innerHTML = '<i class="fa-solid fa-wifi"></i> QUẸT THẺ VÀO MẠCH ĐỂ THÊM';
          lBtn.classList.remove("blinking");
          lBtn.disabled = false;
      }

      let cHtml = "", opts = '<option value="">-- Chọn thẻ --</option><option value="UNKNOWN">Thẻ rác chưa đăng ký</option>';
      d.cards.forEach(c => {
        const t = c.role === "Master" ? "24/7" : `${c.time_start.slice(0,5)} – ${c.time_end.slice(0,5)}`;
        
        // Tạo giao diện trạng thái và Nút Khóa/Mở Khóa
        const statusBadge = c.is_active ? '<span class="badge s">Hoạt động</span>' : '<span class="badge d">Bị Khóa</span>';
        const lockBtnIcon = c.is_active ? '<i class="fa-solid fa-lock"></i> Khóa' : '<i class="fa-solid fa-unlock"></i> Mở';
        const lockBtnColor = c.is_active ? 'background: var(--warning); color: #000;' : 'background: var(--success); color: #fff;';
        
        cHtml += `<tr style="cursor: pointer; ${!c.is_active ? 'opacity: 0.6;' : ''}" title="Bấm vào đây để chỉnh sửa thông tin"
            onclick="fillEditForm('${c.uid}', '${c.name}', '${c.role}', '${c.time_start}', '${c.time_end}')">
          <td style="font-family:monospace;color:var(--warning)">${c.uid}</td>
          <td><b>${c.name}</b> <br> ${statusBadge}</td>
          <td>${c.role}</td>
          <td>${t}</td>
          <td>
            <button class="btn-sm" style="${lockBtnColor} margin-right: 5px;" onclick="toggleCardLock('${c.uid}'); event.stopPropagation();">${lockBtnIcon}</button>
            <button class="btn-sm" style="background:rgba(239,68,68,.15); color:var(--danger);" onclick="deleteCard('${c.uid}'); event.stopPropagation();"><i class="fa-solid fa-trash"></i> Xóa</button>
          </td>
        </tr>`;
        opts += `<option value="${c.uid}">Test: ${c.name} (${c.role})</option>`;
      });
      $("cardTable").innerHTML = cHtml || `<tr><td colspan="5" class="empty">Chưa có thẻ nào.</td></tr>`;
      $("simCard").innerHTML = opts;
      $("simBtn").disabled = d.cards.length === 0;
      
      let lHtml = "";
      d.logs.forEach(l => {
        const cls = badgeMap[l.type] || "p";
        lHtml += `<tr>
          <td style="font-size:12px;color:var(--muted)">${safeDate(l.time)}</td>
          <td><b>${l.user}</b></td>
          <td><span class="badge ${cls}">${l.action}</span></td>
        </tr>`;
      });
      $("logTable").innerHTML = lHtml || `<tr><td colspan="3" class="empty">Chưa có lịch sử.</td></tr>`;
    })
    .catch(() => {});
}
function toggleCardLock(uid) {
  fetch(`/api/cards/${uid}/toggle_lock`, { method: "PUT" })
    .then(r => { if (!r.ok) throw new Error("Lỗi mạng"); return r.json(); })
    .then(d => {
      toast(d.is_active ? "Đã MỞ KHÓA thẻ!" : "Đã KHÓA thẻ an toàn!");
      fetchData();
    })
    .catch(e => toast("Lỗi khi đổi trạng thái: " + e.message, "err"));
}

// Cập nhật lại câu hỏi khi bấm XÓA cho chuẩn xác
function deleteCard(uid) {
  if (!confirm("CẢNH BÁO: XÓA VĨNH VIỄN thẻ " + uid + "?\nDữ liệu sẽ mất hoàn toàn, nếu chỉ mất thẻ tạm thời hãy dùng nút KHÓA!")) return;
  fetch("/api/cards/" + uid, { method: "DELETE" })
    .then(r => { if (!r.ok) throw new Error("HTTP " + r.status); toast("Đã XÓA thẻ " + uid, "err"); fetchData(); })
    .catch(e => toast("Lỗi xóa thẻ: " + e.message, "err"));
}

function startPolling() {
  stopPolling();
  pollTimer = setInterval(() => { if (!document.hidden) fetchData(); }, 1500);
}
function stopPolling() { if (pollTimer) { clearInterval(pollTimer); pollTimer = null; } }
document.addEventListener("visibilitychange", () => document.hidden ? stopPolling() : startPolling());

// Hàm này sẽ tự động điền dữ liệu lên form khi ấn vào 1 thẻ
function fillEditForm(uid, name, role, start, end) {
    $("uid").value = uid;
    $("name").value = name;
    $("role").value = role;
    
    toggleTime(); // Tự động khóa/mở ô nhập giờ tùy theo Vai trò
    
    $("ts").value = start.substring(0, 5); // Cắt lấy HH:MM
    $("te").value = end.substring(0, 5);
    
    // Đổi màu và chữ nút để người dùng biết là đang Cập nhật
    $("saveBtn").innerHTML = '<i class="fa-solid fa-pen"></i> LƯU CẬP NHẬT';
    $("saveBtn").style.backgroundColor = "var(--success)"; 
}

toggleTime();
</script>
</body>
</html>
"""