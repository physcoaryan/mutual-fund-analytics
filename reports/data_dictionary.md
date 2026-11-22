# Mutual Fund Analytics — Data Dictionary

**Database:** `bluestock_mf.db` (SQLite)  
**Schema file:** `sql/schema.sql`  
**Source files:** Cleaned CSVs in `data/processed/` (derived from `data/raw/`)

---

## 1. `dim_fund`
- **Source:** `data/processed/01_fund_master.csv` (40 rows)
- **Grain:** One row per mutual fund scheme (`amfi_code`)

| Column | Type | Constraints | Business Definition |
|---|---|---|---|
| `amfi_code` | INTEGER | PRIMARY KEY | Unique AMFI scheme identifier. |
| `fund_house` | TEXT | NOT NULL | Asset Management Company (AMC) managing the scheme. |
| `scheme_name` | TEXT | NOT NULL | Official name of the mutual fund scheme. |
| `category` | TEXT | NOT NULL | Broad asset class (e.g., Equity, Debt). |
| `sub_category` | TEXT | NOT NULL | SEBI sub-category (e.g., Large Cap, ELSS, Liquid). |
| `plan` | TEXT | NOT NULL | Plan type (e.g., Direct, Regular). |
| `launch_date` | TEXT | NOT NULL | Scheme inception date (`YYYY-MM-DD`). |
| `benchmark` | TEXT | NOT NULL | Market index used to benchmark scheme performance. |
| `expense_ratio_pct` | REAL | NOT NULL | Annual Total Expense Ratio (TER) as a percentage of AUM. |
| `exit_load_pct` | REAL | NOT NULL | Fee charged (%) if units are redeemed before the exit-load period. |
| `min_sip_amount` | INTEGER | NOT NULL | Minimum Systematic Investment Plan (SIP) installment in INR. |
| `min_lumpsum_amount` | INTEGER | NOT NULL | Minimum one-time lumpsum investment in INR. |
| `fund_manager` | TEXT | NOT NULL | Name of the primary fund manager. |
| `risk_category` | TEXT | NOT NULL | Riskometer classification (Low to Very High). |
| `sebi_category_code` | TEXT | NOT NULL | Standardized SEBI category code. |

---

## 2. `dim_date`
- **Source:** Generated in `load_sqlite.py` from all fact table date columns (1,608 rows)
- **Grain:** One row per calendar date (`date_key`)

| Column | Type | Constraints | Business Definition |
|---|---|---|---|
| `date_key` | TEXT | PRIMARY KEY | Calendar date in `YYYY-MM-DD` format. |
| `year` | INTEGER | NOT NULL | Four-digit calendar year. |
| `quarter` | INTEGER | NOT NULL | Calendar quarter (`1`–`4`). |
| `month` | INTEGER | NOT NULL | Calendar month number (`1`–`12`). |
| `month_name` | TEXT | NOT NULL | Full English month name (e.g., January). |
| `day` | INTEGER | NOT NULL | Day of the month (`1`–`31`). |
| `day_of_week` | TEXT | NOT NULL | Full English weekday name (e.g., Monday). |
| `is_weekend` | INTEGER | NOT NULL | Weekend flag (`1` = Saturday/Sunday, `0` = Weekday). |

---

## 3. `fact_nav`
- **Source:** `data/processed/02_nav_history.csv` (64,320 rows; includes 18,320 forward-filled weekend/holiday rows)
- **Grain:** One row per scheme per calendar day (`amfi_code`, `date`)

| Column | Type | Constraints | Business Definition |
|---|---|---|---|
| `amfi_code` | INTEGER | PK, FK → `dim_fund(amfi_code)` | AMFI scheme identifier. |
| `date` | TEXT | PK, FK → `dim_date(date_key)` | Valuation date (`YYYY-MM-DD`). |
| `nav` | REAL | NOT NULL, CHECK (`nav > 0`) | Net Asset Value per unit in INR (forward-filled on non-trading days). |

---

## 4. `fact_transactions`
- **Source:** `data/processed/08_investor_transactions.csv` (32,778 rows)
- **Grain:** One row per investor transaction (`transaction_id`)

