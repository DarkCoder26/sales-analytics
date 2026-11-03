
from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Sales Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
    .stApp {
        background-color: #0b1120;
        color: #e2e8f0;
    }

    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #263449;
    }

    .hero {
        padding: 28px;
        border-radius: 16px;
        background: linear-gradient(120deg, #172554, #172033);
        border: 1px solid #263449;
        margin-bottom: 25px;
    }

    .hero h1 {
        color: white;
        font-size: 34px;
        margin-bottom: 5px;
    }

    .hero p {
        color: #94a3b8;
        font-size: 15px;
    }

    .metric-card {
        background-color: #151f32;
        border: 1px solid #263449;
        padding: 18px;
        border-radius: 12px;
        min-height: 115px;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 13px;
        margin-bottom: 8px;
    }

    .metric-value {
        color: white;
        font-size: 25px;
        font-weight: 700;
    }

    .metric-help {
        color: #64748b;
        font-size: 12px;
        margin-top: 5px;
    }

    .section-title {
        color: white;
        font-size: 20px;
        font-weight: 650;
        margin-top: 22px;
        margin-bottom: 12px;
    }

    .insight-card {
        background-color: #151f32;
        border: 1px solid #263449;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 10px;
    }

    .insight-card p {
        color: #cbd5e1;
        margin: 5px 0 0 0;
        font-size: 14px;
    }

    .footer {
        text-align: center;
        color: #64748b;
        font-size: 12px;
        padding: 25px 0 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# CONSTANTS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "sales_data.csv"

REQUIRED_COLUMNS = [
    "OrderDate",
    "Product",
    "Category",
    "Quantity",
    "UnitPrice",
    "Region"
]


# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

@st.cache_data(ttl=300)
def load_data():

    if not CSV_FILE.exists():
        raise FileNotFoundError(
            "sales_data.csv was not found in the project directory."
        )

    df = pd.read_csv(CSV_FILE)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # Expected normalized columns
    expected = [
        "orderdate",
        "product",
        "category",
        "quantity",
        "unitprice",
        "region"
    ]

    missing = [
        col for col in expected
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing CSV columns: " + ", ".join(missing)
        )

    # Rename columns for consistent use
    df = df.rename(columns={
        "orderdate": "order_date",
        "product": "product",
        "category": "category",
        "quantity": "quantity",
        "unitprice": "unit_price",
        "region": "region"
    })

    # Convert data types
    df["order_date"] = pd.to_datetime(
        df["order_date"],
        errors="coerce"
    )

    df["quantity"] = pd.to_numeric(
        df["quantity"],
        errors="coerce"
    )

    df["unit_price"] = pd.to_numeric(
        df["unit_price"],
        errors="coerce"
    )

    # Remove invalid records
    df = df.dropna(
        subset=[
            "order_date",
            "product",
            "category",
            "quantity",
            "unit_price",
            "region"
        ]
    )

    # Validate values
    df = df[
        (df["quantity"] >= 0) &
        (df["unit_price"] >= 0)
    ].copy()

    # Calculate revenue
    df["total_amount"] = (
        df["quantity"] * df["unit_price"]
    )

    return df


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def format_currency(value):
    return f"₹{value:,.2f}"


def metric_card(label, value, help_text=""):

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-help">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def section_title(title):

    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True
    )


# --------------------------------------------------
# HERO SECTION
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>📊 Sales Intelligence Dashboard</h1>
    <p>
        Monitor business performance, analyze sales trends,
        and discover actionable business insights.
    </p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

try:

    df = load_data()

except Exception as error:

    st.error(f"Unable to load sales data: {error}")
    st.stop()


if df.empty:

    st.warning("No valid sales records found in sales_data.csv.")
    st.stop()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.markdown("## ⚙️ Dashboard Controls")

st.sidebar.caption("DATA SOURCE · CSV sales_data.csv")

if st.sidebar.button(
    "🔄 Refresh Data",
    use_container_width=True
):
    load_data.clear()
    st.rerun()


st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Date Filter")

min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


st.sidebar.markdown("---")
st.sidebar.markdown("### 📦 Category Filter")

categories = sorted(
    df["category"].astype(str).unique()
)

selected_categories = st.sidebar.multiselect(
    "Select categories",
    categories,
    default=categories
)


st.sidebar.markdown("---")
st.sidebar.markdown("### 🌍 Region Filter")

regions = sorted(
    df["region"].astype(str).unique()
)

selected_regions = st.sidebar.multiselect(
    "Select regions",
    regions,
    default=regions
)


# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_df = df.copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:

    start_date, end_date = date_range

    filtered_df = filtered_df[
        (filtered_df["order_date"].dt.date >= start_date) &
        (filtered_df["order_date"].dt.date <= end_date)
    ]


filtered_df = filtered_df[
    filtered_df["category"].astype(str).isin(
        selected_categories
    )
]

filtered_df = filtered_df[
    filtered_df["region"].astype(str).isin(
        selected_regions
    )
]


if filtered_df.empty:

    st.warning("No sales records found for the selected filters.")
    st.stop()


# --------------------------------------------------
# EXECUTIVE SUMMARY
# --------------------------------------------------

section_title("📈 Executive Summary")

total_revenue = filtered_df["total_amount"].sum()

total_units = filtered_df["quantity"].sum()

total_records = len(filtered_df)

total_products = filtered_df["product"].nunique()

total_categories = filtered_df["category"].nunique()

total_regions = filtered_df["region"].nunique()

average_unit_price = (
    filtered_df["unit_price"].mean()
)


# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    metric_card(
        "Total Revenue",
        format_currency(total_revenue),
        "Calculated from quantity × unit price"
    )

