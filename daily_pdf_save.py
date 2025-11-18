import os
import json
import requests
from datetime import datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# ================================================
# 1. Secrets からサービスアカウント情報を読み込む
# ================================================
creds_json = os.environ.get("GOOGLE_DRIVE_SERVICE_ACCOUNT")
if not creds_json:
    print("エラー: GOOGLE_DRIVE_SERVICE_ACCOUNT が設定されていません。")
    exit(1)

with open("service_account.json", "w") as f:
    f.write(creds_json)


# ================================================
# 2. PDF ダウンロード
# ================================================
today = datetime.now().strftime("%Y-%m-%d")
file_name = f"daily_{today}.pdf"

url = "https://www.hotsukyo.or.jp/pdf/daily.pdf"
r = requests.get(url)
r.raise_for_status()

with open(file_name, "wb") as f:
    f.write(r.content)

print(f"{file_name} をダウンロードしました。")


# ================================================
# 3. Google Drive 認証（ServiceAccount）
# ================================================
gauth = GoogleAuth()
gauth.service_account_file = "service_account.json"
gauth.ServiceAuth()

drive = GoogleDrive(gauth)


# ================================================
# 4. Google Drive にアップロード
# ================================================
file_metadata = {
    "title": file_name
}

gfile = drive.CreateFile(file_metadata)
gfile.SetContentFile(file_name)
gfile.Upload()

print(f"Google Drive にアップロード完了: {file_name}")


# ================================================
# 5. 一時ファイルを削除
# ================================================
os.remove(file_name)
os.remove("service_account.json")
