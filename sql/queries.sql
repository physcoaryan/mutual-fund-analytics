-- ============================================================
-- Mutual Fund Analytics — 10 Analytical SQL Queries
-- Database: bluestock_mf.db (SQLite)
-- ============================================================

-- 1. Top 5 funds by AUM (Crore)
SELECT
    d.amfi_code,
    d.scheme_name,
    d.fund_house,
    d.category,
    d.sub_category,
    p.aum_crore,
    p.return_3yr_pct
FROM fact_performance p
JOIN dim_fund d ON p.amfi_code = d.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month by scheme
SELECT
    dt.year,
    dt.month,
    dt.month_name,
    n.amfi_code,
    d.scheme_name,
    ROUND(AVG(n.nav), 4) AS avg_monthly_nav,
    ROUND(MIN(n.nav), 4) AS min_monthly_nav,
    ROUND(MAX(n.nav), 4) AS max_monthly_nav
FROM fact_nav n
JOIN dim_date dt ON n.date = dt.date_key
JOIN dim_fund d  ON n.amfi_code = d.amfi_code
GROUP BY dt.year, dt.month, dt.month_name, n.amfi_code, d.scheme_name
ORDER BY dt.year, dt.month, n.amfi_code;

-- 3. Monthly SIP inflows and YoY growth
SELECT
    month,
    sip_inflow_crore,
    yoy_growth_pct,
    active_sip_accounts_crore,
    sip_aum_lakh_crore
FROM fact_monthly_sip_inflows
ORDER BY month;

-- 4. Investor transactions summary by state
SELECT
    state,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr,
    ROUND(AVG(amount_inr), 2) AS avg_ticket_size_inr,
    COUNT(DISTINCT investor_id) AS unique_investors
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

-- 5. Funds with expense ratio below 1%
SELECT
    d.amfi_code,
    d.scheme_name,
    d.fund_house,
    d.category,
    d.sub_category,
    d.expense_ratio_pct,
    p.return_3yr_pct,
    p.sharpe_ratio
FROM dim_fund d
JOIN fact_performance p ON d.amfi_code = p.amfi_code
WHERE d.expense_ratio_pct < 1.0
ORDER BY d.expense_ratio_pct ASC;

-- 6. Top 5 schemes by risk-adjusted return (Sharpe Ratio)
SELECT
    d.amfi_code,
    d.scheme_name,
    d.sub_category,
    p.sharpe_ratio,
    p.alpha,
    p.return_3yr_pct,
    p.std_dev_ann_pct
FROM fact_performance p
JOIN dim_fund d ON p.amfi_code = d.amfi_code
ORDER BY p.sharpe_ratio DESC
LIMIT 5;

-- 7. Transaction volume and value by transaction type and KYC status
SELECT
    transaction_type,
    kyc_status,
    COUNT(*) AS txn_count,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr,
    ROUND(AVG(amount_inr), 2) AS avg_amount_inr
FROM fact_transactions
GROUP BY transaction_type, kyc_status
ORDER BY transaction_type, total_amount_inr DESC;

-- 8. Latest AUM and scheme count by fund house
SELECT
    date,
    fund_house,
    aum_lakh_crore,
    aum_crore,
    num_schemes
FROM fact_aum
WHERE date = (SELECT MAX(date) FROM fact_aum)
ORDER BY aum_crore DESC;

-- 9. Top 10 portfolio sectors by total market value (Crore)
SELECT
    sector,
    COUNT(DISTINCT stock_symbol) AS distinct_stocks,
    ROUND(SUM(market_value_cr), 2) AS total_market_value_cr,
    ROUND(AVG(weight_pct), 2) AS avg_weight_pct
FROM fact_portfolio_holdings
GROUP BY sector
ORDER BY total_market_value_cr DESC
LIMIT 10;

-- 10. Total net inflows by fund category
SELECT
    category,
    COUNT(*) AS months_reported,
    ROUND(SUM(net_inflow_crore), 2) AS total_net_inflow_cr,
    ROUND(AVG(net_inflow_crore), 2) AS avg_monthly_inflow_cr
FROM fact_category_inflows
GROUP BY category
ORDER BY total_net_inflow_cr DESC;