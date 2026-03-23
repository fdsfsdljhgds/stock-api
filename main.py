from flask import Flask, jsonify
import yfinance as yf
import requests

app = Flask(__name__)

FRED_KEY = "your_fred_key_here"

@app.route('/stock/<ticker>')
def get_stock(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period="3mo")
    return jsonify({
        "name": info.get("longName"),
        "price": info.get("currentPrice"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "52w_high": info.get("fiftyTwoWeekHigh"),
        "52w_low": info.get("fiftyTwoWeekLow"),
        "debt_to_equity": info.get("debtToEquity"),
        "revenue_growth": info.get("revenueGrowth"),
        "profit_margins": info.get("profitMargins"),
        "beta": info.get("beta"),
        "analyst_target": info.get("targetMeanPrice"),
        "recommendation": info.get("recommendationKey"),
        "short_ratio": info.get("shortRatio"),
        "20d_avg": round(hist['Close'].tail(20).mean(), 2) if len(hist) >= 20 else None,
        "50d_avg": round(hist['Close'].tail(50).mean(), 2) if len(hist) >= 50 else None,
    })

@app.route('/market')
def get_market():
    tickers = {
        "sp500": "^GSPC",
        "nasdaq": "^IXIC",
        "dow": "^DJI",
        "vix": "^VIX",
        "crude_oil": "CL=F",
        "brent_oil": "BZ=F",
        "natural_gas": "NG=F",
        "gold": "GC=F",
        "silver": "SI=F",
        "bitcoin": "BTC-USD",
        "ethereum": "ETH-USD",
        "us_10y_yield": "^TNX",
        "dollar_index": "DX-Y.NYB",
    }
    result = {}
    for name, symbol in tickers.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="2d")
            if len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change_pct = ((current - prev) / prev) * 100
                result[name] = {
                    "price": round(current, 2),
                    "change_pct": round(change_pct, 2)
                }
        except:
            result[name] = None
    return jsonify(result)

@app.route('/commodity/<symbol>')
def get_commodity(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1mo")
    return jsonify({
        "price": round(hist['Close'].iloc[-1], 2),
        "20d_avg": round(hist['Close'].tail(20).mean(), 2),
        "change_1mo": round(((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100, 2)
    })

@app.route('/macro')
def get_macro():
    def fred(series):
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series}&api_key={FRED_KEY}&sort_order=desc&limit=1&file_type=json"
        r = requests.get(url)
        return r.json()['observations'][0]['value']
    return jsonify({
        "gdp_growth": fred("A191RL1Q225SBEA"),
        "inflation_cpi": fred("CPIAUCSL"),
        "unemployment": fred("UNRATE"),
        "fed_funds_rate": fred("FEDFUNDS"),
        "us_debt": fred("GFDEBTN"),
    })

if __name__ == '__main__':
    app.run()