with col2:
    metric_card(
        "Units Sold",
        f"{total_units:,.0f}",
        "Total quantity sold"
    )

with col3:
    metric_card(
        "Sales Records",
        f"{total_records:,}",
        "Number of dataset rows"
    )


st.markdown("<br>", unsafe_allow_html=True)

col4, col5, col6 = st.columns(3)

with col4:
    metric_card(
        "Total Products",
        f"{total_products:,}",
        "Unique products"
    )

with col5:
    metric_card(
        "Categories",
        f"{total_categories:,}",
        "Product categories"
    )

with col6:
    metric_card(
        "Sales Regions",
        f"{total_regions:,}",
        "Regions represented"
    )


# --------------------------------------------------
# CHART CONFIGURATION
# --------------------------------------------------

plt.rcParams.update({
    "figure.facecolor": "#151f32",
    "axes.facecolor": "#151f32",
    "axes.edgecolor": "#334155",
    "axes.labelcolor": "#cbd5e1",
    "text.color": "#e2e8f0",
    "xtick.color": "#94a3b8",
    "ytick.color": "#94a3b8",
    "grid.color": "#334155"
})


# --------------------------------------------------
# SALES PERFORMANCE
# --------------------------------------------------

section_title("📊 Sales Performance Analysis")

chart_col1, chart_col2 = st.columns(2)


# Monthly revenue
with chart_col1:

    st.markdown("#### Monthly Revenue Trend")

    monthly_revenue = (
        filtered_df
        .set_index("order_date")
        .resample("ME")["total_amount"]
        .sum()
    )

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(
        monthly_revenue.index.strftime("%b %Y"),
        monthly_revenue.values,
        marker="o",
        linewidth=2.5
    )

    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (₹)")
    ax.grid(alpha=0.25)
    ax.tick_params(axis="x", rotation=35)

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)


# Category revenue
with chart_col2:

    st.markdown("#### Revenue by Category")

    category_revenue = (
        filtered_df
        .groupby("category")["total_amount"]
        .sum()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(8, 4))

    category_revenue.plot(
        kind="bar",
        ax=ax
    )

    ax.set_xlabel("Category")
    ax.set_ylabel("Revenue (₹)")
    ax.tick_params(axis="x", rotation=35)
    ax.grid(axis="y", alpha=0.25)

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)


