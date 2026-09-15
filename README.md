# AWS Finals

校園二手物品交換平台：使用中央大學信箱 (`@g.ncu.edu.tw`) 登入後，可以刊登物品、瀏覽與搜尋、對物品提出交換請求，並在交換頁面聊天、約定面交地點與確認交易。

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

## 本機開發

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

前端連線的 API 位址設定在 `frontend/.env`（開發）與 `frontend/.env.production`（正式站）。

## 部署

- 建立 AWS 資源：[IaC/README.md](IaC/README.md)、[IaC/Cloudformation.md](IaC/Cloudformation.md)
- 分支流程：只有 `dev` 可以發 PR 合併進 `main`（由 GitHub Actions 檢查）