| Column | Type | Constraints | Business Definition |
|---|---|---|---|
| `transaction_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Surrogate key for each transaction record. |
| `investor_id` | TEXT | NOT NULL | Unique identifier for the investor. |
| `transaction_date` | TEXT | NOT NULL, FK → `dim_date(date_key)` | Date the transaction occurred (`YYYY-MM-DD`). |
| `amfi_code` | INTEGER | NOT NULL, FK → `dim_fund(amfi_code)` | Target mutual fund scheme code. |
| `transaction_type` | TEXT | NOT NULL, CHECK (`IN ('SIP','Lumpsum','Redemption')`) | Standardized transaction type. |
| `amount_inr` | REAL | NOT NULL, CHECK (`amount_inr > 0`) | Transaction amount in INR. |
| `state` | TEXT | NOT NULL | Investor's state of residence. |
| `city` | TEXT | NOT NULL | Investor's city of residence. |
| `city_tier` | TEXT | NOT NULL | City tier classification (e.g., Tier 1, Tier 2, Tier 3). |
| `age_group` | TEXT | NOT NULL | Investor age bracket. |
| `gender` | TEXT | NOT NULL | Investor gender. |
| `annual_income_lakh` | REAL | NOT NULL | Investor annual income in INR lakhs. |
| `payment_mode` | TEXT | NOT NULL | Payment channel used (e.g., UPI, NetBanking, Auto-Debit). |
| `kyc_status` | TEXT | NOT NULL, CHECK (`IN ('Verified','Pending','Rejected')`) | Know Your Customer (KYC) verification status. |

---

## 5. `fact_performance`
- **Source:** `data/processed/07_scheme_performance.csv` (40 rows)
- **Grain:** One row per scheme (`amfi_code`)

| Column | Type | Constraints | Business Definition |
|---|---|---|---|
| `amfi_code` | INTEGER | PK, FK → `dim_fund(amfi_code)` | AMFI scheme identifier. |
| `scheme_name` | TEXT | NOT NULL | Scheme name (denormalized from source file). |
| `fund_house` | TEXT | NOT NULL | AMC name. |
| `category` | TEXT | NOT NULL | Fund category. |
| `plan` | TEXT | NOT NULL | Plan type (Direct/Regular). |
| `return_1yr_pct` | REAL | — | 1-year annualized return (%). |
| `return_3yr_pct` | REAL | — | 3-year annualized return (%). |
| `return_5yr_pct` | REAL | — | 5-year annualized return (%). |
| `benchmark_3yr_pct` | REAL | — | 3-year annualized return of the scheme's benchmark (%). |
| `alpha` | REAL | — | Excess return over benchmark adjusted for market risk. |
| `beta` | REAL | — | Sensitivity of scheme returns to benchmark movements. |
| `sharpe_ratio` | REAL | — | Risk-adjusted return per unit of total volatility. |
| `sortino_ratio` | REAL | — | Risk-adjusted return per unit of downside volatility. |
| `std_dev_ann_pct` | REAL | — | Annualized standard deviation of returns (%). |
| `max_drawdown_pct` | REAL | — | Largest peak-to-trough percentage decline. |
| `aum_crore` | REAL | — | Assets Under Management in INR crores. |
| `expense_ratio_pct` | REAL | CHECK (`BETWEEN 0.1 AND 2.5`) | Annual expense ratio (%). |
| `morningstar_rating` | INTEGER | — | Morningstar star rating (1–5). |
| `risk_grade` | TEXT | — | Qualitative risk grade. |
| `anomaly_flag` | INTEGER | NOT NULL, DEFAULT 0 | Data-quality flag (`1` if return outside `[-50%, 100%]` or expense ratio outside `[0.1%, 2.5%]`, else `0`). |

---

## 6. `fact_aum`
- **Source:** `data/processed/03_aum_by_fund_house.csv` (90 rows)
- **Grain:** One row per reporting date per fund house (`date`, `fund_house`)

| Column | Type | Constraints | Business Definition |
|---|---|---|---|
| `date` | TEXT | PK, FK → `dim_date(date_key)` | Reporting date (`YYYY-MM-DD`). |
| `fund_house` | TEXT | PK | Asset Management Company (AMC) name. |
| `aum_lakh_crore` | REAL | NOT NULL | Total AMC AUM in INR lakh crores. |
| `aum_crore` | REAL | NOT NULL | Total AMC AUM in INR crores. |
| `num_schemes` | INTEGER | NOT NULL | Number of active schemes managed by the AMC. |

---

## 7. `fact_monthly_sip_inflows`
- **Source:** `data/processed/04_monthly_sip_inflows.csv` (48 rows)
- **Grain:** One row per reporting month (`month`)

| Column | Type | Constraints | Business Definition |
|---|---|---|---|
| `month` | TEXT | PRIMARY KEY | Reporting month identifier. |
| `sip_inflow_crore` | REAL | NOT NULL | Total industry SIP inflows in INR crores. |
| `active_sip_accounts_crore` | REAL | NOT NULL | Total active SIP accounts in crores. |
| `new_sip_accounts_lakh` | REAL | NOT NULL | New SIP accounts registered during the month (in lakhs). |
| `sip_aum_lakh_crore` | REAL | NOT NULL | Total SIP Assets Under Management in INR lakh crores. |
| `yoy_growth_pct` | REAL | — | Year-over-year SIP inflow growth (%). `NULL` for the first 12 months where prior-year data is unavailable. |

---

## 8. `fact_category_inflows`
- **Source:** `data/processed/05_category_inflows.csv` (144 rows)
- **Grain:** One row per month per fund category (`month`, `category`)

| Column | Type | Constraints | Business Definition |
|---|---|---|---|
| `month` | TEXT | PK | Reporting month identifier. |
| `category` | TEXT | PK | Mutual fund category. |
| `net_inflow_crore` | REAL | NOT NULL | Net monthly inflow (inflows minus outflows) in INR crores. |

---

## 9. `fact_industry_folio_count`
- **Source:** `data/processed/06_industry_folio_count.csv` (21 rows)
- **Grain:** One row per reporting month (`month`)

| Column | Type | Constraints | Business Definition |
|---|---|---|---|
| `month` | TEXT | PRIMARY KEY | Reporting month identifier. |
| `total_folios_crore` | REAL | NOT NULL | Total mutual fund folios across the industry (in crores). |
| `equity_folios_crore` | REAL | NOT NULL | Equity scheme folios (in crores). |
| `debt_folios_crore` | REAL | NOT NULL | Debt scheme folios (in crores). |
| `hybrid_folios_crore` | REAL | NOT NULL | Hybrid scheme folios (in crores). |
| `others_folios_crore` | REAL | NOT NULL | Other scheme folios such as ETFs/Index/Solution-oriented (in crores). |

---

## 10. `fact_portfolio_holdings`
- **Source:** `data/processed/09_portfolio_holdings.csv` (322 rows)
- **Grain:** One row per stock holding per scheme per portfolio date (`holding_id`)

| Column | Type | Constraints | Business Definition |
|---|---|---|---|
| `holding_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Surrogate key for each holding record. |
| `amfi_code` | INTEGER | NOT NULL, FK → `dim_fund(amfi_code)` | Mutual fund scheme holding the security. |
| `stock_symbol` | TEXT | NOT NULL | Exchange ticker symbol of the underlying stock. |
| `stock_name` | TEXT | NOT NULL | Company name of the underlying stock. |
| `sector` | TEXT | NOT NULL | Industry sector classification. |
| `weight_pct` | REAL | NOT NULL | Percentage weight of the stock in the scheme's portfolio. |
| `market_value_cr` | REAL | NOT NULL | Market value of the holding in INR crores. |
| `current_price_inr` | REAL | NOT NULL | Current share price in INR. |
| `portfolio_date` | TEXT | NOT NULL, FK → `dim_date(date_key)` | Portfolio disclosure date (`YYYY-MM-DD`). |

---

## 11. `fact_benchmark_indices`
- **Source:** `data/processed/10_benchmark_indices.csv` (8,050 rows)
- **Grain:** One row per date per benchmark index (`date`, `index_name`)

| Column | Type | Constraints | Business Definition |
|---|---|---|---|
| `date` | TEXT | PK, FK → `dim_date(date_key)` | Trading date (`YYYY-MM-DD`). |
| `index_name` | TEXT | PK | Name of the market benchmark index. |
| `close_value` | REAL | NOT NULL | Closing index level on that date. |