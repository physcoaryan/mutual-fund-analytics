# Day 1 - Data Quality Summary

## 1. Dataset overview

| Dataset | Rows | Columns | Missing values | Duplicate rows |
|---|---:|---:|---:|---:|
| 01_fund_master.csv | 40 | 15 | 0 | 0 |
| 02_nav_history.csv | 46000 | 3 | 0 | 0 |
| 03_aum_by_fund_house.csv | 90 | 5 | 0 | 0 |
| 04_monthly_sip_inflows.csv | 48 | 6 | 12 | 0 |
| 05_category_inflows.csv | 144 | 3 | 0 | 0 |
| 06_industry_folio_count.csv | 21 | 6 | 0 | 0 |
| 07_scheme_performance.csv | 40 | 19 | 0 | 0 |
| 08_investor_transactions.csv | 32778 | 13 | 0 | 0 |
| 09_portfolio_holdings.csv | 322 | 8 | 0 | 0 |
| 10_benchmark_indices.csv | 8050 | 3 | 0 | 0 |

**Total records across available datasets:** 87533

## 2. Missing-value observations

### 04_monthly_sip_inflows.csv

- `yoy_growth_pct`: 12 missing values

## 3. Fund master exploration

- Fund master records: 40
- Unique fund houses: 10
- Unique categories: 2
- Unique sub-categories: 12
- Unique risk grades: 5

## 4. AMFI scheme-code validation

- Unique codes in fund master: 40
- Unique codes in NAV history: 40
- Codes matched: 40
- Codes missing from NAV history: 0

**Result: All fund-master codes are present in nav_history.**

## 5. Understanding AMFI scheme codes

AMFI scheme codes are numeric identifiers used to identify mutual fund schemes. The digits should not be interpreted as a code for fund house, category, plan, or risk grade. These details should be read from the scheme master or official scheme metadata. Different plans and options can have different scheme codes.

The live NAV exercise also demonstrated why scheme names should be checked against the actual API metadata rather than inferred from a scheme code alone.