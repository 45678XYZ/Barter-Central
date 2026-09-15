## 如何設定環境

1. 進入 backend 資料夾

   ```
   cd backend
   ```

2. 執行創建環境的命令:  
   Windows
   ```
   py -m venv .venv
   ```
   Mac
   ```
   python3 -m venv .venv
   ```

## 進入 Virtual Environment (開始寫專案時就要進入)

1. 在 vscode powershell 中打上  
   Windows
   ```
   .\.venv\Scripts\activate
   ```
   Mac
   ```
   source .venv/bin/activate
   ```
2. 開始下載套件
   ```
   pip install -r requirements.txt
   ```

## 設定環境變數

1. 複製範本成 `.env`，再填入 DB、Cognito、S3 的設定（`.env` 已被 gitignore，不會進版控）  
   Windows
   ```
   copy .env.example .env
   ```
   Mac
   ```
   cp .env.example .env
   ```

## 更新或加入套件

1. 安裝你的 Dependency
   ```
   pip install {你的Dependency}
   ```
2. 手動把套件名稱加到 `requirements.txt`（一行一個）

   > 不要用 `pip freeze > requirements.txt`：會把所有間接依賴一起寫進去，而且在 Windows PowerShell 會存成 UTF-16，git 會把它當成二進位檔而看不到 diff。

## 如何開啟後端 FastAPI server

1. 進入 backend 資料夾
   ```
   cd backend
   ```
2. 開啟 server
   ```
   uvicorn src.main:app --reload
   ```
