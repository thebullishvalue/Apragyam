# Apragyam (अप्रज्ञम) — Inverted Portfolio Intelligence

**Version:** 7.3.0
**Author:** @thebullishvalue
**License:** Proprietary (See LICENSE file)

Contrarian inverse portfolio curation for Indian equity markets using 80+ quantitative strategies. Weakness is strength — weakest candidates receive the most weight.

**Latest:** v7.3.0 — Inverted conviction-based curation with Terminal Glass design system.

---

## Overview

Apragyam uses a **pure inverted conviction-based approach** to portfolio construction:

1. **All 80+ strategies run** — Every strategy generates candidate holdings
2. **Inverted conviction scoring** — Each symbol scored 0-100 using inverted 4 technical signals
3. **Weakest first selection** — Lowest conviction scores selected (contrarian approach)
4. **Inverted weighting** — `weight = (weakness_score / total) × 100`

**Execution time:** ~20-40 seconds

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Inverted Conviction** | 4 signals inverted: RSI (30%), Oscillator (30%), Z-Score (20%), MA Alignment (20%) |
| **All Strategies** | 80+ quantitative strategies contribute candidates |
| **Contrarian Formula** | `weight_i = (inverted_conviction_i / Σ all_inverted_convictions) × 100` |
| **Position Bounds** | 1% minimum, 10% maximum per position |
| **Regime Detection** | 7-factor market regime analysis (display only) |
| **Live Data** | Real-time NSE data via yfinance |

---

## Architecture

```
Apragyam v7.3.0 — 2 Phases (Inverted)

┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: DATA FETCHING                                      │
│ → Fetch historical data for all symbols (yfinance)          │
│ → Detect market regime (7-factor composite)                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: INVERTED CONVICTION-BASED CURATION                │
│ → Run ALL 80+ strategies                                    │
│ → Aggregate all candidate holdings (~200-400 symbols)      │
│ → Compute INVERTED conviction scores (regime.py)           │
│ → Select LOWEST conviction by strength                      │
│ → Apply formula: weight = (weakness / total) × 100          │
│ → Apply bounds (1%-10%)                                     │
│ → Calculate units and value                                 │
└─────────────────────────────────────────────────────────────┘
```

### Module Structure

```
Apragyam/
├── app.py                    # Main UI (Streamlit)
├── universe.py               # Universe definitions & selection
├── portfolio.py              # Inverted conviction-based weighting
├── regime.py                 # Market regime + inverted conviction scoring
├── strategies.py             # 95 BaseStrategy implementations
├── backdata.py               # Data fetching (yfinance)
├── charts.py                 # Plotly visualizations
├── circuit_breaker.py        # yfinance rate limiting
├── logger_config.py          # Console output system
├── metrics.py                # Execution metrics
├── ui/                       # UI layer
│   ├── components.py         # Reusable UI components
│   ├── theme.py             # Theme constants
│   └── theme.css            # Terminal Glass CSS
├── requirements.txt          # Dependencies
└── pyproject.toml            # Project configuration
```

---

## Installation

```bash
# Clone repository
git clone <repository-url>
cd Apragyam

# Install dependencies
pip install -r requirements.txt
```

### Requirements

- Python 3.10+
- streamlit>=1.28.0
- pandas>=2.0.0
- numpy>=1.24.0
- plotly>=5.18.0
- yfinance>=0.2.28
- scipy>=1.11.0
- colorama>=0.4.6

---

## Usage

### 1. Select Universe

Use the sidebar dropdown to choose your analysis universe:

**Available Universes:**
- **ETF Universe** — 30 NSE ETFs covering major indices and sectors
- **India Indexes** — NIFTY 50, NIFTY 100, NIFTY 500, F&O Stocks, sectoral indices
- **US Indexes** — S&P 500, DOW JONES, NASDAQ 100
- **Commodities** — 24 commodity futures
- **Currency** — 24 currency pairs

### 2. Run Application

```bash
streamlit run app.py
```

### 3. Use the Interface

