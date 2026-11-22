from pathlib import Path
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

PROCESSED_DIR = Path("data/processed")
SCHEMA_PATH = Path("sql/schema.sql")
DB_PATH = Path("bluestock_mf.db")


def build_dim_date(dfs_and_cols: list[tuple[pd.DataFrame, str]]) -> pd.DataFrame:
    all_dates = pd.concat(
        [pd.to_datetime(df[col], errors="coerce") for df, col in dfs_and_cols],
        ignore_index=True,
    ).dropna().drop_duplicates().sort_values()

    return pd.DataFrame(
        {
            "date_key": all_dates.dt.strftime("%Y-%m-%d"),
            "year": all_dates.dt.year,
            "quarter": all_dates.dt.quarter,
            "month": all_dates.dt.month,
            "month_name": all_dates.dt.month_name(),
            "day": all_dates.dt.day,
            "day_of_week": all_dates.dt.day_name(),
            "is_weekend": (all_dates.dt.dayofweek >= 5).astype(int),
        }
    )


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    # Create tables from schema.sql
    with sqlite3.connect(DB_PATH) as raw_conn:
        raw_conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    engine = create_engine(f"sqlite:///{DB_PATH}")

    # Load cleaned CSVs
    fund_master = pd.read_csv(PROCESSED_DIR / "01_fund_master.csv")
    nav_history = pd.read_csv(PROCESSED_DIR / "02_nav_history.csv")
    aum_fh = pd.read_csv(PROCESSED_DIR / "03_aum_by_fund_house.csv")
    sip_inflows = pd.read_csv(PROCESSED_DIR / "04_monthly_sip_inflows.csv")
    cat_inflows = pd.read_csv(PROCESSED_DIR / "05_category_inflows.csv")
    folio_count = pd.read_csv(PROCESSED_DIR / "06_industry_folio_count.csv")
    scheme_perf = pd.read_csv(PROCESSED_DIR / "07_scheme_performance.csv")
    transactions = pd.read_csv(PROCESSED_DIR / "08_investor_transactions.csv")
    holdings = pd.read_csv(PROCESSED_DIR / "09_portfolio_holdings.csv")
    benchmarks = pd.read_csv(PROCESSED_DIR / "10_benchmark_indices.csv")

    # Convert boolean anomaly_flag to 0/1 for SQLite INTEGER column
    scheme_perf["anomaly_flag"] = scheme_perf["anomaly_flag"].astype(int)

    # Build dim_date from all fact date columns so every FK is satisfied
    dim_date = build_dim_date(
        [
            (nav_history, "date"),
            (transactions, "transaction_date"),
            (aum_fh, "date"),
            (holdings, "portfolio_date"),
            (benchmarks, "date"),
        ]
    )

    load_plan = [
        ("dim_fund", fund_master),
        ("dim_date", dim_date),
        ("fact_nav", nav_history),
        ("fact_transactions", transactions),
        ("fact_performance", scheme_perf),
        ("fact_aum", aum_fh),
        ("fact_monthly_sip_inflows", sip_inflows),
        ("fact_category_inflows", cat_inflows),
        ("fact_industry_folio_count", folio_count),
        ("fact_portfolio_holdings", holdings),
        ("fact_benchmark_indices", benchmarks),
    ]

    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys = ON;"))
        for table_name, df in load_plan:
            df.to_sql(table_name, con=conn, if_exists="append", index=False)

    # Verify row counts
    print(f"\n{'Table':<28} {'Expected':>10} {'SQLite':>10} {'Status':>8}")
    print("-" * 60)
    all_ok = True
    with engine.connect() as conn:
        for table_name, df in load_plan:
            db_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            ok = db_count == len(df)
            all_ok = all_ok and ok
            print(f"{table_name:<28} {len(df):>10,} {db_count:>10,} {'OK' if ok else 'MISMATCH':>8}")

    print("\nDatabase ready:", DB_PATH.resolve())
    if not all_ok:
        raise SystemExit("Row count mismatch detected!")


if __name__ == "__main__":
    main()