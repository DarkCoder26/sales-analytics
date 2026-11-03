
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
        color: #ffffff;
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
        color: #ffffff;
        font-size: 25px;
        font-weight: 700;
    }

    .metric-help {
        color: #64748b;
        font-size: 12px;
        margin-top: 5px;
    }

    .section-title {
        color: #ffffff;
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

    div[data-testid="stDataFrame"] {
        border: 1px solid #263449;
        border-radius: 10px;
    }

    .stButton button {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# CONSTANTS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "sales_data.csv"

REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "customer_id",
    "customer_name",
    "city",
    "state",
    "gender",
    "product_id",
    "product_name",
    "category",
    "price",
    "quantity",
    "total_amount"
]


# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

@st.cache_data(ttl=300, show_spinner="Loading sales data from CSV...")
def load_data():

    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"sales_data.csv not found at: {CSV_FILE}"
        )

    df = pd.read_csv(CSV_FILE)

st.write("CSV Column Names:", df.columns.tolist())
st.write("First 5 Records:", df.head())
    
    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    # Validate required columns
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    # Keep expected columns
    df = df[REQUIRED_COLUMNS].copy()

    # Convert date
    df["order_date"] = pd.to_datetime(
        df["order_date"],
        errors="coerce"
    )

    # Convert numeric columns
    numeric_columns = [
        "price",
        "quantity",
        "total_amount"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # Remove invalid rows
    df = df.dropna(
        subset=[
            "order_date",
            "total_amount",
            "quantity"
        ]
    )

    # Remove negative or invalid values
    df = df[
        (df["quantity"] >= 0) &
        (df["total_amount"] >= 0)
    ]

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

except FileNotFoundError:
    st.error(
        "Sales dataset not found. Please add "
        "`sales_data.csv` to the project root directory."
    )
    st.stop()

except Exception as error:
    st.error(f"Unable to load sales data: {error}")
    st.stop()


if df.empty:
    st.warning(
        "The sales_data.csv file is empty or contains no valid records."
    )
    st.stop()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.markdown("## ⚙️ Dashboard Controls")

st.sidebar.caption("DATA SOURCE · CSV sales_data.csv")

if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
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
    df["category"].dropna().astype(str).unique()
)

selected_categories = st.sidebar.multiselect(
    "Select categories",
    categories,
    default=categories
)


st.sidebar.markdown("---")
st.sidebar.markdown("### 📍 State Filter")

states = sorted(
    df["state"].dropna().astype(str).unique()
)

selected_states = st.sidebar.multiselect(
    "Select states",
    states,
    default=states
)


st.sidebar.markdown("---")
st.sidebar.markdown("### 🏙️ City Filter")

cities = sorted(
    df["city"].dropna().astype(str).unique()
)

selected_cities = st.sidebar.multiselect(
    "Select cities",
    cities,
    default=cities
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
    filtered_df["category"].astype(str).isin(selected_categories)
]

filtered_df = filtered_df[
    filtered_df["state"].astype(str).isin(selected_states)
]

filtered_df = filtered_df[
    filtered_df["city"].astype(str).isin(selected_cities)
]


if filtered_df.empty:
    st.warning(
        "No sales records found for the selected filters. "
        "Please change your filters."
    )
    st.stop()


# --------------------------------------------------
# EXECUTIVE SUMMARY
# --------------------------------------------------

section_title("📈 Executive Summary")

total_revenue = filtered_df["total_amount"].sum()

total_orders = filtered_df["order_id"].nunique()

total_units = filtered_df["quantity"].sum()

total_customers = filtered_df["customer_id"].nunique()

average_order_value = (
    total_revenue / total_orders
    if total_orders > 0 else 0
)

total_line_items = len(filtered_df)


# --------------------------------------------------
# KPI METRICS
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    metric_card(
        "Total Revenue",
        format_currency(total_revenue),
        "Revenue generated"
    )

with col2:
    metric_card(
        "Total Orders",
        f"{total_orders:,}",
        "Unique orders"
    )

