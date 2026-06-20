import yfinance as yf
import requests
import os
from term_printer import Color, cprint, StdText, Format
from dotenv import load_dotenv
load_dotenv()


stock_code = '7203.T'
EDINET_CODE = "E02144"
EDINETDB_KEY = os.getenv("API_KEY")


# --- 1. データ取得 ---
edb_url = f"https://edinetdb.jp/v1/companies/{EDINET_CODE}/financials"
edb_resp = requests.get(edb_url, params={"years": 2}, headers={"X-API-Key": EDINETDB_KEY})

if edb_resp.status_code == 200:
    data_list = edb_resp.json().get('data', [])
    # 提出日（submit_date）が新しい順にソートする
    data_list.sort(key=lambda x: x.get('submit_date', ''), reverse=True)
    edinet_data = data_list[0] # 最新データ
    edinet_data_prev = data_list[1] if len(data_list) > 1 else None # 前年データ
else:
    print("EDINET DBからのデータ取得に失敗しました。")
    exit()

ticker = yf.Ticker(stock_code)
hist = ticker.history(period='1d')
stock_price = hist['Close'].iloc[-1] if not hist.empty else 0
market_cap = ticker.info.get('marketCap', 0)


# --- 2. 変数定義・共通計算 ---
net_income = edinet_data['net_income']
total_equity = edinet_data['shareholders_equity']
total_assets = edinet_data.get('total_assets', 1)
revenue = edinet_data['revenue']
operating_income = edinet_data.get('operating_income', 0)
sga = edinet_data.get('sga', 0) # 販管費
num_employees = edinet_data.get('num_employees', 1)
all_debt = edinet_data.get('ibd_current', 0) + edinet_data.get('ibd_noncurrent', 0)
cash = edinet_data.get('cash', 0)
depreciation = edinet_data.get('depreciation', 0)

# 算出数値（粗利・売上原価を推計）
gross_profit = operating_income + sga
cost_of_sales = revenue - gross_profit

# 効率性・安全性指標
current_assets = edinet_data.get('current_assets', 0)
inventories = edinet_data.get('inventories', 0)
current_liabilities = edinet_data.get('current_liabilities', 1)
quick_ratio = ((current_assets - inventories) / current_liabilities) * 100
asset_turnover = revenue / total_assets
inventory_days = (inventories / (cost_of_sales / 365)) if cost_of_sales > 0 else 0
liquidity_ratio = cash / (revenue / 12)
free_cash_flow = edinet_data.get('cf_operating', 0) + edinet_data.get('cf_investing', 0)
revenue_prev = edinet_data_prev.get('revenue', revenue) if edinet_data_prev else revenue
revenue_growth = ((revenue - revenue_prev) / revenue_prev) * 100 if revenue_prev != 0 else 0
cf_operating = edinet_data.get('cf_operating', 0)
cf_margin = (cf_operating / revenue) * 100 if revenue != 0 else 0
cash_profit_ratio = (cf_operating / operating_income) * 100 if operating_income != 0 else 0
total_expenses = revenue - operating_income
cost_per_employee_monthly = (total_expenses / 12) / num_employees
eps = edinet_data.get('eps', 0)
ev = market_cap + (all_debt - cash)
cash_equiv = edinet_data.get('cash', 0) 
all_debt = edinet_data.get('ibd_current', 0) + edinet_data.get('ibd_noncurrent', 0)
net_debt = all_debt - cash_equiv
de_ratio = (all_debt / total_equity) * 100 if total_equity != 0 else 0
ebitda = operating_income + depreciation
ebitda_debt_ratio = (all_debt / ebitda) if ebitda > 0 else 0


# --- 3. 出力 ---
print('\n----------------------------------------------------------')
cprint(f"{StdText('最終提出日', Color.BRIGHT_MAGENTA)}: {edinet_data.get('submit_date', '不明')}\n")

