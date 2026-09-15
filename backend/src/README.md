## iam 模組
1. Frontend 透過 Cognito 登入後，把拿到的 authorization code 傳給後端。
2. Backend 用 code 向 Cognito 換取 ID Token，並驗證 Token 合法性。
3. Backend 檢查 email 是否屬於允許的網域 (`ALLOWED_EMAIL_DOMAIN`，預設 `g.ncu.edu.tw`)。
4. Backend 檢查資料庫有無此人：
* 若無：自動註冊 (將 Cognito 資料寫入 MySQL)。
* 若有：更新姓名與大頭貼。
5. Backend 回傳使用者資訊與 access token。