with col3:
    metric_card(
        "Units Sold",
        f"{total_units:,.0f}",
        "Total quantity sold"
    )


st.markdown("<br>", unsafe_allow_html=True)

col4, col5, col6 = st.columns(3)

with col4:
    metric_card(
        "Total Customers",
        f"{total_customers:,}",
        "Unique customers"
    )

with col5:
    metric_card(
        "Average Order Value",
        format_currency(average_order_value),
        "Revenue per unique order"
    )

with col6:
    metric_card(
        "Sales Line Items",
        f"{total_line_items:,}",
        "Total transaction records"
    )


# --------------------------------------------------
# CHART SETTINGS
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
# MONTHLY REVENUE TREND
# --------------------------------------------------

section_title("📊 Sales Performance Analysis")

chart_col1, chart_col2 = st.columns(2)

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


# --------------------------------------------------
# CATEGORY REVENUE
# --------------------------------------------------

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
# TOP PRODUCTS
# --------------------------------------------------

section_title("🏆 Product Performance")

product_revenue = (
    filtered_df
    .groupby("product_name")["total_amount"]
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
# REVENUE BY CITY
# --------------------------------------------------

section_title("🌍 Geographic Sales Analysis")

city_revenue = (
    filtered_df
    .groupby("city")["total_amount"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fig, ax = plt.subplots(figsize=(11, 5))

city_revenue.sort_values().plot(
    kind="barh",
    ax=ax
)

ax.set_xlabel("Revenue (₹)")
ax.set_ylabel("City")
ax.grid(axis="x", alpha=0.25)

fig.tight_layout()

st.pyplot(fig)
plt.close(fig)


# --------------------------------------------------
# BUSINESS INSIGHTS
# --------------------------------------------------

section_title("💡 Business Insights")

best_category = (
    filtered_df.groupby("category")["total_amount"]
    .sum()
    .idxmax()
)

best_city = (
    filtered_df.groupby("city")["total_amount"]
    .sum()
    .idxmax()
)

best_product = (
    filtered_df.groupby("product_name")["total_amount"]
    .sum()
    .idxmax()
)

top_customer = (
    filtered_df.groupby("customer_name")["total_amount"]
    .sum()
    .idxmax()
)

insight_col1, insight_col2 = st.columns(2)

with insight_col1:

    st.markdown(
        f"""
        <div class="insight-card">
            <strong>🏆 Best Performing Category</strong>
            <p>{best_category}</p>
        </div>

        <div class="insight-card">
            <strong>📍 Highest Revenue City</strong>
            <p>{best_city}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


with insight_col2:

    st.markdown(
        f"""
        <div class="insight-card">
            <strong>📦 Top Selling Product by Revenue</strong>
            <p>{best_product}</p>
        </div>

        <div class="insight-card">
            <strong>👤 Highest Spending Customer</strong>
            <p>{top_customer}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# CUSTOMER PERFORMANCE
# --------------------------------------------------

section_title("👥 Customer Performance")

customer_performance = (
    filtered_df
    .groupby(
        ["customer_id", "customer_name"],
        as_index=False
    )
    .agg(
        total_spent=("total_amount", "sum"),
        total_orders=("order_id", "nunique"),
        total_units=("quantity", "sum")
    )
    .sort_values(
        "total_spent",
        ascending=False
    )
)

customer_performance["total_spent"] = (
    customer_performance["total_spent"].round(2)
)

st.dataframe(
    customer_performance,
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# DETAILED SALES RECORDS
# --------------------------------------------------

section_title("📋 Detailed Sales Records")

search_query = st.text_input(
    "🔍 Search by order ID, customer, product or city"
)

display_df = filtered_df.copy()

if search_query:

    search_query = search_query.lower()

    search_columns = [
        "order_id",
        "customer_id",
        "customer_name",
        "product_name",
        "city"
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
    label="📥 Download Filtered Sales Data",
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
    Data source: CSV · Cache duration: 5 minutes
</div>
""", unsafe_allow_html=True)
    