# --------------------------------------------------
# PRODUCT PERFORMANCE
# --------------------------------------------------

section_title("🏆 Product Performance")

product_revenue = (
    filtered_df
    .groupby("product")["total_amount"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fig, ax = plt.subplots(figsize=(11, 5))

product_revenue.sort_values().plot(
    kind="barh",
    ax=ax
)

ax.set_xlabel("Revenue (₹)")
ax.set_ylabel("Product")
ax.grid(axis="x", alpha=0.25)

fig.tight_layout()

st.pyplot(fig)
plt.close(fig)


# --------------------------------------------------
# REGIONAL PERFORMANCE
# --------------------------------------------------

section_title("🌍 Regional Sales Analysis")

region_revenue = (
    filtered_df
    .groupby("region")["total_amount"]
    .sum()
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(11, 5))

region_revenue.sort_values().plot(
    kind="barh",
    ax=ax
)

ax.set_xlabel("Revenue (₹)")
ax.set_ylabel("Region")
ax.grid(axis="x", alpha=0.25)

fig.tight_layout()

st.pyplot(fig)
plt.close(fig)


# --------------------------------------------------
# BUSINESS INSIGHTS
# --------------------------------------------------

section_title("💡 Business Insights")

best_category = category_revenue.idxmax()

best_product = product_revenue.idxmax()

best_region = region_revenue.idxmax()

highest_revenue = region_revenue.max()

top_product_revenue = product_revenue.max()


insight_col1, insight_col2 = st.columns(2)

with insight_col1:

    st.markdown(
        f"""
        <div class="insight-card">
            <strong>🏆 Best Performing Category</strong>
            <p>{best_category}</p>
        </div>

        <div class="insight-card">
            <strong>📦 Top Product by Revenue</strong>
            <p>{best_product}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


with insight_col2:

    st.markdown(
        f"""
        <div class="insight-card">
            <strong>🌍 Highest Revenue Region</strong>
            <p>{best_region}</p>
        </div>

        <div class="insight-card">
            <strong>💰 Revenue from Top Region</strong>
            <p>{format_currency(highest_revenue)}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# PRODUCT SUMMARY TABLE
# --------------------------------------------------

section_title("📋 Product Performance Details")

product_summary = (
    filtered_df
    .groupby(
        ["product", "category"],
        as_index=False
    )
    .agg(
        total_units=("quantity", "sum"),
        total_revenue=("total_amount", "sum"),
        average_price=("unit_price", "mean")
    )
    .sort_values(
        "total_revenue",
        ascending=False
    )
)

product_summary["total_revenue"] = (
    product_summary["total_revenue"].round(2)
)

product_summary["average_price"] = (
    product_summary["average_price"].round(2)
)

st.dataframe(
    product_summary,
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# DETAILED SALES RECORDS
# --------------------------------------------------

section_title("🔎 Detailed Sales Records")

search_query = st.text_input(
    "Search by product, category or region"
)

display_df = filtered_df.copy()

if search_query:

    search_query = search_query.lower()

    search_columns = [
        "product",
        "category",
        "region"
    ]

    mask = display_df[search_columns].astype(str).apply(
        lambda column: column.str.lower().str.contains(
            search_query,
            regex=False,
            na=False
        )
    ).any(axis=1)

    display_df = display_df[mask]


st.dataframe(
    display_df.sort_values(
        "order_date",
        ascending=False
    ),
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# DOWNLOAD REPORT
# --------------------------------------------------

section_title("⬇️ Export Sales Report")

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="📥 Download Filtered Sales Report",
    data=csv_data,
    file_name="sales_report.csv",
    mime="text/csv",
    use_container_width=True
)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("""
<div class="footer">
    Sales Intelligence Dashboard · Powered by Streamlit and Pandas
    <br>
    Data Source: CSV · Cache Duration: 5 Minutes
</div>
""", unsafe_allow_html=True)
        
