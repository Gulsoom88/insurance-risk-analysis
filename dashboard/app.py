import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Page setup
st.set_page_config(
    page_title="Insurance Risk Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load data safely
BASE_DIR = Path(__file__).resolve().parent.parent
csv_path = BASE_DIR / "data" / "processed" / "insurance_clean.csv"

df = pd.read_csv(csv_path)

# Create images folder for README chart exports
images_path = BASE_DIR / "images"
images_path.mkdir(exist_ok=True)

st.title("Insurance Risk, Pricing & Customer Segmentation Dashboard")
st.write(
    "This dashboard analyzes customer risk, pricing patterns, claim history, "
    "and insurance customer segmentation."
)

# Sidebar filters
st.sidebar.header("Filters")

policy_filter = st.sidebar.multiselect(
    "Select Policy Type",
    options=df["policy_type"].unique(),
    default=df["policy_type"].unique()
)

risk_filter = st.sidebar.multiselect(
    "Select Risk Category",
    options=df["risk_category"].dropna().unique(),
    default=df["risk_category"].dropna().unique()
)

filtered_df = df[
    (df["policy_type"].isin(policy_filter)) &
    (df["risk_category"].isin(risk_filter))
]

# KPI section
st.subheader("Executive Overview")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Customers", f"{len(filtered_df):,}")
col2.metric("Avg Premium", f"{filtered_df['premium_amount'].mean():,.0f}")
col3.metric("Avg Coverage", f"{filtered_df['coverage_amount'].mean():,.0f}")
col4.metric("Avg Risk", f"{filtered_df['risk_profile'].mean():.2f}")
col5.metric("Avg Credit Score", f"{filtered_df['credit_score'].mean():.0f}")

st.divider()

# Risk analysis
st.subheader("Risk Analysis")

col1, col2 = st.columns(2)

with col1:
    risk_count = filtered_df["risk_category"].value_counts().reset_index()
    risk_count.columns = ["risk_category", "count"]

    fig = px.bar(
        risk_count,
        x="risk_category",
        y="count",
        title="Customer Count by Risk Category"
    )

    st.plotly_chart(fig, use_container_width=True)
    fig.write_image(images_path / "risk_distribution.png")

with col2:
    fig = px.box(
        filtered_df,
        x="risk_category",
        y="premium_amount",
        title="Premium Amount by Risk Category"
    )

    st.plotly_chart(fig, use_container_width=True)
    fig.write_image(images_path / "premium_by_risk.png")

# Pricing analysis
st.subheader("Pricing Analysis")

col1, col2 = st.columns(2)

with col1:
    pricing = filtered_df.groupby("policy_type", as_index=False).agg(
        avg_premium=("premium_amount", "mean"),
        avg_risk=("risk_profile", "mean"),
        avg_claim_history=("claim_history", "mean")
    )

    fig = px.bar(
        pricing,
        x="policy_type",
        y="avg_premium",
        color="avg_risk",
        title="Average Premium by Policy Type and Risk"
    )

    st.plotly_chart(fig, use_container_width=True)
    fig.write_image(images_path / "policy_risk_analysis.png")

with col2:
    sample_size = min(5000, len(filtered_df))

    fig = px.scatter(
        filtered_df.sample(sample_size, random_state=42),
        x="coverage_amount",
        y="premium_amount",
        color="risk_category",
        title="Coverage Amount vs Premium Amount",
        opacity=0.3
    )

    fig.update_traces(marker=dict(size=4))

    st.plotly_chart(fig, use_container_width=True)
    fig.write_image(images_path / "coverage_vs_premium.png")

# Claims behavior
st.subheader("Claims Behavior")

col1, col2 = st.columns(2)

with col1:
    claims_by_policy = filtered_df.groupby("policy_type", as_index=False).agg(
        avg_claim_history=("claim_history", "mean")
    )

    fig = px.bar(
        claims_by_policy,
        x="policy_type",
        y="avg_claim_history",
        title="Average Claim History by Policy Type"
    )

    st.plotly_chart(fig, use_container_width=True)
    fig.write_image(images_path / "claims_by_policy.png")

with col2:
    fig = px.box(
        filtered_df,
        x="risk_category",
        y="claim_history",
        title="Claim History by Risk Category"
    )

    st.plotly_chart(fig, use_container_width=True)
    fig.write_image(images_path / "claims_by_risk.png")

# Customer segmentation
st.subheader("Customer Segmentation")

col1, col2 = st.columns(2)

with col1:
    segment_analysis = filtered_df.groupby("segmentation_group", as_index=False).agg(
        customers=("customer_id", "count"),
        avg_premium=("premium_amount", "mean"),
        avg_risk=("risk_profile", "mean")
    )

    fig = px.bar(
        segment_analysis,
        x="segmentation_group",
        y="customers",
        color="avg_risk",
        title="Customer Segments by Size and Risk"
    )

    st.plotly_chart(fig, use_container_width=True)
    fig.write_image(images_path / "customer_segments.png")

with col2:
    sample_size = min(5000, len(filtered_df))

    fig = px.scatter(
        filtered_df.sample(sample_size, random_state=42),
        x="credit_score",
        y="claim_history",
        color="risk_category",
        title="Credit Score vs Claim History",
        opacity=0.6
    )

    st.plotly_chart(fig, use_container_width=True)
    fig.write_image(images_path / "credit_vs_claims.png")

# Age analysis
st.subheader("Age and Risk Analysis")

age_analysis = filtered_df.groupby("age_group", as_index=False).agg(
    avg_premium=("premium_amount", "mean"),
    avg_risk=("risk_profile", "mean"),
    avg_claim_history=("claim_history", "mean")
)

fig = px.line(
    age_analysis,
    x="age_group",
    y=["avg_premium", "avg_risk", "avg_claim_history"],
    markers=True,
    title="Premium, Risk, and Claim History by Age Group"
)

st.plotly_chart(fig, use_container_width=True)
fig.write_image(images_path / "age_group_analysis.png")

# Business insights
st.subheader("Business Insights")

highest_risk_policy = pricing.sort_values("avg_risk", ascending=False).iloc[0]
highest_claim_policy = claims_by_policy.sort_values("avg_claim_history", ascending=False).iloc[0]

st.write(f"""
### Key Findings

1. The policy type with the highest average risk is **{highest_risk_policy['policy_type']}**.
2. The policy type with the highest average claim history is **{highest_claim_policy['policy_type']}**.
3. Average premium across selected customers is **{filtered_df['premium_amount'].mean():,.0f}**.
4. Average risk profile across selected customers is **{filtered_df['risk_profile'].mean():.2f}**.
5. Credit score and claim history can be used together to support customer risk segmentation.

### Business Recommendations

- Review pricing for high-risk policy groups.
- Monitor customers with high claim history and low premium levels.
- Use risk category, credit score, and claim history together for better customer segmentation.
- Build a predictive model to estimate customer risk and expected claims.
""")

# Data preview
with st.expander("View Filtered Data"):
    st.dataframe(filtered_df)