import yfinance as yf
import requests
import os
from term_printer import Color, cprint, StdText, Format
from dotenv import load_dotenv
load_dotenv()

stock_code = '7203.T'
EDINET_CODE = "E02144" 
EDINETDB_KEY = os.getenv("API_KEY")


# --- EDINET DBから【財務データ】を取得 ---
edb_url = f"https://edinetdb.jp/v1/companies/{EDINET_CODE}/financials"
edb_resp = requests.get(edb_url, params={"years": 1}, headers={"X-API-Key": EDINETDB_KEY})

if edb_resp.status_code == 200:
    # 取得したJSONデータから最新の年度のデータを取得
    data_dict = edb_resp.json()
    edinet_data = data_dict['data'][0]
else:
    print("EDINET DBからのデータ取得に失敗しました。")
    exit()

# --- yfinanceから【市場データ】を取得 ---
ticker = yf.Ticker(stock_code)
stock_price = ticker.history(period='1d')['Close'].iloc[-1]
market_cap = ticker.info.get('marketCap')



print('\n----------------------------------------------------------')

cprint(f"{StdText('最新の決算データ年度', Color.BRIGHT_MAGENTA)}: {edinet_data.get('fiscal_year', '不明')}")

# 【収益性の指標】
net_income = edinet_data['net_income']
total_equity = edinet_data['shareholders_equity']
total_assets = edinet_data['total_assets']
revenue = edinet_data['revenue']

# ROE
roe = (net_income / total_equity) * 100
cprint(f"{StdText('ROE', Color.BRIGHT_YELLOW)}: {roe:.2f} {StdText('(一般的な目安としては8～10%。)', Color.BRIGHT_BLACK)}")

# ROA
roa = (net_income / total_assets) * 100
cprint(f"{StdText('ROA', Color.BRIGHT_YELLOW)}: {roa:.2f} {StdText('(5%以上の企業が優良企業。)', Color.BRIGHT_BLACK)}")

# 【効率性の指標】
# 棚卸資産回転日数
inventory = edinet_data.get('inventories', 0)
cost_of_sales = edinet_data.get('cost_of_sales', 1) # 0割り防止
inventory_period = inventory / (cost_of_sales / 365)
cprint(f"{StdText('棚卸資産回転日数', Color.BRIGHT_MAGENTA)}: {inventory_period:.2f}日分")

# 売上債権回転日数
receivables = edinet_data.get('trade_receivables', 0)
receivables_period = receivables / (revenue / 365)
cprint(f"{StdText('売上債権回転日数', Color.BRIGHT_MAGENTA)}: {receivables_period:.2f}日分")

# 【安全性指標】
# 自己資本比率
equity_ratio = (total_equity / total_assets) * 100
cprint(f"{StdText('自己資本比率', Color.BRIGHT_MAGENTA)}: {equity_ratio:.2f}%")

# 有利子負債（短期 + 長期）
all_debt = edinet_data.get('ibd_current', 0) + edinet_data.get('ibd_noncurrent', 0)
cprint(f"{StdText('有利子負債', Color.BRIGHT_CYAN)}: {all_debt / 100000000:.2f}億円")

# 【バリュエーション（財務 × 株価）】
eps = edinet_data['eps']
bps = edinet_data['bps']

cprint(f"{StdText('現在の株価', Color.BG_BRIGHT_WHITE)}: {stock_price:.2f}円")
cprint(f"{StdText('PER', Color.BRIGHT_CYAN)}: {stock_price / eps:.2f}倍")
cprint(f"{StdText('PBR', Color.BRIGHT_CYAN)}: {stock_price / bps:.2f}倍")

print('----------------------------------------------------------\n')