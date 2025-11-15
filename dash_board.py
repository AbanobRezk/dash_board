import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Auto Dashboard", layout="wide")

st.title("Financial Dashboard")
uploaded = st.file_uploader("Upload your dataset", type=["xlsx", "csv"])

if uploaded is not None:
    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

    st.dataframe(df.head())

    # Auto-detect date columns
    for col in df.columns:
        if "date" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass

    # Sidebar filters
    st.sidebar.header("Filters")

    for col in df.select_dtypes(include="object").columns:
        unique_vals = df[col].dropna().unique()
        if len(unique_vals) <= 100:
            selection = st.sidebar.multiselect(col, unique_vals, default=unique_vals)
            df = df[df[col].isin(selection)]

    for col in df.select_dtypes(include="datetime").columns:
        min_d, max_d = df[col].min(), df[col].max()
        date_range = st.sidebar.date_input(col, [min_d, max_d])
        if len(date_range) == 2:
            df = df[(df[col] >= pd.to_datetime(date_range[0])) &
                    (df[col] <= pd.to_datetime(date_range[1]))]

    numeric_cols = df.select_dtypes(include=["float", "int"]).columns

    # KPIs
    st.subheader("KPIs")
    kpi_cols = st.columns(4)

    kpi_cols[0].metric("Total Rows", len(df))
    if "Amount" in df.columns:
        kpi_cols[1].metric("Total Amount", f"{df['Amount'].sum():,.2f}")
        kpi_cols[2].metric("Avg Amount", f"{df['Amount'].mean():,.2f}")
    if "Fee" in df.columns:
        kpi_cols[3].metric("Total Fee", f"{df['Fee'].sum():,.2f}")

    # Charts
    st.subheader("Charts")

    if "Payment Entity" in df.columns and "Amount" in df.columns:
        fig1 = px.bar(df.groupby("Payment Entity")["Amount"].sum().reset_index(),
                      x="Payment Entity", y="Amount")
        st.plotly_chart(fig1, use_container_width=True)

    date_columns = df.select_dtypes(include="datetime").columns
    if len(date_columns) > 0 and "Amount" in df.columns:
        date_col = date_columns[0]
        fig2 = px.line(df.groupby(date_col)["Amount"].sum().reset_index(),
                       x=date_col, y="Amount")
        st.plotly_chart(fig2, use_container_width=True)

    if "Amount" in df.columns and "Fee" in df.columns:
        fig3 = px.scatter(df, x="Amount", y="Fee")
        st.plotly_chart(fig3, use_container_width=True)
        