# 【収益性・成長性】
cprint(f"{StdText('ROE', Color.BRIGHT_YELLOW)}: {(net_income / total_equity) * 100:.2f}%")
cprint(f"{StdText('ROA', Color.BRIGHT_YELLOW)}: {(net_income / total_assets) * 100:.2f}%\n")
cprint(f"{StdText('売上高成長率(前年比)', Color.BRIGHT_MAGENTA)}: {revenue_growth:.2f}%")
cprint(f"{StdText('売上高総利益率(粗利率)', Color.BRIGHT_MAGENTA)}: {(gross_profit / revenue) * 100:.2f}%")
cprint(f"{StdText('売上高営業利益率', Color.BRIGHT_MAGENTA)}: {(operating_income / revenue) * 100:.2f}%")
cprint(f"{StdText('1人当たり月間売上高', Color.BRIGHT_MAGENTA)}: {(revenue / 12) / num_employees / 10000:.2f}万円")
cprint(f"{StdText('1人当たり月間総費用', Color.BRIGHT_MAGENTA)}: {cost_per_employee_monthly / 10000:.2f}万円")
cprint(f"{StdText('従業員効率（月間）', Color.BRIGHT_MAGENTA)}: {(operating_income / 12) / num_employees:.2f}円\n")

# 【効率性・従業員生産性】
cprint(f"{StdText('総資産回転率', Color.BRIGHT_CYAN)}: {asset_turnover:.2f}回")
cprint(f"{StdText('棚卸資産回転日数', Color.BRIGHT_CYAN)}: {inventory_days:.2f}日分")
cprint(f"{StdText('売上債権回転日数', Color.BRIGHT_CYAN)}: {edinet_data.get('trade_receivables', 0) / (revenue / 365):.2f}日分\n")

# 【安全性・キャッシュフロー】
cprint(f"{StdText('自己資本比率', Color.BRIGHT_YELLOW)}: {(total_equity / total_assets) * 100:.2f}%")
cprint(f"{StdText('手元流動性', Color.BRIGHT_YELLOW)}: {liquidity_ratio:.2f}ヶ月分")
cprint(f"{StdText('流動比率', Color.BRIGHT_YELLOW)}: {(current_assets / current_liabilities) * 100:.2f}%")
cprint(f"{StdText('当座比率', Color.BRIGHT_YELLOW)}: {quick_ratio:.2f}%\n")

cprint(f"{StdText('現金および現金同等物', Color.BRIGHT_MAGENTA)}: {cash_equiv / 100000000:.2f}億円")
cprint(f"{StdText('有利子負債', Color.BRIGHT_MAGENTA)}: {all_debt / 100000000:.2f}億円")
cprint(f"{StdText('純有利子負債', Color.BRIGHT_MAGENTA)}: {net_debt / 100000000:.2f}億円")
cprint(f"{StdText('有利子負債比率(DEレシオ)', Color.BRIGHT_MAGENTA)}: {de_ratio:.2f}%")
cprint(f"{StdText('有利子負債月商倍率', Color.BRIGHT_MAGENTA)}: {all_debt / (revenue / 12):.2f}ヶ月分")
cprint(f"{StdText('EBITDA有利子負債倍率', Color.BRIGHT_MAGENTA)}: {ebitda_debt_ratio:.2f}倍\n")

cprint(f"{StdText('CFマージン', Color.BRIGHT_CYAN)}: {cf_margin:.2f}%")
cprint(f"{StdText('キャッシュ利益比率', Color.BRIGHT_CYAN)}: {cash_profit_ratio:.2f}%")
cprint(f"{StdText('フリーCF', Color.BRIGHT_CYAN)}: {free_cash_flow / 100000000:.2f}億円")
cprint(f"{StdText('ネットキャッシュ', Color.BRIGHT_CYAN)}: {(cash - all_debt) / 100000000:.2f}億円\n")

# 【バリュエーション】
cprint(f"{StdText('現在の株価', Color.BG_BRIGHT_WHITE)}: {stock_price:.2f}円\n")
cprint(f"{StdText('EPS(1株益)', Color.BRIGHT_YELLOW)}: {eps:.2f}円")
cprint(f"{StdText('PER', Color.BRIGHT_YELLOW)}: {stock_price / edinet_data['eps']:.2f}倍")
cprint(f"{StdText('PBR', Color.BRIGHT_YELLOW)}: {stock_price / edinet_data['bps']:.2f}倍")
cprint(f"{StdText('BPS', Color.BRIGHT_YELLOW)}: {edinet_data['bps']:.2f}円\n")

cprint(f"{StdText('時価総額', Color.BRIGHT_MAGENTA)}: {market_cap / 100000000:.2f}億円")
cprint(f"{StdText('企業価値(EV)', Color.BRIGHT_MAGENTA)}: {ev / 100000000:.2f}億円")
cprint(f"{StdText('EV/EBITDA倍率', Color.BRIGHT_MAGENTA)}: {(market_cap + (all_debt - cash)) / (operating_income + depreciation):.2f}倍")

print('----------------------------------------------------------\n')

