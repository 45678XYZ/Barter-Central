from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 先載入 .env，後面 import 的模組才讀得到環境變數
load_dotenv()

from .modules.exchanges.presentation.router import router as exchange_router
from .modules.iam.presentation.router import router as iam_router
from .modules.inventory.presentation.router import router as inventory_router

# 初始化 App
app = FastAPI(title="AWS Finals API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.yueyue.site",
        "https://www.xid3.site",
        "https://www.aaron2.site",
        "https://www.ian2.site",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 註冊各模組的路由 (Include Routers) ---
app.include_router(iam_router)
app.include_router(inventory_router)
app.include_router(exchange_router)


@app.get("/")
def read_root():
    return {"message": "Server is running!"}
