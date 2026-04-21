"""
APRAGYAM Universe Selection Module
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Dynamic universe definitions and fetching functions for portfolio analysis.

Supports:
- ETF Universe (fixed list of 30 NSE ETFs)
- India Indices (NIFTY 50, NIFTY 500, F&O Stocks, sectoral indices)
- US Indices (S&P 500, DOW JONES, NASDAQ 100)
- Commodities (24 futures)
- Currency (24 pairs)
- Crypto (21 digital assets)

Adapted from Nirnay system.
"""

import streamlit as st
import pandas as pd
import requests
import io
import urllib.parse
from typing import List, Tuple, Optional

# ══════════════════════════════════════════════════════════════════════════════
# UNIVERSE DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════════

# ── ETF Universe (Fixed) ─────────────────────────────────────────────────────
ETF_UNIVERSE = [
    "SENSEXIETF.NS", "NIFTYIETF.NS", "MON100.NS", "MAKEINDIA.NS", "SILVERIETF.NS",
    "HEALTHIETF.NS", "CONSUMIETF.NS", "GOLDIETF.NS", "INFRAIETF.NS", "CPSEETF.NS",
    "TNIDETF.NS", "COMMOIETF.NS", "MODEFENCE.NS", "MOREALTY.NS", "PSUBNKIETF.NS",
    "MASPTOP50.NS", "FMCGIETF.NS", "BANKIETF.NS", "ITIETF.NS", "EVINDIA.NS",
    "MNC.NS", "FINIETF.NS", "AUTOIETF.NS", "PVTBANIETF.NS", "MONIFTY500.NS",
    "ECAPINSURE.NS", "MIDCAPIETF.NS", "MOSMALL250.NS", "OILIETF.NS", "METALIETF.NS"
]

# ── India Index Universe ─────────────────────────────────────────────────────
INDIA_INDEX_LIST = [
    "NIFTY 50",
    "F&O Stocks",
    "NIFTY NEXT 50",
    "NIFTY 100",
    "NIFTY 200",
    "NIFTY 500",
    # Midcap
    "NIFTY MIDCAP 50",
    "NIFTY MIDCAP 100",
    "NIFTY MIDCAP 150",
    "NIFTY MID SELECT",
    # Smallcap
    "NIFTY SMLCAP 50",
    "NIFTY SMLCAP 100",
    "NIFTY SMLCAP 250",
    # Sectoral
    "NIFTY BANK",
    "NIFTY PRIVATE BANK",
    "NIFTY PSU BANK",
    "NIFTY AUTO",
    "NIFTY FIN SERVICE",
    "NIFTY FMCG",
    "NIFTY IT",
    "NIFTY MEDIA",
    "NIFTY METAL",
    "NIFTY ENERGY",
    "NIFTY INFRA",
    "NIFTY REALTY",
    "NIFTY PHARMA",
]

# ── US Index Universe ────────────────────────────────────────────────────────
US_INDEX_LIST = ["S&P 500", "DOW JONES", "NASDAQ 100"]

# ── Universe Options for Dropdown ────────────────────────────────────────────
UNIVERSE_OPTIONS = [
    "ETF Universe",
    "India Indexes",
    "US Indexes",
    "Commodities",
    "Currency",
    "Crypto",
]

