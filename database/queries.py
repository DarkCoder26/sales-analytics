
from pathlib import Path
import pandas as pd
import streamlit as st


@st.cache_data
def get_sales_data():
    csv_path = Path(__file__).resolve().parent.parent / "sales_data.csv"

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Sales CSV not found: {csv_path}"
        )

    df = pd.read_csv(csv_path)

    required_columns = [
        "OrderDate",
        "Product",
        "Category",
        "Quantity",
        "UnitPrice",
        "Region",
    ]

    missing = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing CSV columns: {', '.join(missing)}"
        )

    df["OrderDate"] = pd.to_datetime(
        df["OrderDate"], errors="coerce"
    )
    df["Quantity"] = pd.to_numeric(
        df["Quantity"], errors="coerce"
    )
    df["UnitPrice"] = pd.to_numeric(
        df["UnitPrice"], errors="coerce"
    )

    df = df.dropna(
        subset=["OrderDate", "Quantity", "UnitPrice"]
    )

    df["Sales"] = df["Quantity"] * df["UnitPrice"]

    return df
    