1. **Select Analysis Date** — Choose the date for portfolio curation
2. **Set Investment Style** — Swing Trading or SIP Investment
3. **Configure Parameters:**
   - Capital (₹) — Total capital to deploy (default: ₹2,500,000)
   - Number of Positions — Holdings in final portfolio (default: 30, range: 5-100)
   - Min/Max Position Weight — Bounds for individual positions (1%-10% default)
4. **Click "Run Analysis"**

### 4. Review Results

- **Tab 1: Portfolio** — Holdings with inverted conviction signals and position guide
- **Tab 2: Performance** — Methodology explanation
- **Tab 3: Regime** — Market regime analysis (7-factor composite)
- **Tab 4: System** — Technical details and configuration

---

## Inverted Conviction Scoring Formula

### Signal Components (Inverted)

| Signal | Weight | Calculation |
|--------|--------|-------------|
| **RSI** | 30% | <40: +2, <48: +1, >52: -1, >60: -2 (inverted from original) |
| **Oscillator** | 30% | <EMA9 & <0: +2, <EMA9: +1, >EMA9 & >0: -2, else: -1 |
| **Z-Score** | 30% | >2: +2, >1: +1, <-2: -2, <-1: -1 (inverted) |
| **MA Alignment** | 20% | Count of 5 bearish conditions (0-5 scaled to -2 to +2, inverted) |

### Composite Score

```python
raw = (RSI_signal × 0.30 +
       OSC_signal × 0.30 +
       Z-Score_signal × 0.20 +
       MA_signal × 0.20)

# Normalize to 0-100 scale
inverted_conviction_score = (raw + 2) / 4 × 100
```

### Contrarian Dispersion Weighting (v7.3.0)

Style-aware dispersion weighting automatically adjusts based on investment style:

| Style | Boost (Below Median) | Penalty (Above Median) |
|-------|---------------------|------------------------|
| **SIP Investment** | +125% (×2.25) | -50% (×0.50) |
| **Swing Trading** | +225% (×3.25) | -75% (×0.25) |

**Effect:** 
- SIP: Strong concentration in weakest picks (~350% tilt)
- Swing: Very aggressive concentration in weakest picks (~1200% tilt)

---

## Example Output

```
Execution Summary
────────────────────────────────────────
Run ID:             20260416_175721
Strategies Run:     83
Candidate Symbols:  287
Positions Selected: 30
Avg Conviction:     37.7/100
Lowest Conviction:  22/100
Status:             SUCCESS
────────────────────────────────────────

Portfolio: 30 positions
Total Value: ₹2,487,350
Cash Remaining: ₹12,650
```

---

## Troubleshooting

### "No historical data loaded"
- Check your universe selection in the sidebar
- Verify internet connection
- Reduce lookback period in sidebar
- Ensure yfinance can access NSE data (may be rate-limited)

### "No holdings generated"
- Some strategies may not generate signals for current market conditions
- Try a different analysis date
- Increase number of positions in sidebar

### Slow execution or timeouts
- v7.3.0 executes in 20-40 seconds for small universes (<50 symbols)
- Larger universes may take 1-3 minutes
- Reduce universe size if needed

### Rate limiting from yfinance
- Circuit breaker implemented in `circuit_breaker.py`
- Add fewer symbols or use smaller universe to distribute requests

---

## License

Proprietary Software License — See LICENSE file for details.

Copyright (c) 2024-2026 @thebullishvalue. All Rights Reserved.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and notable changes.

---

## Version History

| Version | Date | Architecture | Key Feature |
|---------|------|--------------|-------------|
| 7.3.0 | 2026-04-16 | 2 phases | Inverted conviction-based curation |
| 7.2.0 | 2026-04-13 | 2 phases | Terminal Glass design system |
| 7.1.0 | 2026-04-13 | 2 phases | UI/UX enhancements |
| 7.0.5 | 2026-04-05 | 2 phases | Production hardening |

---

## Disclaimer

This software is for educational and research purposes only. Not financial advice. Past performance does not guarantee future results. Always conduct your own research before making investment decisions.

---

## Contact

**@thebullishvalue** — Portfolio Intelligence Systems
