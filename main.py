import requests
import os
from dotenv import load_dotenv
load_dotenv()

# --- 設定 ---
EDINETDB_KEY = os.getenv("API_KEY")

EDINET_CODE = "E02144"    # トヨタ自動車のEDINETコード


# --- EDINET DBからBPS・EPSを取得 ---
edb_url = f"https://edinetdb.jp/v1/companies/{EDINET_CODE}/financials"
edb_resp = requests.get(edb_url, params={
    "years": 1,
}, headers={
    "X-API-Key": EDINETDB_KEY,
})

edb_data = edb_resp.json()
latest = edb_data["data"][-1]  # 直近年度（配列は古い順）
bps = latest["bps"]
eps = latest["eps"]
print(f"BPS: {bps:,.1f}円 / EPS: {eps:,.1f}円")

