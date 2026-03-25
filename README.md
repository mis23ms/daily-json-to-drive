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

## 第一次使用

1. 建立 GitHub repo：`daily-json-to-drive`
2. 把本資料夾全部上傳到 repo 根目錄。
3. 到 GitHub repo 的 **Actions** 頁面，啟用 workflows。
4. 手動執行一次 **Daily JSON to Google Drive**。
5. 到 Google Drive 檢查有沒有出現 `daily_YYYYMMDD.json`。

## 已內建設定

- Workload Identity Provider  
  `projects/40450699519/locations/global/workloadIdentityPools/github/providers/daily-json-to-drive`
- Service Account  
  `my-auto-tools-drive-466@project-471d58b6-37a4-461d-859.iam.gserviceaccount.com`
- Drive Folder ID  
  `1zEkCW3lUWbAIa65XHfINbLDhCKUt-9pY`

## 重跑行為

如果同一天的 `daily_YYYYMMDD.json` 已存在，就會直接更新，不會重複新增第二份。
