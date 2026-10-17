import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from database.queries import get_sales_data

st.set_page_config(page_title="Sales Intelligence", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

BG, PANEL, BORDER = "#0B1020", "#111A2E", "#26334F"
BLUE, PURPLE, GREEN = "#38BDF8", "#A78BFA", "#34D399"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
.stApp{{background:radial-gradient(ellipse at 10% 0%,rgba(56,189,248,.09),transparent 34%),{BG};color:#F3F6FC;font-family:'DM Sans',sans-serif}}
[data-testid="stHeader"]{{background:rgba(11,16,32,.9)}}
.block-container{{max-width:1600px;padding-top:1.7rem;padding-bottom:3rem}}
[data-testid="stSidebar"]{{background:#0D1426;border-right:1px solid {BORDER}}}
[data-testid="stSidebar"] *{{color:#F3F6FC}}
h1,h2,h3,h4{{color:#F3F6FC!important;font-family:'Space Grotesk',sans-serif!important}}
p,label{{color:#A8B6CC}}
div[data-testid="stMetric"]{{background:linear-gradient(145deg,#151F36,#10182A);border:1px solid {BORDER};border-radius:16px;padding:18px 20px;min-height:125px;box-shadow:0 8px 26px rgba(0,0,0,.12)}}
div[data-testid="stMetricLabel"] p{{color:#A7B4CA!important;font-size:.82rem!important;font-weight:600!important}}
div[data-testid="stMetricValue"]{{color:#F8FAFC!important;font-family:'Space Grotesk',sans-serif;font-size:clamp(1.25rem,1.8vw,2rem)!important;font-weight:700!important}}
[data-testid="stSelectbox"]>div>div,[data-testid="stMultiSelect"]>div>div,[data-testid="stDateInput"]>div>div,[data-testid="stTextInput"]>div>div{{background:#111A2E;border-color:#34415C;border-radius:10px}}
.hero{{background:linear-gradient(110deg,rgba(56,189,248,.13),rgba(167,139,250,.11) 65%,rgba(17,26,46,.5));border:1px solid #293956;border-radius:22px;padding:25px 28px;margin-bottom:22px}}
.eyebrow{{color:{BLUE};font-size:.75rem;letter-spacing:.15em;font-weight:700;text-transform:uppercase;margin-bottom:8px}}
.hero-title{{font-family:'Space Grotesk',sans-serif;font-size:clamp(1.8rem,3vw,2.55rem);line-height:1.12;font-weight:700;color:#F8FAFC}}
.hero-subtitle{{color:#A8B6CC;margin-top:10px;font-size:.96rem}}
.section-head{{display:flex;align-items:center;gap:10px;margin:25px 0 13px;font-family:'Space Grotesk',sans-serif;font-size:1.15rem;font-weight:700;color:#F1F5F9}}
.section-dot{{width:8px;height:8px;border-radius:50%;background:{BLUE};box-shadow:0 0 14px {BLUE};display:inline-block}}
.panel{{background:linear-gradient(145deg,#151F36,#0F1728);border:1px solid {BORDER};border-radius:16px;padding:16px 18px}}
.panel-label{{color:#9BAAC1;font-size:.8rem;font-weight:600;margin-bottom:8px}}
.stButton button,.stDownloadButton button{{border-radius:10px;border:1px solid #34415C;background:#17233B;color:#F8FAFC;font-weight:600;min-height:2.5rem}}
.stButton button:hover,.stDownloadButton button:hover{{border-color:{BLUE};color:{BLUE}}}
[data-testid="stDataFrame"]{{border:1px solid {BORDER};border-radius:12px;overflow:hidden}}
hr{{border-color:{BORDER}}}
.footer{{border-top:1px solid {BORDER};padding-top:16px;margin-top:28px;color:#64748B;font-size:.78rem}}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300, show_spinner="Loading sales data from MySQL...")
def load_data():
    df = get_sales_data().copy()
    if df.empty:
        return df
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    for c in ["price", "quantity", "total_amount"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.dropna(subset=["order_date"])

def money(v):
    return f"₹{float(v or 0):,.0f}"

def section(title):
    st.markdown(f'<div class="section-head"><span class="section-dot"></span>{title}</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="hero">
  <div class="eyebrow">Business intelligence · Sales performance</div>
  <div class="hero-title">Sales Intelligence</div>
  <div class="hero-subtitle">A clear view of revenue, customer behavior and product performance.</div>
</div>
""", unsafe_allow_html=True)

_, refresh_col = st.columns([5, 1])
with refresh_col:
    if st.button("↻ Refresh data", use_container_width=True):
        load_data.clear()
        st.rerun()

try:
    df = load_data()
except Exception as exc:
    st.error("Could not load sales data from MySQL. Check the database connection and query.")
    with st.expander("Technical details"):
        st.exception(exc)
    st.stop()

if df.empty:
    st.warning("No sales records were returned. Add records to MySQL and refresh.")
    st.stop()

required = ["order_id","order_date","customer_id","customer_name","city","state","gender","product_id","product_name","category","price","quantity","total_amount"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error(f"Missing columns from the sales query: {', '.join(missing)}")
    st.stop()

with st.sidebar:
    st.markdown("## ◈ Control center")
    st.caption("Refine the reporting period and sales segments.")
    st.divider()
    min_date, max_date = df["order_date"].min().date(), df["order_date"].max().date()
    date_range = st.date_input("Reporting period", value=(min_date,max_date), min_value=min_date,max_value=max_date,format="YYYY-MM-DD")
    categories = sorted(df["category"].dropna().astype(str).unique())
    selected_categories = st.multiselect("Product categories", categories, default=categories)
    states = sorted(df["state"].dropna().astype(str).unique())
    selected_states = st.multiselect("States / regions", states, default=states)
    cities = sorted(df.loc[df["state"].astype(str).isin(selected_states),"city"].dropna().astype(str).unique()) if selected_states else []
    selected_cities = st.multiselect("Cities", cities, default=cities)
    st.divider()
    st.caption(f"DATA SOURCE  ·  MySQL sales_analytics")
    st.caption(f"ROWS LOADED  ·  {len(df):,}")
    st.caption("Cache refresh · 5 minutes")

data = df.copy()
if isinstance(date_range,(tuple,list)) and len(date_range)==2:
    start,end=date_range
    data=data[data["order_date"].dt.date.between(start,end)]
elif isinstance(date_range,(tuple,list)) and len(date_range)==1:
    data=data[data["order_date"].dt.date==date_range[0]]
data=data[
    data["category"].astype(str).isin(selected_categories)
    & data["state"].astype(str).isin(selected_states)
    & data["city"].astype(str).isin(selected_cities)
]
if data.empty:
    st.warning("No records match these filters. Adjust the date range or selected segments.")
    st.stop()

section("Executive overview")
revenue=data["total_amount"].sum()
orders=data["order_id"].nunique()
units=data["quantity"].sum()
customers=data["customer_id"].nunique()
aov=revenue/orders if orders else 0
k1,k2,k3,k4=st.columns(4)
k1.metric("TOTAL REVENUE",money(revenue))
k2.metric("ORDERS",f"{orders:,}")
k3.metric("UNITS SOLD",f"{units:,.0f}")
k4.metric("UNIQUE CUSTOMERS",f"{customers:,}")
k5,k6=st.columns(2)
k5.metric("AVERAGE ORDER VALUE",money(aov))
k6.metric("SALES LINE ITEMS",f"{len(data):,}")

section("Revenue & demand trends")
left,right=st.columns([1.55,1])
monthly=data.assign(month=data["order_date"].dt.to_period("M").dt.to_timestamp()).groupby("month",as_index=False)["total_amount"].sum().sort_values("month")
with left:
    st.markdown('<div class="panel">**Revenue over time**</div>',unsafe_allow_html=True)
    fig,ax=plt.subplots(figsize=(8.5,3.6)); fig.patch.set_facecolor(PANEL); ax.set_facecolor(PANEL)
    ax.plot(monthly["month"],monthly["total_amount"],color=BLUE,linewidth=2.6,marker="o",markersize=4)
    ax.fill_between(monthly["month"],monthly["total_amount"],color=BLUE,alpha=.12)
    ax.set_title("Monthly revenue",loc="left",fontsize=12,pad=12,color="#F3F6FC")
    ax.set_ylabel("Revenue (₹)",color="#94A3B8"); ax.tick_params(colors="#B6C2D5",labelsize=8)
    ax.grid(axis="y",color="#2A3650",alpha=.6)
    for spine in ax.spines.values(): spine.set_color(BORDER)
    fig.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close(fig)
with right:
    st.markdown('<div class="panel">**Revenue by category**</div>',unsafe_allow_html=True)
    cat=data.groupby("category",as_index=False)["total_amount"].sum().sort_values("total_amount")
    fig,ax=plt.subplots(figsize=(5.2,3.6)); fig.patch.set_facecolor(PANEL); ax.set_facecolor(PANEL)
    ax.barh(cat["category"].astype(str),cat["total_amount"],color=PURPLE)
    ax.set_xlabel("Revenue (₹)",color="#94A3B8"); ax.tick_params(colors="#B6C2D5",labelsize=8)
    ax.grid(axis="x",color="#2A3650",alpha=.6); ax.grid(axis="y",visible=False)
    for spine in ax.spines.values(): spine.set_color(BORDER)
    fig.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close(fig)

section("Product & market performance")
p1,p2=st.columns(2)
products=data.groupby("product_name",as_index=False).agg(revenue=("total_amount","sum"),units=("quantity","sum")).sort_values("revenue",ascending=False).head(8).sort_values("revenue")
cities_sales=data.groupby("city",as_index=False)["total_amount"].sum().sort_values("total_amount").tail(8)
with p1:
    st.markdown('<div class="panel">**Top products by revenue**</div>',unsafe_allow_html=True)
    fig,ax=plt.subplots(figsize=(7,3.8)); fig.patch.set_facecolor(PANEL); ax.set_facecolor(PANEL)
    ax.barh(products["product_name"].astype(str),products["revenue"],color=PURPLE)
    ax.set_xlabel("Revenue (₹)",color="#94A3B8"); ax.tick_params(colors="#B6C2D5",labelsize=8); ax.grid(axis="x",color="#2A3650",alpha=.6); ax.grid(axis="y",visible=False)
    for spine in ax.spines.values(): spine.set_color(BORDER)
    fig.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close(fig)
with p2:
    st.markdown('<div class="panel">**Revenue by city**</div>',unsafe_allow_html=True)
    fig,ax=plt.subplots(figsize=(7,3.8)); fig.patch.set_facecolor(PANEL); ax.set_facecolor(PANEL)
    ax.barh(cities_sales["city"].astype(str),cities_sales["total_amount"],color=BLUE)
    ax.set_xlabel("Revenue (₹)",color="#94A3B8"); ax.tick_params(colors="#B6C2D5",labelsize=8); ax.grid(axis="x",color="#2A3650",alpha=.6); ax.grid(axis="y",visible=False)
    for spine in ax.spines.values(): spine.set_color(BORDER)
    fig.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close(fig)

section("Business insights")
top_category=data.groupby("category")["total_amount"].sum().idxmax() if data["category"].notna().any() else "N/A"
top_product=data.groupby("product_name")["total_amount"].sum().idxmax() if data["product_name"].notna().any() else "N/A"
top_city=data.groupby("city")["total_amount"].sum().idxmax() if data["city"].notna().any() else "N/A"
cat_rev=data.loc[data["category"]==top_category,"total_amount"].sum() if top_category!="N/A" else 0
city_rev=data.loc[data["city"]==top_city,"total_amount"].sum() if top_city!="N/A" else 0
share=cat_rev/revenue*100 if revenue else 0
insights=[
    ("TOP CATEGORY",top_category,f"{share:.1f}% of selected revenue"),
    ("TOP PRODUCT",top_product,"Highest revenue product"),
    ("LEADING CITY",top_city,f"{money(city_rev)} revenue"),
]
cols=st.columns(3)
for col,(label,value,note) in zip(cols,insights):
    with col:
        st.markdown(f'<div class="panel"><div class="panel-label">{label}</div><div style="font-family:Space Grotesk,sans-serif;font-size:1.2rem;font-weight:700;color:#F8FAFC;overflow-wrap:anywhere">{value}</div><div style="color:#94A3B8;font-size:.82rem;margin-top:8px">{note}</div></div>',unsafe_allow_html=True)

section("Customer performance")
customers_table=data.groupby(["customer_id","customer_name"],dropna=False,as_index=False).agg(revenue=("total_amount","sum"),orders=("order_id","nunique"),units=("quantity","sum")).sort_values("revenue",ascending=False).head(10)
st.dataframe(customers_table,use_container_width=True,hide_index=True,column_config={
    "revenue":st.column_config.NumberColumn("Revenue",format="₹%.2f"),
    "orders":st.column_config.NumberColumn("Orders",format="%d"),
    "units":st.column_config.NumberColumn("Units",format="%d"),
})
with st.expander("Explore detailed sales records"):
    search=st.text_input("Search order, customer, product, city or category",placeholder="Type a keyword...")
    detail=data.copy()
    if search.strip():
        cols_to_search=["order_id","customer_name","product_name","city","category","state"]
        mask=pd.Series(False,index=detail.index)
        for col in cols_to_search:
            mask |= detail[col].astype(str).str.contains(search.strip(),case=False,na=False,regex=False)
        detail=detail[mask]
    st.caption(f"{len(detail):,} matching records")
    st.dataframe(detail,use_container_width=True,hide_index=True)
    st.download_button("Download filtered sales CSV",data=detail.to_csv(index=False).encode("utf-8-sig"),file_name="sales_analytics_export.csv",mime="text/csv")
st.markdown('<div class="footer">SALES INTELLIGENCE · Connected through your existing MySQL query module · Data cache: 5 minutes</div>',unsafe_allow_html=True)
