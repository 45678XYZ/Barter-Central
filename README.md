# 物物阿阿！中央大學返璞歸真福利社

專為中央大學打造的交易系統，使用中央大學信箱 (`@g.ncu.edu.tw`) 登入後就能在校園內刊登並交易物品。交換頁面內建聊天功能，讓雙方直接溝通並選定交易地點，打造方便的以物易物社群，讓舊物品發揮新價值

## 技術架構

| 項目 | 技術 |
| --- | --- |
| 前端 | Vue 3、Vite、Pinia、Vue Router、Axios |
| 後端 | FastAPI、SQLAlchemy（每個模組分成 domain / application / infrastructure / presentation 四層） |
| 資料庫 | Amazon RDS MySQL 8.0 |
| 登入 | Amazon Cognito |
| 部署 | CloudFormation：VPC、ALB、Auto Scaling Group（EC2 + Nginx + Uvicorn）、S3（前端靜態網站、物品圖片、後端部署包） |

## 專案結構

```
.
├── frontend/              # Vue 前端
│   └── src/
│       ├── api/           # 呼叫後端 API（auth、items、exchanges）
│       ├── components/
│       ├── router/
│       ├── stores/        # Pinia（登入狀態）
│       └── views/
├── backend/               # FastAPI 後端
│   └── src/
│       ├── main.py        # App 進入點：CORS、註冊路由
│       ├── database.py    # RDS 連線與建立 table
│       └── modules/
│           ├── iam/       # 登入與使用者（Cognito）
│           ├── inventory/ # 物品刊登、查詢、圖片上傳（S3）
│           └── exchanges/ # 交換請求、聊天訊息、面交地點
├── IaC/                   # CloudFormation stacks（network → security → data → app）
└── .github/workflows/     # 檢查只有 dev 分支能合併進 main
```

## 開發＆部署

### 本機開發

後端（完整步驟見 [backend/Setup_Guide.md](backend/Setup_Guide.md)）：

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # 填入 DB、Cognito、S3 設定
uvicorn src.main:app --reload     # http://localhost:8000
```

前端：

```bash
cd frontend
npm install
npm run dev                       # http://localhost:5173
```

前端連線的 API 位址設定在 `frontend/.env`；執行 `npm run build` 打包部署時，會改用 `frontend/.env.production` 的設定

### 部署

使用 CloudFormation 依序建立 network → security → data → app 四個 stack，詳細步驟見 [IaC/README.md](IaC/README.md) 與 [IaC/Cloudformation.md](IaC/Cloudformation.md)
