import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Nassau Candy | Business Analytics",
    page_icon="🍫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# PROFESSIONAL CHOCOLATE THEME
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

.stApp {
    background: #FAF8F5;
    font-family: 'DM Sans', sans-serif;
}
.block-container {
    padding-top: 1.4rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}
h1, h2, h3 {
    color: #4B2E2B;
}
.hero {
    background: linear-gradient(120deg, #30201E, #67453B, #A8754D);
    padding: 28px 30px;
    border-radius: 18px;
    color: white;
    margin-bottom: 22px;
}
.hero h1 {
    font-family: 'Playfair Display', serif;
    color: white !important;
    font-size: 2.25rem;
    margin: 5px 0;
}
.hero p {
    color: #F4E8DD;
    margin-bottom: 0;
}
.eyebrow {
    color: #F1C99E;
    letter-spacing: 2px;
    font-size: 12px;
    font-weight: 700;
}
.kpi {
    background: white;
    border: 1px solid #E9DFD5;
    border-radius: 15px;
    padding: 17px;
    min-height: 115px;
    box-shadow: 0 3px 12px rgba(61,42,34,.04);
}
.kpi-label {
    color: #84756D;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: .5px;
}
.kpi-value {
    color: #4B2E2B;
    font-size: 25px;
    font-weight: 700;
    margin-top: 7px;
}
.kpi-note {
    color: #A07858;
    font-size: 11px;
    margin-top: 5px;
}
.section-title {
    font-family: 'Playfair Display', serif;
    color: #4B2E2B;
    font-size: 22px;
    font-weight: 700;
    margin-top: 12px;
}
.section-subtitle {
    color: #81736B;
    font-size: 13px;
    margin-bottom: 12px;
}
.insight {
    background: white;
    border: 1px solid #E9DFD5;
    border-left: 4px solid #B77945;
    border-radius: 12px;
    padding: 15px;
    min-height: 100px;
}
.insight-label {
    color: #9A6E49;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 7px;
}
.insight-value {
    color: #49332D;
    font-size: 14px;
    font-weight: 600;
}
[data-testid="stSidebar"] {
    background: #F0E9E2;
    border-right: 1px solid #E4D8CC;
}
[data-testid="stTabs"] button {
    font-weight: 600;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #E9DFD5;
    border-radius: 10px;
}
.stDownloadButton button {
    background: #4B2E2B;
    color: white;
    border-radius: 8px;
    border: none;
}
.stDownloadButton button:hover {
    background: #704A3F;
    color: white;
}
.footer {
    color: #897C74;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD AND PREPARE DATA
# =========================================================
@st.cache_data
def load_data():
    base = Path(__file__).resolve().parent

    paths = [
        base / "Dataset" / "Nassau Candy Distributor.csv",
        base / "Nassau Candy Distributor.csv",
        Path.cwd() / "Dataset" / "Nassau Candy Distributor.csv",
        Path.cwd() / "Nassau Candy Distributor.csv",
    ]

    csv_path = next((p for p in paths if p.exists()), None)

    if csv_path is None:
        raise FileNotFoundError(
            "Dataset not found. Place Nassau Candy Distributor.csv "
            "inside the Dataset folder beside app.py."
        )

    data = pd.read_csv(csv_path)
    data.columns = data.columns.str.strip()

    required = ["Sales", "Cost", "Gross Profit", "Units",
                "Product Name", "Division"]

    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError(
            "Required columns missing from CSV: " + ", ".join(missing)
        )

    for col in ["Sales", "Cost", "Gross Profit", "Units"]:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)

    for col in ["Product Name", "Division"]:
        data[col] = data[col].fillna("Unknown").astype(str).str.strip()

    if "Order Date" in data.columns:
        data["Order Date"] = pd.to_datetime(
            data["Order Date"], errors="coerce"
        )
    else:
        data["Order Date"] = pd.NaT

    if "Order ID" not in data.columns:
        data["Order ID"] = np.arange(len(data)).astype(str)

    factory_map = {
        "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
        "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
        "Wonka Bar -Scrumdiddlyumptious": "Lot's O' Nuts",
        "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
        "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
        "Laffy Taffy": "Sugar Shack",
        "SweeTARTS": "Sugar Shack",
        "Nerds": "Sugar Shack",
        "Fun Dip": "Sugar Shack",
        "Everlasting Gobstopper": "Secret Factory",
        "Hair Toffee": "The Other Factory",
        "Fizzy Lifting Drinks": "Sugar Shack",
        "Lickable Wallpaper": "Secret Factory",
        "Wonka Gum": "Secret Factory",
        "Kazookles": "The Other Factory"
    }

    data["Factory"] = data["Product Name"].map(factory_map).fillna("Not Mapped")

    data["Gross Margin %"] = np.where(
        data["Sales"] > 0,
        data["Gross Profit"] / data["Sales"] * 100,
        np.nan
    )

    data["Profit per Unit"] = np.where(
        data["Units"] > 0,
        data["Gross Profit"] / data["Units"],
        np.nan
    )

    data["Cost Ratio %"] = np.where(
        data["Sales"] > 0,
        data["Cost"] / data["Sales"] * 100,
        np.nan
    )

    return data


try:
    df = load_data()
except Exception as e:
    st.error("Unable to load the dataset.")
    st.write("Check the dataset location and column names.")
    st.code(str(e))
    st.stop()


# =========================================================
# HELPER FUNCTIONS
# =========================================================
def money(value):
    return f"${value:,.2f}" if pd.notna(value) else "—"


def percentage(value):
    return f"{value:.2f}%" if pd.notna(value) else "—"


def kpi(label, value, note):
    st.markdown(f"""
    <div class="kpi">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)


def insight(label, value):
    st.markdown(f"""
    <div class="insight">
        <div class="insight-label">{label}</div>
        <div class="insight-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def section(title, subtitle=""):
    st.markdown(f'<div class="section-title">{title}</div>',
                unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-subtitle">{subtitle}</div>',
                    unsafe_allow_html=True)


def chart_layout(fig, height=350):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=25, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#4B3A34"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1)
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#EEE7E0")
    return fig


# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## 🍫 Nassau Candy")
st.sidebar.caption("Product Profitability Analytics")
st.sidebar.divider()

st.sidebar.markdown("### Dashboard Filters")

filtered = df.copy()

if df["Order Date"].notna().any():
    min_date = df["Order Date"].min().date()
    max_date = df["Order Date"].max().date()

    date_range = st.sidebar.date_input(
        "Order date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start = pd.Timestamp(date_range[0])
        end = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
        filtered = filtered[
            (filtered["Order Date"] >= start) &
            (filtered["Order Date"] < end)
        ]

divisions = sorted(df["Division"].unique().tolist())
selected_divisions = st.sidebar.multiselect(
    "Division",
    divisions,
    default=divisions
)

filtered = filtered[filtered["Division"].isin(selected_divisions)]

search = st.sidebar.text_input("Search product", placeholder="Type product name")
if search.strip():
    filtered = filtered[
        filtered["Product Name"].str.contains(search.strip(), case=False, na=False)
    ]

threshold = st.sidebar.slider(
    "Low-margin threshold (%)", 0, 70, 30, 5
)

ranking = st.sidebar.selectbox(
    "Product ranking metric",
    ["Gross Profit", "Sales", "Gross Margin %", "Profit per Unit"]
)

st.sidebar.divider()
st.sidebar.caption(f"Records loaded: {len(df):,}")
st.sidebar.caption(f"Products: {df['Product Name'].nunique():,}")
st.sidebar.caption(f"Divisions: {df['Division'].nunique():,}")


# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="hero">
    <div class="eyebrow">BUSINESS INTELLIGENCE · PROFITABILITY ANALYSIS</div>
    <h1>Nassau Candy Distributor</h1>
    <p>Product Line Profitability & Margin Performance Dashboard</p>
</div>
""", unsafe_allow_html=True)

if filtered.empty:
    st.warning("No records match the selected filters. Change your filters and try again.")
    st.stop()


# =========================================================
# KPI CALCULATIONS
# =========================================================
sales = filtered["Sales"].sum()
cost = filtered["Cost"].sum()
profit = filtered["Gross Profit"].sum()
units = filtered["Units"].sum()
margin = profit / sales * 100 if sales else np.nan
profit_unit = profit / units if units else np.nan
orders = filtered["Order ID"].nunique()
average_order = sales / orders if orders else 0

cols = st.columns(5)
with cols[0]:
    kpi("TOTAL SALES", money(sales), "Revenue in selected view")
with cols[1]:
    kpi("GROSS PROFIT", money(profit), "Sales minus cost")
with cols[2]:
    kpi("GROSS MARGIN", percentage(margin), "Profit / sales")
with cols[3]:
    kpi("UNITS SOLD", f"{units:,.0f}", "Total units")
with cols[4]:
    kpi("PROFIT PER UNIT", money(profit_unit), f"Avg. order: {money(average_order)}")


# =========================================================
# SUMMARY TABLES
# =========================================================
products = (
    filtered.groupby(["Product Name", "Division", "Factory"], as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        **{"Gross Profit": ("Gross Profit", "sum")},
        Units=("Units", "sum")
    )
)

products["Gross Margin %"] = np.where(
    products["Sales"] > 0,
    products["Gross Profit"] / products["Sales"] * 100,
    np.nan
)
products["Profit per Unit"] = np.where(
    products["Units"] > 0,
    products["Gross Profit"] / products["Units"],
    np.nan
)
products["Cost Ratio %"] = np.where(
    products["Sales"] > 0,
    products["Cost"] / products["Sales"] * 100,
    np.nan
)
products["Revenue Contribution %"] = (
    products["Sales"] / sales * 100 if sales else 0
)
products["Profit Contribution %"] = (
    products["Gross Profit"] / profit * 100 if profit else 0
)

profit_median = products["Gross Profit"].median()
margin_median = products["Gross Margin %"].median()

def portfolio(row):
    high_profit = row["Gross Profit"] >= profit_median
    high_margin = pd.notna(row["Gross Margin %"]) and row["Gross Margin %"] >= margin_median

    if high_profit and high_margin:
        return "High Profit / High Margin"
    if high_profit:
        return "High Profit / Lower Margin"
    if high_margin:
        return "Lower Profit / High Margin"
    return "Lower Profit / Lower Margin"

products["Portfolio Segment"] = products.apply(portfolio, axis=1)

divisions_summary = (
    filtered.groupby("Division", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        **{"Gross Profit": ("Gross Profit", "sum")},
        Units=("Units", "sum")
    )
)
divisions_summary["Gross Margin %"] = np.where(
    divisions_summary["Sales"] > 0,
    divisions_summary["Gross Profit"] / divisions_summary["Sales"] * 100,
    np.nan
)


# =========================================================
# DASHBOARD TABS
# =========================================================
overview, division_tab, cost_tab, pareto_tab, explorer_tab = st.tabs([
    "📊 Overview",
    "🏢 Division Performance",
    "⚖️ Cost & Margin",
    "📈 Profit Concentration",
    "🔎 Product Explorer"
])


# =========================================================
# OVERVIEW TAB
# =========================================================
with overview:
    left, right = st.columns([1.25, 1])

    with left:
        section("Top Products by Gross Profit",
                "Products contributing the most total profit.")

        top = products.nlargest(10, "Gross Profit").sort_values("Gross Profit")

        fig = px.bar(
            top,
            x="Gross Profit",
            y="Product Name",
            orientation="h",
            color="Gross Profit",
            color_continuous_scale=["#D8B79A", "#4B2E2B"],
            hover_data=["Sales", "Gross Margin %"]
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(chart_layout(fig, 390), width="stretch")

    with right:
        section("Product Portfolio",
                "Product count across profit and margin groups.")

        mix = products["Portfolio Segment"].value_counts().reset_index()
        mix.columns = ["Segment", "Products"]

        fig = px.pie(
            mix,
            names="Segment",
            values="Products",
            hole=0.58,
            color_discrete_sequence=[
                "#4B2E2B", "#A66B45", "#D6B48E", "#E7DCD1"
            ]
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(chart_layout(fig, 390), width="stretch")

    section("Business Highlights", "Quick insights from the current filters.")

    best_profit = products.loc[products["Gross Profit"].idxmax()]
    valid_margin = products.dropna(subset=["Gross Margin %"])
    best_margin = valid_margin.loc[valid_margin["Gross Margin %"].idxmax()] if not valid_margin.empty else None
    low_margin_count = (
        (products["Gross Margin %"] < threshold) &
        (products["Sales"] > 0)
    ).sum()
    best_division = divisions_summary.loc[
        divisions_summary["Gross Profit"].idxmax()
    ] if not divisions_summary.empty else None

    c = st.columns(4)
    with c[0]:
        insight("Top profit product",
                f"{best_profit['Product Name']} · {money(best_profit['Gross Profit'])}")
    with c[1]:
        insight("Highest margin product",
                f"{best_margin['Product Name']} · {percentage(best_margin['Gross Margin %'])}"
                if best_margin is not None else "No margin data")
    with c[2]:
        insight("Margin watchlist",
                f"{low_margin_count} product(s) below {threshold}%")
    with c[3]:
        insight("Leading division",
                f"{best_division['Division']} · {money(best_division['Gross Profit'])}"
                if best_division is not None else "No division data")

    section("Monthly Sales & Profit Trend",
            "Track how sales and gross profit change over time.")

    dated = filtered.dropna(subset=["Order Date"]).copy()

    if not dated.empty:
        dated["Month"] = dated["Order Date"].dt.to_period("M").astype(str)
        monthly = dated.groupby("Month", as_index=False).agg(
            Sales=("Sales", "sum"),
            **{"Gross Profit": ("Gross Profit", "sum")}
        )
        monthly_long = monthly.melt(
            id_vars="Month",
            value_vars=["Sales", "Gross Profit"],
            var_name="Metric",
            value_name="Amount"
        )

        fig = px.line(
            monthly_long,
            x="Month",
            y="Amount",
            color="Metric",
            markers=True,
            color_discrete_map={
                "Sales": "#B98A63",
                "Gross Profit": "#4B2E2B"
            }
        )
        st.plotly_chart(chart_layout(fig, 320), width="stretch")
    else:
        st.info("Monthly trends are unavailable because valid order dates were not found.")


# =========================================================
# DIVISION PERFORMANCE TAB
# =========================================================
with division_tab:
    section("Division Performance",
            "Compare sales, gross profit, and gross margin by division.")

    if not divisions_summary.empty:
        left, right = st.columns(2)

        with left:
            long_div = divisions_summary.melt(
                id_vars="Division",
                value_vars=["Sales", "Gross Profit"],
                var_name="Metric",
                value_name="Amount"
            )
            fig = px.bar(
                long_div,
                x="Division",
                y="Amount",
                color="Metric",
                barmode="group",
                color_discrete_map={
                    "Sales": "#C69A75",
                    "Gross Profit": "#4B2E2B"
                }
            )
            st.plotly_chart(chart_layout(fig, 360), width="stretch")

        with right:
            fig = px.bar(
                divisions_summary.sort_values("Gross Margin %"),
                x="Gross Margin %",
                y="Division",
                orientation="h",
                text="Gross Margin %",
                color="Gross Margin %",
                color_continuous_scale=["#D9BDA5", "#4B2E2B"]
            )
            fig.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
                cliponaxis=False
            )
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(chart_layout(fig, 360), width="stretch")

        st.dataframe(
            divisions_summary.style.format({
                "Sales": "${:,.2f}",
                "Cost": "${:,.2f}",
                "Gross Profit": "${:,.2f}",
                "Gross Margin %": "{:.2f}%",
                "Units": "{:,.0f}"
            }),
            width="stretch",
            hide_index=True
        )


# =========================================================
# COST AND MARGIN TAB
# =========================================================
with cost_tab:
    section("Cost & Margin Diagnostics",
            "Find products whose margins may need management attention.")

    risk = products[
        (products["Sales"] > 0) &
        (products["Gross Margin %"] < threshold)
    ].sort_values("Gross Margin %")

    a, b, c = st.columns(3)
    with a:
        kpi("PRODUCTS AT RISK", f"{len(risk)}", f"Below {threshold}% margin")
    with b:
        kpi("RISK-GROUP SALES", money(risk["Sales"].sum()), "Sales from flagged products")
    with c:
        kpi("RISK-GROUP PROFIT", money(risk["Gross Profit"].sum()), "Profit from flagged products")

    left, right = st.columns(2)

    with left:
        section("Cost vs Sales",
                "Products closer to the diagonal have costs closer to sales.")

        fig = px.scatter(
            products,
            x="Sales",
            y="Cost",
            size="Units",
            color="Gross Margin %",
            hover_name="Product Name",
            hover_data=["Gross Profit", "Division"],
            color_continuous_scale=["#B45D4C", "#D9B98C", "#4B2E2B"]
        )

        max_value = max(
            float(products["Sales"].max()),
            float(products["Cost"].max()),
            1
        )
        fig.add_trace(go.Scatter(
            x=[0, max_value],
            y=[0, max_value],
            mode="lines",
            name="Cost = Sales",
            line=dict(color="#8A7770", dash="dash")
        ))
        st.plotly_chart(chart_layout(fig, 370), width="stretch")

    with right:
        section("Margin by Product",
                "The dashed line marks your selected margin threshold.")

        margin_data = products.dropna(subset=["Gross Margin %"]).sort_values("Gross Margin %")

        if not margin_data.empty:
            fig = px.bar(
                margin_data,
                x="Gross Margin %",
                y="Product Name",
                orientation="h",
                color="Gross Margin %",
                color_continuous_scale=["#B45D4C", "#D9B98C", "#4B2E2B"]
            )
            fig.add_vline(
                x=threshold,
                line_dash="dash",
                line_color="#B45D4C",
                annotation_text=f"{threshold}% threshold"
            )
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(chart_layout(fig, 370), width="stretch")
        else:
            st.info("No margin values available.")

    section("Margin Watchlist",
            "Consider reviewing pricing, sourcing costs, or product positioning.")

    if not risk.empty:
        st.dataframe(
            risk[[
                "Product Name", "Division", "Factory", "Sales", "Cost",
                "Gross Profit", "Gross Margin %", "Profit per Unit"
            ]].style.format({
                "Sales": "${:,.2f}",
                "Cost": "${:,.2f}",
                "Gross Profit": "${:,.2f}",
                "Gross Margin %": "{:.2f}%",
                "Profit per Unit": "${:,.2f}"
            }),
            width="stretch",
            hide_index=True
        )
    else:
        st.success("No products fall below the selected margin threshold.")


# =========================================================
# PROFIT CONCENTRATION / PARETO TAB
# =========================================================
with pareto_tab:
    section("Profit Concentration Analysis",
            "Measure how much sales and profit depend on a small group of products.")

    def pareto_table(data, metric):
        result = data.groupby("Product Name", as_index=False)[metric].sum()
        result = result.sort_values(metric, ascending=False).reset_index(drop=True)
        total_value = result[metric].sum()

        if total_value != 0:
            result["Contribution %"] = result[metric] / total_value * 100
        else:
            result["Contribution %"] = 0

        result["Cumulative %"] = result["Contribution %"].cumsum()
        return result

    def products_to_80(table):
        if table.empty:
            return 0
        reached = np.flatnonzero(table["Cumulative %"].to_numpy() >= 80)
        return int(reached[0] + 1) if len(reached) else len(table)

    revenue_pareto = pareto_table(filtered, "Sales")
    profit_pareto = pareto_table(filtered, "Gross Profit")

    a, b = st.columns(2)
    with a:
        kpi("PRODUCTS FOR 80% OF SALES",
            str(products_to_80(revenue_pareto)),
            "Products ranked by sales")
    with b:
        kpi("PRODUCTS FOR 80% OF PROFIT",
            str(products_to_80(profit_pareto)),
            "Products ranked by profit")

    left, right = st.columns(2)

    with left:
        section("Revenue Pareto")
        if not revenue_pareto.empty:
            fig = go.Figure()
            fig.add_bar(
                x=revenue_pareto["Product Name"],
                y=revenue_pareto["Sales"],
                name="Sales",
                marker_color="#B98A63"
            )
            fig.add_scatter(
                x=revenue_pareto["Product Name"],
                y=revenue_pareto["Cumulative %"],
                name="Cumulative %",
                yaxis="y2",
                mode="lines+markers",
                line=dict(color="#4B2E2B", width=3)
            )
            fig.add_hline(y=80, line_dash="dash", line_color="#B45D4C", yref="y2")
            fig.update_layout(
                height=380,
                margin=dict(l=10, r=10, t=25, b=90),
                paper_bgcolor="white",
                plot_bgcolor="white",
                xaxis=dict(tickangle=-45),
                yaxis=dict(title="Sales ($)"),
                yaxis2=dict(title="Cumulative (%)", overlaying="y",
                            side="right", range=[0, 105], ticksuffix="%")
            )
            st.plotly_chart(fig, width="stretch")

    with right:
        section("Profit Pareto")
        if not profit_pareto.empty:
            fig = go.Figure()
            fig.add_bar(
                x=profit_pareto["Product Name"],
                y=profit_pareto["Gross Profit"],
                name="Gross Profit",
                marker_color="#6A443C"
            )
            fig.add_scatter(
                x=profit_pareto["Product Name"],
                y=profit_pareto["Cumulative %"],
                name="Cumulative %",
                yaxis="y2",
                mode="lines+markers",
                line=dict(color="#C58C57", width=3)
            )
            fig.add_hline(y=80, line_dash="dash", line_color="#B45D4C", yref="y2")
            fig.update_layout(
                height=380,
                margin=dict(l=10, r=10, t=25, b=90),
                paper_bgcolor="white",
                plot_bgcolor="white",
                xaxis=dict(tickangle=-45),
                yaxis=dict(title="Gross profit ($)"),
                yaxis2=dict(title="Cumulative (%)", overlaying="y",
                            side="right", range=[0, 105], ticksuffix="%")
            )
            st.plotly_chart(fig, width="stretch")

    choice = st.radio(
        "View contribution table",
        ["Sales", "Gross Profit"],
        horizontal=True
    )
    table = revenue_pareto if choice == "Sales" else profit_pareto
    st.dataframe(
        table.style.format({
            choice: "${:,.2f}",
            "Contribution %": "{:.2f}%",
            "Cumulative %": "{:.2f}%"
        }),
        width="stretch",
        hide_index=True
    )


# =========================================================
# PRODUCT EXPLORER TAB
# =========================================================
with explorer_tab:
    section("Product Explorer",
            "Rank products, inspect profitability, and review factory mapping.")

    ranked = products.sort_values(ranking, ascending=False, na_position="last")

    number = st.selectbox(
        "Number of products to display",
        [5, 10, 15, 20, 50],
        index=2
    )

    columns_to_show = [
        "Product Name", "Division", "Factory", "Sales", "Cost",
        "Gross Profit", "Gross Margin %", "Units", "Profit per Unit",
        "Revenue Contribution %", "Profit Contribution %", "Portfolio Segment"
    ]

    st.dataframe(
        ranked[columns_to_show].head(number).style.format({
            "Sales": "${:,.2f}",
            "Cost": "${:,.2f}",
            "Gross Profit": "${:,.2f}",
            "Gross Margin %": "{:.2f}%",
            "Units": "{:,.0f}",
            "Profit per Unit": "${:,.2f}",
            "Revenue Contribution %": "{:.2f}%",
            "Profit Contribution %": "{:.2f}%"
        }),
        width="stretch",
        hide_index=True
    )

    st.download_button(
        "⬇️ Download Product Analysis CSV",
        data=ranked.to_csv(index=False).encode("utf-8"),
        file_name="nassau_candy_profitability.csv",
        mime="text/csv"
    )

    st.divider()

    selected_product = st.selectbox(
        "Select a product to inspect",
        ranked["Product Name"].tolist()
    )

    selected = ranked[ranked["Product Name"] == selected_product].iloc[0]

    a, b, c, d = st.columns(4)
    with a:
        kpi("PRODUCT SALES", money(selected["Sales"]), selected["Division"])
    with b:
        kpi("GROSS PROFIT", money(selected["Gross Profit"]), "Selected product")
    with c:
        kpi("GROSS MARGIN", percentage(selected["Gross Margin %"]), "Selected product")
    with d:
        kpi("FACTORY", selected["Factory"], "Mapped manufacturing site")

    history_data = filtered[
        filtered["Product Name"] == selected_product
    ].dropna(subset=["Order Date"]).copy()

    if not history_data.empty:
        history_data["Month"] = history_data["Order Date"].dt.to_period("M").astype(str)
        history = history_data.groupby("Month", as_index=False).agg(
            Sales=("Sales", "sum"),
            **{"Gross Profit": ("Gross Profit", "sum")}
        )
        history_long = history.melt(
            id_vars="Month",
            value_vars=["Sales", "Gross Profit"],
            var_name="Metric",
            value_name="Amount"
        )

        section("Selected Product: Monthly Performance")
        fig = px.line(
            history_long,
            x="Month",
            y="Amount",
            color="Metric",
            markers=True,
            color_discrete_map={
                "Sales": "#B98A63",
                "Gross Profit": "#4B2E2B"
            }
        )
        st.plotly_chart(chart_layout(fig, 300), width="stretch")
    else:
        st.info("No valid order dates are available for this product's trend.")


# =========================================================
# FOOTER
# =========================================================
st.divider()
st.markdown("""
<div class="footer">
Nassau Candy Distributor · Product Line Profitability & Margin Performance Analysis
<br>
Built with Streamlit, Pandas and Plotly
</div>
""", unsafe_allow_html=True)