# ── Index URL Map for fetching constituents ──────────────────────────────────
BASE_URL = "https://archives.nseindia.com/content/indices/"
INDEX_URL_MAP = {
    "NIFTY 50": f"{BASE_URL}ind_nifty50list.csv",
    "NIFTY NEXT 50": f"{BASE_URL}ind_niftynext50list.csv",
    "NIFTY 100": f"{BASE_URL}ind_nifty100list.csv",
    "NIFTY 200": f"{BASE_URL}ind_nifty200list.csv",
    "NIFTY 500": f"{BASE_URL}ind_nifty500list.csv",
    "NIFTY MIDCAP 50": f"{BASE_URL}ind_niftymidcap50list.csv",
    "NIFTY MIDCAP 100": f"{BASE_URL}ind_niftymidcap100list.csv",
    "NIFTY MIDCAP 150": f"{BASE_URL}ind_niftymidcap150list.csv",
    "NIFTY MID SELECT": f"{BASE_URL}ind_niftymidcapselectlist.csv",
    "NIFTY SMLCAP 50": f"{BASE_URL}ind_niftysmallcap50list.csv",
    "NIFTY SMLCAP 100": f"{BASE_URL}ind_niftysmallcap100list.csv",
    "NIFTY SMLCAP 250": f"{BASE_URL}ind_niftysmallcap250list.csv",
    "NIFTY BANK": f"{BASE_URL}ind_niftybanklist.csv",
    "NIFTY PRIVATE BANK": f"{BASE_URL}ind_niftypvtbanklist.csv",
    "NIFTY PSU BANK": f"{BASE_URL}ind_niftypsubanklist.csv",
    "NIFTY AUTO": f"{BASE_URL}ind_niftyautolist.csv",
    "NIFTY FIN SERVICE": f"{BASE_URL}ind_niftyfinancelist.csv",
    "NIFTY FMCG": f"{BASE_URL}ind_niftyfmcglist.csv",
    "NIFTY IT": f"{BASE_URL}ind_niftyitlist.csv",
    "NIFTY MEDIA": f"{BASE_URL}ind_niftymedialist.csv",
    "NIFTY METAL": f"{BASE_URL}ind_niftymetallist.csv",
    "NIFTY ENERGY": f"{BASE_URL}ind_niftyenergylist.csv",
    "NIFTY INFRA": f"{BASE_URL}ind_niftyinfrastructurelist.csv",
    "NIFTY REALTY": f"{BASE_URL}ind_niftyrealtylist.csv",
    "NIFTY PHARMA": f"{BASE_URL}ind_niftypharmalist.csv",
}

# ── Commodity Futures (Yahoo Finance) ─────────────────────────────────────────
COMMODITY_TICKERS = {
    "GC=F": "Gold",
    "SI=F": "Silver",
    "PL=F": "Platinum",
    "PA=F": "Palladium",
    "HG=F": "Copper",
    "CL=F": "Crude Oil WTI",
    "BZ=F": "Brent Crude",
    "NG=F": "Natural Gas",
    "RB=F": "Gasoline RBOB",
    "HO=F": "Heating Oil",
    "ZC=F": "Corn",
    "ZW=F": "Wheat",
    "ZS=F": "Soybeans",
    "ZM=F": "Soybean Meal",
    "ZL=F": "Soybean Oil",
    "CT=F": "Cotton",
    "KC=F": "Coffee",
    "SB=F": "Sugar",
    "CC=F": "Cocoa",
    "OJ=F": "Orange Juice",
    "LBS=F": "Lumber",
    "LE=F": "Live Cattle",
    "HE=F": "Lean Hogs",
    "GF=F": "Feeder Cattle",
}

# ── Currency Pairs (Yahoo Finance) ────────────────────────────────────────────
CURRENCY_TICKERS = {
    "EURUSD=X": "EUR/USD",
    "GBPUSD=X": "GBP/USD",
    "USDJPY=X": "USD/JPY",
    "USDCHF=X": "USD/CHF",
    "AUDUSD=X": "AUD/USD",
    "USDCAD=X": "USD/CAD",
    "NZDUSD=X": "NZD/USD",
    "USDINR=X": "USD/INR",
    "EURGBP=X": "EUR/GBP",
    "EURJPY=X": "EUR/JPY",
    "GBPJPY=X": "GBP/JPY",
    "AUDJPY=X": "AUD/JPY",
    "EURCHF=X": "EUR/CHF",
    "EURAUD=X": "EUR/AUD",
    "GBPCHF=X": "GBP/CHF",
    "GBPAUD=X": "GBP/AUD",
    "USDSGD=X": "USD/SGD",
    "USDHKD=X": "USD/HKD",
    "USDCNH=X": "USD/CNH",
    "USDZAR=X": "USD/ZAR",
    "USDMXN=X": "USD/MXN",
    "USDTRY=X": "USD/TRY",
    "USDBRL=X": "USD/BRL",
    "USDKRW=X": "USD/KRW",
}

