from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def strip_strings(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype("string").str.strip()
    return df


def clean_nav_history() -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / "02_nav_history.csv")
    raw_rows = len(df)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df = df.dropna(subset=["amfi_code", "date"])
    df = df.sort_values(["amfi_code", "date"]).drop_duplicates(
        subset=["amfi_code", "date"], keep="last"
    )

    # Reindex each scheme to daily calendar dates and forward-fill weekends/holidays
    filled_parts = []
    for code, grp in df.groupby("amfi_code", sort=True):
        full_dates = pd.date_range(grp["date"].min(), grp["date"].max(), freq="D")
        g = grp.set_index("date").reindex(full_dates)
        g.index.name = "date"
        g["amfi_code"] = code
        g["nav"] = g["nav"].ffill()
        filled_parts.append(g.reset_index())

    cleaned = pd.concat(filled_parts, ignore_index=True)
    cleaned = cleaned[["amfi_code", "date", "nav"]]

    invalid_nav = (cleaned["nav"] <= 0) | cleaned["nav"].isna()
    cleaned = cleaned[~invalid_nav].copy()
    cleaned["amfi_code"] = cleaned["amfi_code"].astype(int)
    cleaned["date"] = cleaned["date"].dt.strftime("%Y-%m-%d")

    cleaned.to_csv(PROCESSED_DIR / "02_nav_history.csv", index=False)
    print(
        f"[02_nav_history] raw={raw_rows:,} -> cleaned={len(cleaned):,} "
        f"(ffilled={len(cleaned) - raw_rows:,}, invalid_nav_removed={invalid_nav.sum()})"
    )
    return cleaned


def clean_investor_transactions() -> pd.DataFrame:
    df = strip_strings(pd.read_csv(RAW_DIR / "08_investor_transactions.csv"))
    raw_rows = len(df)

    # Standardise transaction_type
    tx_map = {
        "sip": "SIP",
        "lumpsum": "Lumpsum",
        "lump sum": "Lumpsum",
        "redemption": "Redemption",
        "redeem": "Redemption",
    }
    df["transaction_type"] = (
        df["transaction_type"].str.lower().map(tx_map).fillna(df["transaction_type"])
    )

    # Parse dates and validate amount > 0
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")

    valid_types = {"SIP", "Lumpsum", "Redemption"}
    valid_kyc = {"Verified", "Pending", "Rejected"}

    bad_type = ~df["transaction_type"].isin(valid_types)
    bad_kyc = ~df["kyc_status"].isin(valid_kyc)
    bad_amt = (df["amount_inr"] <= 0) | df["amount_inr"].isna()
    bad_date = df["transaction_date"].isna()

    df = df[~(bad_amt | bad_date)].drop_duplicates().copy()
    df["amfi_code"] = df["amfi_code"].astype(int)

    df.to_csv(PROCESSED_DIR / "08_investor_transactions.csv", index=False)
    print(
        f"[08_investor_transactions] raw={raw_rows:,} -> cleaned={len(df):,} | "
        f"bad_type={bad_type.sum()}, bad_kyc={bad_kyc.sum()}, "
        f"bad_amt={bad_amt.sum()}, bad_date={bad_date.sum()}"
    )
    return df


def clean_scheme_performance() -> pd.DataFrame:
    df = strip_strings(pd.read_csv(RAW_DIR / "07_scheme_performance.csv"))
    raw_rows = len(df)

    numeric_cols = [
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
        "aum_crore",
        "expense_ratio_pct",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Flag anomalies: returns outside [-50%, 100%] or expense ratio outside [0.1%, 2.5%]
    return_cols = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "benchmark_3yr_pct"]
    return_anomaly = df[return_cols].apply(lambda s: (s < -50) | (s > 100) | s.isna()).any(axis=1)
    expense_anomaly = (df["expense_ratio_pct"] < 0.1) | (df["expense_ratio_pct"] > 2.5) | df["expense_ratio_pct"].isna()

    df["anomaly_flag"] = return_anomaly | expense_anomaly
    df = df.drop_duplicates().copy()
    df["amfi_code"] = df["amfi_code"].astype(int)

    df.to_csv(PROCESSED_DIR / "07_scheme_performance.csv", index=False)
    print(
        f"[07_scheme_performance] raw={raw_rows:,} -> cleaned={len(df):,} | "
        f"return_anomalies={return_anomaly.sum()}, expense_ratio_out_of_range={expense_anomaly.sum()}"
    )
    return df


def clean_standard_file(filename: str, date_cols: list[str] | None = None) -> pd.DataFrame:
    df = strip_strings(pd.read_csv(RAW_DIR / filename))
    raw_rows = len(df)

    if date_cols:
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")

    df = df.drop_duplicates().copy()
    df.to_csv(PROCESSED_DIR / filename, index=False)
    print(f"[{filename[:-4]}] raw={raw_rows:,} -> cleaned={len(df):,}")
    return df


def main() -> None:
    clean_standard_file("01_fund_master.csv", date_cols=["launch_date"])
    clean_nav_history()
    clean_standard_file("03_aum_by_fund_house.csv", date_cols=["date"])
    clean_standard_file("04_monthly_sip_inflows.csv")
    clean_standard_file("05_category_inflows.csv")
    clean_standard_file("06_industry_folio_count.csv")
    clean_scheme_performance()
    clean_investor_transactions()
    clean_standard_file("09_portfolio_holdings.csv", date_cols=["portfolio_date"])
    clean_standard_file("10_benchmark_indices.csv", date_cols=["date"])
    print("\nAll 10 cleaned CSVs written to data/processed/.")


if __name__ == "__main__":
    main()