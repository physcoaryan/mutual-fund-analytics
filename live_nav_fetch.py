
import requests
import pandas as pd
from pathlib import Path

API_URL = "https://api.mfapi.in/mf/"

# The six codes explicitly listed in the assignment.
ASSIGNMENT_CODES = {
    125497: "HDFC Top 100 - Direct Growth",
    119551: "SBI Bluechip - Regular Growth",
    120503: "ICICI Pru Bluechip - Regular Growth",
    118632: "Nippon India Large Cap",
    119092: "Axis Bluechip - Regular Growth",
    120841: "Kotak Bluechip - Regular Growth"
}

# Current AMFI codes for the intended funds/plans.
# The Nippon Regular Growth code is included separately because
# assignment code 118632 represents Direct Growth.
VERIFIED_CODES = {
    119018: "HDFC Large Cap - Direct Growth",
    103504: "SBI Large Cap - Regular Growth",
    108466: "ICICI Pru Large Cap - Regular Growth",
    106235: "Nippon India Large Cap - Regular Growth",
    112277: "Axis Large Cap - Regular Growth",
    114458: "Kotak Large Cap - Regular Growth"
}

SCHEMES = {}

for code, label in ASSIGNMENT_CODES.items():
    SCHEMES[code] = {
        "reference_label": label,
        "mapping_source": "Assignment-specified code"
    }

for code, label in VERIFIED_CODES.items():
    SCHEMES[code] = {
        "reference_label": label,
        "mapping_source": "Current AMFI-verified code"
    }

# Output directory
OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

nav_records = []
metadata_records = []

print("STARTING LIVE NAV FETCH")
print("=" * 75)

for code, details in SCHEMES.items():

    url = f"{API_URL}{code}"

    print(f"\nFetching scheme code: {code}")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        result = response.json()

        meta = result.get("meta", {})
        nav_data = result.get("data", [])

        actual_name = meta.get("scheme_name", "Unknown")
        actual_code = meta.get("scheme_code", code)

        print("Actual scheme name:", actual_name)
        print("Fund house:", meta.get("fund_house", "Unknown"))
        print("NAV records:", len(nav_data))

        metadata_records.append({
            "requested_code": code,
            "api_scheme_code": actual_code,
            "reference_label": details["reference_label"],
            "mapping_source": details["mapping_source"],
            "actual_scheme_name": actual_name,
            "fund_house": meta.get("fund_house"),
            "scheme_type": meta.get("scheme_type"),
            "scheme_category": meta.get("scheme_category"),
            "nav_records": len(nav_data),
            "source_url": url
        })

        for item in nav_data:
            nav_records.append({
                "scheme_code": code,
                "actual_scheme_name": actual_name,
                "fund_house": meta.get("fund_house"),
                "reference_label": details["reference_label"],
                "mapping_source": details["mapping_source"],
                "date": item.get("date"),
                "nav": item.get("nav")
            })

    except (requests.exceptions.RequestException, ValueError) as error:
        print(f"FAILED for code {code}: {error}")

# Save NAV data
nav_df = pd.DataFrame(nav_records)

if not nav_df.empty:
    nav_df["nav"] = pd.to_numeric(nav_df["nav"], errors="coerce")

nav_path = OUTPUT_DIR / "live_nav_all_schemes.csv"
nav_df.to_csv(nav_path, index=False)

# Save metadata
metadata_df = pd.DataFrame(metadata_records)

metadata_path = OUTPUT_DIR / "live_scheme_metadata.csv"
metadata_df.to_csv(metadata_path, index=False)

print("\n" + "=" * 75)
print("LIVE NAV FETCH COMPLETED")
print("Unique scheme codes configured:", len(SCHEMES))
print("Successfully fetched schemes:", len(metadata_records))
print("Total NAV records:", len(nav_df))
print("NAV file:", nav_path)
print("Metadata file:", metadata_path)
print("=" * 75)

print("\nACTUAL API SCHEME MAPPINGS")
print(metadata_df[
    ["requested_code", "actual_scheme_name", "mapping_source"]
].to_string(index=False))