# ── Crypto Assets (Yahoo Finance) ────────────────────────────────────────────
CRYPTO_TICKERS = {
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "SOL-USD": "Solana",
    "BNB-USD": "Binance Coin",
    "XRP-USD": "Ripple (XRP)",
    "ADA-USD": "Cardano",
    "DOGE-USD": "Dogecoin",
    "TRX-USD": "Tron",
    "LINK-USD": "Chainlink",
    "DOT-USD": "Polkadot",
    "POL-USD": "Polygon (POL)",
    "LTC-USD": "Litecoin",
    "BCH-USD": "Bitcoin Cash",
    "SHIB-USD": "Shiba Inu",
    "AVAX-USD": "Avalanche",
    "NEAR-USD": "Near Protocol",
    "UNI-USD": "Uniswap",
    "XLM-USD": "Stellar",
    "ETC-USD": "Ethereum Classic",
    "XMR-USD": "Monero",
    "ATOM-USD": "Cosmos",
}

# ── Hardcoded Dow Jones 30 components ─────────────────────────────────────────
DOW_JONES_TICKERS = [
    "AMZN", "AMGN", "AAPL", "BA", "CAT", "CSCO", "CVX", "GS", "HD", "HON",
    "IBM", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT", "NKE", "PG",
    "CRM", "SHW", "TRV", "UNH", "V", "VZ", "WMT", "DIS", "DOW", "NVDA"
]

# ── Wikipedia URLs for India Index fallback ───────────────────────────────────
INDIA_INDEX_WIKI_MAP = {
    "NIFTY 50": "https://en.wikipedia.org/wiki/NIFTY_50",
    "NIFTY NEXT 50": "https://en.wikipedia.org/wiki/NIFTY_Next_50",
    "NIFTY 100": "https://en.wikipedia.org/wiki/NIFTY_100",
    "NIFTY 200": "https://en.wikipedia.org/wiki/NIFTY_200",
    "NIFTY 500": "https://en.wikipedia.org/wiki/NIFTY_500",
    "NIFTY MIDCAP 50": "https://en.wikipedia.org/wiki/NIFTY_Midcap_50",
    "NIFTY BANK": "https://en.wikipedia.org/wiki/NIFTY_Bank",
}


# ══════════════════════════════════════════════════════════════════════════════
# NSE SESSION HELPER
# ══════════════════════════════════════════════════════════════════════════════

# Headers that match a real Chrome browser — NSE bot-detection checks these.
# No Accept-Encoding: NSE sometimes returns garbled compressed content when
# requests handles decompression automatically with this header set.
_NSE_API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/market-data/live-equity-market",
}


def _create_nse_session() -> requests.Session:
    """
    Create a requests.Session with NSE cookies.

    NSE blocks direct API calls without a prior homepage visit that sets
    session cookies (nseappid, nsit, bm_sv etc.).  This helper visits the
    NSE homepage first, then returns a session ready for API calls.

    Headers are passed per-request (not at session level) so the homepage
    visit and API call share the same header fingerprint — matching what a
    real browser does.
    """
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=_NSE_API_HEADERS, timeout=10)
    return session


# ══════════════════════════════════════════════════════════════════════════════
# UNIVERSE FETCHING FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_etf_universe() -> Tuple[List[str], str]:
    """Return the fixed ETF universe for analysis"""
    return ETF_UNIVERSE, f"✓ Loaded {len(ETF_UNIVERSE)} ETFs"


# ── F&O Stocks ───────────────────────────────────────────────────────────────

