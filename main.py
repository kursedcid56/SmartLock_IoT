from fastapi import FastAPI
from db import seed, init_db, get_db
from api import router
import uvicorn

# ── KHỞI ĐỘNG ───────────────────────────────────────────
init_db()
seed()

app = FastAPI(title="Smart Lock Admin")
app.include_router(router)

# ── CHẠY TRỰC TIẾP ──────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=False)