import os
import requests
import json
import time
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# ----------------------------------------------------
# 1. 認証情報を環境変数から読み込み、一時ファイルに保存
# ----------------------------------------------------
# GitHub Secrets に登録した JSON 全体を取得
CREDS_JSON = os.environ.get("GOOGLE_DRIVE_CREDENTIALS")
TEMP_CREDS_FILE = "client_secrets.json" # pydriveがServiceAuth()で探すファイル名

if not CREDS_JSON:
    print("エラー: GOOGLE_DRIVE_CREDENTIALS が環境変数に設定されていません。")
    exit(1)

# JSON文字列を解析し、整形してから一時ファイルとして書き出す
try:
    # 環境変数から受け取ったJSON文字列を解析
    creds_data = json.loads(CREDS_JSON) 
    
    # 整形したJSONを一時ファイルとして書き出す
    with open(TEMP_CREDS_FILE, "w", encoding="utf-8") as f:
        json.dump(creds_data, f, indent=4) # indent=4で整形して書き込み
except json.JSONDecodeError as e:
    print(f"エラー: 認証情報のJSON解析に失敗しました。Secretsの値を確認してください。詳細: {e}")
    exit(1)
except Exception as e:
    print(f"エラー: 認証情報の書き出しに失敗しました: {e}")
    exit(1)

print(f"認証情報 ({TEMP_CREDS_FILE}) の書き出しに成功しました。")

# ----------------------------------------------------
# 2. PDF のダウンロード
# ----------------------------------------------------
today = datetime.now().strftime("%Y-%m-%d")
file_name = f"daily_{today}.pdf"
url = "https://www.hotsukyo.or.jp/pdf/daily.pdf"

try:
    print(f"PDFダウンロード開始: {url}")
    r = requests.get(url)
    r.raise_for_status() # HTTPエラーがあれば例外を発生させる

    with open(file_name, "wb") as f:
        f.write(r.content)
    print(f"PDFダウンロード完了: {file_name}")

except requests.exceptions.RequestException as e:
    print(f"エラー: PDFのダウンロードに失敗しました: {e}")
    exit(1)


# ----------------------------------------------------
# 3. Google Drive 認証 (Service Account) とアップロード
# ----------------------------------------------------
gauth = GoogleAuth()

# ★★★ ここから3行を追加/修正します ★★★
# pydriveの設定を上書きし、認証情報ファイル(client_secrets.json)の場所を明示的に指定
TEMP_CREDS_FILE = "client_secrets.json" # 変数を再定義（念のため）
gauth.settings['client_config_file'] = TEMP_CREDS_FILE
# ★★★ ここまで追加/修正 ★★★

try:
    # Google Drive 認証 (Service Account)
    gauth = GoogleAuth()
    gauth.ServiceAuth() # client_secrets.json を使って非対話的に認証
    drive = GoogleDrive(gauth)
    print("Google Drive 認証に成功しました。")

    # Google Drive にアップロード
    # 特定のフォルダにアップロードする場合は 'parents': [{'id': 'フォルダID'}] を追加
    gfile = drive.CreateFile({'title': file_name}) 
    gfile.SetContentFile(file_name)
    gfile.Upload()
    
    print(f"✅ {file_name} を Google Drive に保存しました。")

except Exception as e:
    print(f"エラー: Google Drive へのアップロードに失敗しました。権限と認証情報をご確認ください。詳細: {e}")
    exit(1)

finally:
    # ----------------------------------------------------
    # 4. 後処理 (一時ファイルとダウンロードしたPDFを削除)
    # ----------------------------------------------------
    # ダウンロードしたPDFを削除
    if os.path.exists(file_name):
        os.remove(file_name)
    
    # 認証情報を一時的に保存したファイルを削除
    if os.path.exists(TEMP_CREDS_FILE):
        os.remove(TEMP_CREDS_FILE)