# Hardcoded fallback: NSE F&O stock list as of April 2025.
# Used when live NSE API is unreachable.
FNO_FALLBACK_SYMBOLS = [
    "AARTIIND", "ABB", "ABBOTINDIA", "ABCAPITAL", "ABFRL", "ACC", "ADANIENT",
    "ADANIPORTS", "ALKEM", "AMBUJACEM", "APOLLOHOSP", "APOLLOTYRE", "ASHOKLEY",
    "ASIANPAINT", "ASTRAL", "ATUL", "AUBANK", "AUROPHARMA", "AXISBANK",
    "BAJAJ-AUTO", "BAJAJFINSV", "BAJFINANCE", "BALKRISIND", "BALRAMCHIN",
    "BANDHANBNK", "BANKBARODA", "BATAINDIA", "BEL", "BERGEPAINT", "BHARATFORG",
    "BHARTIARTL", "BHEL", "BIOCON", "BOSCHLTD", "BPCL", "BRITANNIA", "BSOFT",
    "CANBK", "CANFINHOME", "CHAMBLFERT", "CHOLAFIN", "CIPLA", "COALINDIA",
    "COFORGE", "COLPAL", "CONCOR", "COROMANDEL", "CROMPTON", "CUB",
    "CUMMINSIND", "DABUR", "DALBHARAT", "DEEPAKNTR", "DELTACORP", "DIVISLAB",
    "DIXON", "DLF", "DRREDDY", "EICHERMOT", "ESCORTS", "EXIDEIND",
    "FEDERALBNK", "GAIL", "GLENMARK", "GMRINFRA", "GNFC", "GODREJCP",
    "GODREJPROP", "GRANULES", "GRASIM", "GUJGASLTD", "HAL", "HAVELLS",
    "HCLTECH", "HDFC", "HDFCAMC", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO",
    "HINDALCO", "HINDCOPPER", "HINDPETRO", "HINDUNILVR", "IBULHSGFIN",
    "ICICIBANK", "ICICIGI", "ICICIPRULI", "IDEA", "IDFC", "IDFCFIRSTB",
    "IEX", "IGL", "INDHOTEL", "INDIACEM", "INDIAMART", "INDIGO",
    "INDUSINDBK", "INDUSTOWER", "INFY", "IOC", "IPCALAB", "IRCTC",
    "ITC", "JINDALSTEL", "JKCEMENT", "JSWSTEEL", "JUBLFOOD", "KOTAKBANK",
    "L&TFH", "LALPATHLAB", "LAURUSLABS", "LICHSGFIN", "LT", "LTIM",
    "LTTS", "LUPIN", "M&M", "M&MFIN", "MANAPPURAM", "MARICO",
    "MARUTI", "MCDOWELL-N", "MCX", "METROPOLIS", "MFSL", "MGL",
    "MOTHERSON", "MPHASIS", "MRF", "MUTHOOTFIN", "NATIONALUM", "NAUKRI",
    "NAVINFLUOR", "NESTLEIND", "NMDC", "NTPC", "OBEROIRLTY", "OFSS",
    "ONGC", "PAGEIND", "PEL", "PERSISTENT", "PETRONET", "PFC",
    "PIDILITIND", "PIIND", "PNB", "POLYCAB", "POWERGRID", "PVRINOX",
    "RAMCOCEM", "RBLBANK", "RECLTD", "RELIANCE", "SAIL", "SBICARD",
    "SBILIFE", "SBIN", "SHREECEM", "SHRIRAMFIN", "SIEMENS", "SRF",
    "SUNPHARMA", "SUNTV", "SYNGENE", "TATACHEM", "TATACOMM", "TATACONSUM",
    "TATAMOTORS", "TATAPOWER", "TATASTEEL", "TCS", "TECHM", "TITAN",
    "TORNTPHARM", "TORNTPOWER", "TRENT", "TVSMOTOR", "UBL", "ULTRACEMCO",
    "UPL", "VEDL", "VOLTAS", "WIPRO", "ZEEL", "ZYDUSLIFE",
]


