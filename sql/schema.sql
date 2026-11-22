PRAGMA foreign_keys = ON;

-- ============================================================
-- DIMENSION TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code          INTEGER PRIMARY KEY,
    fund_house         TEXT NOT NULL,
    scheme_name        TEXT NOT NULL,
    category           TEXT NOT NULL,
    sub_category       TEXT NOT NULL,
    plan               TEXT NOT NULL,
    launch_date        TEXT NOT NULL,
    benchmark          TEXT NOT NULL,
    expense_ratio_pct  REAL NOT NULL,
    exit_load_pct      REAL NOT NULL,
    min_sip_amount     INTEGER NOT NULL,
    min_lumpsum_amount INTEGER NOT NULL,
    fund_manager       TEXT NOT NULL,
    risk_category      TEXT NOT NULL,
    sebi_category_code TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_key    TEXT PRIMARY KEY,   -- YYYY-MM-DD
    year        INTEGER NOT NULL,
    quarter     INTEGER NOT NULL,
    month       INTEGER NOT NULL,
    month_name  TEXT NOT NULL,
    day         INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    is_weekend  INTEGER NOT NULL    -- 1 = Sat/Sun, 0 = Weekday
);

-- ============================================================
-- CORE FACT TABLES (STAR SCHEMA)
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_nav (
    amfi_code INTEGER NOT NULL,
    date      TEXT NOT NULL,
    nav       REAL NOT NULL CHECK (nav > 0),
    PRIMARY KEY (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date)      REFERENCES dim_date(date_key)
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id        TEXT NOT NULL,
    transaction_date   TEXT NOT NULL,
    amfi_code          INTEGER NOT NULL,
    transaction_type   TEXT NOT NULL CHECK (transaction_type IN ('SIP', 'Lumpsum', 'Redemption')),
    amount_inr         REAL NOT NULL CHECK (amount_inr > 0),
    state              TEXT NOT NULL,
    city               TEXT NOT NULL,
    city_tier          TEXT NOT NULL,
    age_group          TEXT NOT NULL,
    gender             TEXT NOT NULL,
    annual_income_lakh REAL NOT NULL,
    payment_mode       TEXT NOT NULL,
    kyc_status         TEXT NOT NULL CHECK (kyc_status IN ('Verified', 'Pending', 'Rejected')),
    FOREIGN KEY (amfi_code)        REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (transaction_date) REFERENCES dim_date(date_key)
);

CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code          INTEGER PRIMARY KEY,
    scheme_name        TEXT NOT NULL,
    fund_house         TEXT NOT NULL,
    category           TEXT NOT NULL,
    plan               TEXT NOT NULL,
    return_1yr_pct     REAL,
    return_3yr_pct     REAL,
    return_5yr_pct     REAL,
    benchmark_3yr_pct  REAL,
    alpha              REAL,
    beta               REAL,
    sharpe_ratio       REAL,
    sortino_ratio      REAL,
    std_dev_ann_pct    REAL,
    max_drawdown_pct   REAL,
    aum_crore          REAL,
    expense_ratio_pct  REAL CHECK (expense_ratio_pct BETWEEN 0.1 AND 2.5),
    morningstar_rating INTEGER,
    risk_grade         TEXT,
    anomaly_flag       INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_aum (
    date           TEXT NOT NULL,
    fund_house     TEXT NOT NULL,
    aum_lakh_crore REAL NOT NULL,
    aum_crore      REAL NOT NULL,
    num_schemes    INTEGER NOT NULL,
    PRIMARY KEY (date, fund_house),
    FOREIGN KEY (date) REFERENCES dim_date(date_key)
);

-- ============================================================
-- SUPPORTING FACT TABLES (REMAINING CLEANED DATASETS)
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_monthly_sip_inflows (
    month                     TEXT PRIMARY KEY,
    sip_inflow_crore          REAL NOT NULL,
    active_sip_accounts_crore REAL NOT NULL,
    new_sip_accounts_lakh     REAL NOT NULL,
    sip_aum_lakh_crore        REAL NOT NULL,
    yoy_growth_pct            REAL
);

CREATE TABLE IF NOT EXISTS fact_category_inflows (
    month            TEXT NOT NULL,
    category         TEXT NOT NULL,
    net_inflow_crore REAL NOT NULL,
    PRIMARY KEY (month, category)
);

CREATE TABLE IF NOT EXISTS fact_industry_folio_count (
    month               TEXT PRIMARY KEY,
    total_folios_crore  REAL NOT NULL,
    equity_folios_crore REAL NOT NULL,
    debt_folios_crore   REAL NOT NULL,
    hybrid_folios_crore REAL NOT NULL,
    others_folios_crore REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_portfolio_holdings (
    holding_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code         INTEGER NOT NULL,
    stock_symbol      TEXT NOT NULL,
    stock_name        TEXT NOT NULL,
    sector            TEXT NOT NULL,
    weight_pct        REAL NOT NULL,
    market_value_cr   REAL NOT NULL,
    current_price_inr REAL NOT NULL,
    portfolio_date    TEXT NOT NULL,
    FOREIGN KEY (amfi_code)      REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (portfolio_date) REFERENCES dim_date(date_key)
);

CREATE TABLE IF NOT EXISTS fact_benchmark_indices (
    date        TEXT NOT NULL,
    index_name  TEXT NOT NULL,
    close_value REAL NOT NULL,
    PRIMARY KEY (date, index_name),
    FOREIGN KEY (date) REFERENCES dim_date(date_key)
);