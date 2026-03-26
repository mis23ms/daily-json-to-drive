# daily-json-to-drive

每天台灣時間 19:30 抓 5 個 JSON，合成 `daily_YYYYMMDD.json`，再上傳到指定 Google Drive 資料夾。

## 來源

- https://mis23ms.github.io/tw-stock-futures/summary.json
- https://mis23ms.github.io/tw-stock-options/options_data.json
- https://mis23ms.github.io/tw-stock-06/summary.json
- https://raw.githubusercontent.com/mis23ms/tw-stock-06/main/docs/data.json
- https://mis23ms.github.io/us-market-tracker/data/etf.json

## 產出格式

外層會增加：
- `file_name`
- `generated_at_taipei`
- `generated_at_utc`
- `source_urls`
- `data`

`data` 裡面保留 5 份原始 JSON 內容，不改欄位、不改值。

## GitHub Secrets

到 repo：
**Settings → Secrets and variables → Actions**

新增 3 個 repository secrets：
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REFRESH_TOKEN`

## 第一次使用

1. 用這個資料夾內容覆蓋 repo。
2. 到 GitHub repo 的 **Settings → Secrets and variables → Actions**，新增 3 個 secrets。
3. 到 GitHub repo 的 **Actions** 頁面，啟用 workflows。
4. 手動執行一次 **Daily JSON to Google Drive**。
5. 到 Google Drive 檢查有沒有出現 `daily_YYYYMMDD.json`。

## 重要

如果你的 OAuth app 還是 **Testing**，refresh token 可能在 7 天後失效。請把 Google Auth Platform 的 publishing status 改成 **In production**，再重拿一次 refresh token。

## 目前指定資料夾

程式已固定使用這個 Google Drive folder ID：
`1zEkCW3lUWbAIa65XHfINbLDhCKUt-9pY`