@st.cache_data(ttl=3600, show_spinner=False)
def get_fno_stock_list() -> Tuple[Optional[List[str]], str]:
    """
    Fetch F&O stock list from NSE.

    Strategy:
      1. Create an NSE session (homepage visit for cookies)
      2. Hit the correct endpoint: equity-stockIndices?index=SECURITIES IN F&O
      3. Fall back to hardcoded list if API fails
    """
    # ── Attempt 1: NSE live API ──
    try:
        session = _create_nse_session()
        url = "https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O"
        response = session.get(url, headers=_NSE_API_HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()

        if "data" in data:
            # First entry is always the index summary row, skip it
            symbols = [
                item["symbol"]
                for item in data["data"][1:]
                if item.get("symbol") and str(item["symbol"]).strip()
            ]
            if symbols:
                symbols_ns = [f"{s}.NS" for s in symbols]
                return symbols_ns, f"✓ Fetched {len(symbols_ns)} F&O securities from NSE (live)"
    except Exception:
        pass

    # ── Attempt 2: NSE lot-size CSV (columns have trailing whitespace) ──
    try:
        session = _create_nse_session()
        csv_url = "https://nsearchives.nseindia.com/content/fo/fo_mktlots.csv"
        response = session.get(csv_url, headers=_NSE_API_HEADERS, timeout=15)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        # Strip whitespace from column names — NSE CSV has padded headers
        df.columns = [c.strip() for c in df.columns]
        if "SYMBOL" in df.columns:
            # Known index symbols to exclude (not tradable stocks)
            index_symbols = {
                "NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY",
                "NIFTYNXT50", "SENSEX", "BANKEX",
            }
            symbols = (
                df["SYMBOL"]
                .dropna()
                .astype(str)
                .str.strip()
                .loc[lambda s: (s != "") & (s != "nan")]
                .unique()
                .tolist()
            )
            # Filter out index symbols and header artifacts, keep only stock symbols
            symbols = [s for s in symbols if s not in index_symbols and s.upper() != "SYMBOL"]
            if len(symbols) >= 50:
                symbols_ns = [f"{s}.NS" for s in symbols]
                return symbols_ns, f"✓ Fetched {len(symbols_ns)} F&O securities from NSE lot-size CSV"
    except Exception:
        pass

    # ── Fallback: hardcoded list ──
    symbols_ns = [f"{s}.NS" for s in FNO_FALLBACK_SYMBOLS]
    return symbols_ns, f"⚠ NSE API unavailable → Loaded {len(symbols_ns)} F&O stocks from built-in fallback (Apr 2025)"


# ── Wikipedia helpers ────────────────────────────────────────────────────────

def _parse_wiki_table(url: str, min_count: int = 10) -> Optional[List[str]]:
    """Parse a Wikipedia page and extract NSE symbols from the constituent table."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        tables = pd.read_html(io.StringIO(response.text))
        for tbl in tables:
            # Try common column names: Symbol, Ticker, NSE Symbol
            for col_name in ("Symbol", "Ticker", "NSE Symbol", "NSE symbol"):
                if col_name in tbl.columns:
                    symbols = tbl[col_name].dropna().astype(str).str.strip().tolist()
                    symbols = [s for s in symbols if s and len(s) <= 20 and s != 'nan']
                    if len(symbols) >= min_count:
                        return symbols
        return None
    except Exception:
        return None


def _fetch_india_index_from_wikipedia(index: str) -> Tuple[Optional[List[str]], Optional[str]]:
    """Fallback: Fetch Indian index constituents from Wikipedia when niftyindices.com is unreachable."""
    try:
        wiki_url = INDIA_INDEX_WIKI_MAP.get(index)
        if not wiki_url:
            return None, None

        min_expected = {
            "NIFTY 50": 40,
            "NIFTY NEXT 50": 40,
            "NIFTY 100": 80,
            "NIFTY 200": 150,
            "NIFTY 500": 400,
            "NIFTY MIDCAP 50": 40,
            "NIFTY BANK": 8,
        }.get(index, 10)

        symbols = _parse_wiki_table(wiki_url, min_count=min_expected)
        if symbols:
            symbols_ns = [s + ".NS" for s in symbols]
            return symbols_ns, (
                f"⚠ NSE archives unavailable → Loaded {len(symbols_ns)} "
                f"{index} constituents from Wikipedia"
            )
        return None, f"Wikipedia fallback: could not parse {index} table"

    except Exception as e:
        return None, f"Wikipedia fallback error: {e}"


# ── India index fetching (primary: NSE API, fallback 1: archives.nseindia.com CSV,
#    fallback 2: Wikipedia) ───────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def get_index_stock_list(index: str) -> Tuple[Optional[List[str]], str]:
    """
    Fetch index constituents with a 3-tier strategy:

      1. NSE API (equity-stockIndices) — most up-to-date, needs session cookies
      2. archives.nseindia.com CSV download — official NSE archive
      3. Wikipedia scrape — always available, may lag by a few weeks

    For US indices, delegates to get_us_index_stock_list().
    For F&O Stocks, delegates to get_fno_stock_list().
    """
    # Route special cases
    if index in US_INDEX_LIST:
        return get_us_index_stock_list(index)
    if index == "F&O Stocks":
        return get_fno_stock_list()

    # ── Attempt 1: NSE live API ──
    nse_api_error = None
    nse_index_key = _nse_api_index_key(index)
    if nse_index_key:
        try:
            session = _create_nse_session()
            url = f"https://www.nseindia.com/api/equity-stockIndices?index={nse_index_key}"
            response = session.get(url, headers=_NSE_API_HEADERS, timeout=15)
            response.raise_for_status()
            data = response.json()
            if "data" in data:
                # First entry is always the index summary row, skip it
                symbols = [
                    item["symbol"]
                    for item in data["data"][1:]
                    if item.get("symbol") and str(item["symbol"]).strip()
                ]
                if symbols:
                    symbols_ns = [f"{s}.NS" for s in symbols]
                    return symbols_ns, f"✓ Fetched {len(symbols_ns)} constituents for {index} from NSE (live)"
            nse_api_error = "No symbols in API response"
        except Exception as e:
            nse_api_error = str(e)

    # ── Attempt 2: NSE archives CSV ──
    csv_error = None
    csv_url = INDEX_URL_MAP.get(index)
    if csv_url:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0',
            }
            session = requests.Session()
            session.get("https://archives.nseindia.com", headers=headers, verify=False, timeout=10)
            response = session.get(csv_url, headers=headers, verify=False, timeout=15)
            response.raise_for_status()
            stock_df = pd.read_csv(io.StringIO(response.text))

            symbol_col = next((c for c in stock_df.columns if c.lower() == 'symbol'), None)
            if symbol_col:
                symbols = stock_df[symbol_col].tolist()
                symbols_ns = [str(s) + ".NS" for s in symbols if s and str(s).strip()]
                if symbols_ns:
                    return symbols_ns, f"✓ Fetched {len(symbols_ns)} constituents for {index} from NSE archives"
            csv_error = "No Symbol column found in CSV"
        except Exception as e:
            csv_error = str(e)

    # ── Attempt 3: Wikipedia fallback ──
    wiki_result, wiki_msg = _fetch_india_index_from_wikipedia(index)
    if wiki_result:
        return wiki_result, wiki_msg

    # All three tiers failed
    errors = []
    if nse_api_error:
        errors.append(f"NSE API: {nse_api_error}")
    if csv_error:
        errors.append(f"CSV: {csv_error}")
    if wiki_msg:
        errors.append(wiki_msg)
    elif index not in INDIA_INDEX_WIKI_MAP:
        errors.append("No Wikipedia fallback available for this index")

    return None, f"All sources failed for {index} — " + " | ".join(errors)


def _nse_api_index_key(index: str) -> Optional[str]:
    """
    Map a human-readable index name to the NSE API query-string key.

    Most names can be URL-encoded directly. A small set have display names
    that differ from the API key (e.g. "NIFTY FIN SERVICE" → "NIFTY FINANCIAL SERVICES").
    """
    # Special cases where display name differs from API key
    special = {
        "NIFTY FIN SERVICE": "NIFTY FINANCIAL SERVICES",
        "NIFTY SMLCAP 50": "NIFTY SMALLCAP 50",
        "NIFTY SMLCAP 100": "NIFTY SMALLCAP 100",
        "NIFTY SMLCAP 250": "NIFTY SMALLCAP 250",
        "NIFTY MID SELECT": "NIFTY MIDCAP SELECT",
        "NIFTY PRIVATE BANK": "NIFTY PRIVATE BANK",
        "NIFTY PSU BANK": "NIFTY PSU BANK",
        "NIFTY INFRA": "NIFTY INFRASTRUCTURE",
    }
    api_name = special.get(index, index)
    return urllib.parse.quote(api_name)


# ── US index fetching ────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def get_us_index_stock_list(index: str) -> Tuple[Optional[List[str]], str]:
    """Fetch US index constituents from Wikipedia with hardcoded fallback for Dow Jones."""
    _headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    if index == "DOW JONES":
        return DOW_JONES_TICKERS, f"✓ Loaded {len(DOW_JONES_TICKERS)} Dow Jones components"

    if index == "S&P 500":
        try:
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            response = requests.get(url, headers=_headers, timeout=15)
            response.raise_for_status()
            tables = pd.read_html(io.StringIO(response.text))
            for tbl in tables:
                cols_lower = {str(c).lower(): c for c in tbl.columns}
                for candidate in ("symbol", "ticker", "stock symbol"):
                    if candidate in cols_lower:
                        col = cols_lower[candidate]
                        # Keep dots/hyphens intact — yfinance accepts BRK.B directly
                        symbols = tbl[col].dropna().astype(str).str.strip().tolist()
                        symbols = [
                            s for s in symbols
                            if s and 1 <= len(s) <= 6
                            and s not in ('nan', 'None', 'Symbol', 'Ticker')
                            and not s[0].isdigit()
                        ]
                        if len(symbols) >= 400:
                            return symbols, f"✓ Fetched {len(symbols)} S&P 500 constituents from Wikipedia"
            return None, "Could not parse S&P 500 table from Wikipedia"
        except Exception as e:
            return None, f"S&P 500 Wikipedia fetch failed: {e}"

    if index == "NASDAQ 100":
        try:
            url = "https://en.wikipedia.org/wiki/Nasdaq-100"
            response = requests.get(url, headers=_headers, timeout=15)
            response.raise_for_status()
            tables = pd.read_html(io.StringIO(response.text))
            for tbl in tables:
                cols_lower = {str(c).lower(): c for c in tbl.columns}
                for candidate in ("ticker", "symbol"):
                    if candidate in cols_lower:
                        col = cols_lower[candidate]
                        symbols = tbl[col].dropna().astype(str).str.strip().tolist()
                        symbols = [
                            s for s in symbols
                            if s and 1 <= len(s) <= 6
                            and s not in ('nan', 'None', 'Symbol', 'Ticker')
                            and not s[0].isdigit()
                        ]
                        if len(symbols) >= 80:
                            return symbols, f"✓ Fetched {len(symbols)} NASDAQ 100 constituents from Wikipedia"
            return None, "Could not parse NASDAQ 100 table from Wikipedia"
        except Exception as e:
            return None, f"NASDAQ 100 Wikipedia fetch failed: {e}"

    return None, f"Unknown US index: {index}"


def get_commodity_list() -> Tuple[List[str], str]:
    """Return all commodity futures tickers for analysis"""
    tickers = list(COMMODITY_TICKERS.keys())
    return tickers, f"✓ Loaded {len(tickers)} commodity futures"


def get_currency_list() -> Tuple[List[str], str]:
    """Return all currency pair tickers for analysis"""
    tickers = list(CURRENCY_TICKERS.keys())
    return tickers, f"✓ Loaded {len(tickers)} currency pairs"


def get_crypto_list() -> Tuple[List[str], str]:
    """Return all crypto asset tickers for analysis"""
    tickers = list(CRYPTO_TICKERS.keys())
    return tickers, f"✓ Loaded {len(tickers)} crypto assets"


# ══════════════════════════════════════════════════════════════════════════════
# MAIN RESOLVE FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def resolve_universe(
    universe: str,
    index: Optional[str] = None
) -> Tuple[List[str], str]:
    """
    Resolve a universe selection to a list of symbols.

    Args:
        universe: One of UNIVERSE_OPTIONS ("ETF Universe", "India Indexes", etc.)
        index: Sub-selection (e.g., "NIFTY 50", "S&P 500") — required for India/US Indexes

    Returns:
        Tuple of (symbol_list, status_message)

    Raises:
        ValueError: If universe is unknown or index is missing when required
    """
    if universe == "ETF Universe":
        return get_etf_universe()

    elif universe == "India Indexes":
        if not index:
            raise ValueError("Index selection is required for India Indexes universe")
        return get_index_stock_list(index)

    elif universe == "US Indexes":
        if not index:
            raise ValueError("Index selection is required for US Indexes universe")
        return get_us_index_stock_list(index)

    elif universe == "Commodities":
        return get_commodity_list()

    elif universe == "Currency":
        return get_currency_list()

    elif universe == "Crypto":
        return get_crypto_list()

    else:
        raise ValueError(f"Unknown universe: {universe}. Choose from: {UNIVERSE_OPTIONS}")


def get_index_options(universe: str) -> List[str]:
    """Return the list of index options for a given universe"""
    if universe == "India Indexes":
        return INDIA_INDEX_LIST
    elif universe == "US Indexes":
        return US_INDEX_LIST
    return []


def get_default_index(universe: str) -> Optional[str]:
    """Return the default index for a given universe"""
    if universe == "India Indexes":
        return "NIFTY 50"
    elif universe == "US Indexes":
        return "S&P 500"
    return None


# ══════════════════════════════════════════════════════════════════════════════
# UI RENDERER
# ══════════════════════════════════════════════════════════════════════════════

def render_universe_selector() -> Tuple[str, Optional[str]]:
    """
    Render the universe selection UI inputs in the sidebar (title rendered externally).

    Returns:
        Tuple of (universe, selected_index) where selected_index may be None
    """
    universe = st.selectbox(
        "Analysis Universe",
        UNIVERSE_OPTIONS,
        help="Choose the universe of securities to analyze"
    )

    selected_index = None

    # Show index dropdown only for India/US Indexes
    if universe in ("India Indexes", "US Indexes"):
        index_options = get_index_options(universe)
        default_index = get_default_index(universe)
        default_idx = index_options.index(default_index) if default_index in index_options else 0

        label = "Select Index" if universe == "India Indexes" else "Select US Index"
        help_text = "Select the index for constituent analysis"

        selected_index = st.selectbox(
            label,
            index_options,
            index=default_idx,
            help=help_text
        )

    return universe, selected_index


# ══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Universe definitions
    'ETF_UNIVERSE',
    'INDIA_INDEX_LIST',
    'US_INDEX_LIST',
    'UNIVERSE_OPTIONS',
    'COMMODITY_TICKERS',
    'CURRENCY_TICKERS',
    'CRYPTO_TICKERS',
    'DOW_JONES_TICKERS',
    'FNO_FALLBACK_SYMBOLS',
    'INDEX_URL_MAP',
    # Fetching functions
    'get_etf_universe',
    'get_fno_stock_list',
    'get_index_stock_list',
    'get_us_index_stock_list',
    'get_commodity_list',
    'get_currency_list',
    'get_crypto_list',
    # Resolver
    'resolve_universe',
    'get_index_options',
    'get_default_index',
    # UI
    'render_universe_selector',
]
