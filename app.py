
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(page_title="FinanceFlow", page_icon="💰", layout="wide")

st.markdown("""
<style>
.main {background-color:#0F172A;}
.metric-card{
    background:#1E293B;
    padding:20px;
    border-radius:15px;
    border:1px solid #334155;
}
h1,h2,h3{color:white;}
</style>
""", unsafe_allow_html=True)

DATA_FILE = "transactions.csv"

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date","Title","Category","Type","Amount"]).to_csv(DATA_FILE,index=False)

def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE,index=False)

st.title("💰 FinanceFlow")
st.caption("Professional Expense Analytics Dashboard")

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard","Add Transaction","Transactions","Analytics"]
)

df = load_data()

if menu == "Add Transaction":
    st.header("Add Transaction")

    with st.form("txn"):
        date = st.date_input("Date")
        title = st.text_input("Title")
        category = st.selectbox("Category",
                                ["Food","Travel","Shopping","Education",
                                 "Entertainment","Bills","Other"])
        ttype = st.selectbox("Type",["Income","Expense"])
        amount = st.number_input("Amount",min_value=0.0)
        submit = st.form_submit_button("Save")

        if submit:
            new_row = pd.DataFrame([{
                "Date":date,
                "Title":title,
                "Category":category,
                "Type":ttype,
                "Amount":amount
            }])
            df = pd.concat([df,new_row],ignore_index=True)
            save_data(df)
            st.success("Transaction Added!")

elif menu == "Transactions":
    st.header("Transaction History")

    if len(df):
        search = st.text_input("Search")
        filtered = df[df["Title"].astype(str).str.contains(search, case=False, na=False)]
        st.dataframe(filtered, use_container_width=True)

        st.download_button(
            "Download CSV",
            filtered.to_csv(index=False),
            "financeflow_report.csv",
            "text/csv"
        )
    else:
        st.info("No transactions yet")

elif menu == "Analytics":
    st.header("Analytics")

    if len(df):
        expense_df = df[df["Type"]=="Expense"]

        if len(expense_df):
            pie = px.pie(
                expense_df,
                names="Category",
                values="Amount",
                title="Expense Distribution"
            )
            st.plotly_chart(pie, use_container_width=True)

            bar = px.bar(
                expense_df.groupby("Category",as_index=False)["Amount"].sum(),
                x="Category",
                y="Amount",
                title="Category Spending"
            )
            st.plotly_chart(bar, use_container_width=True)

        try:
            df["Date"] = pd.to_datetime(df["Date"])
            monthly = df.groupby(df["Date"].dt.strftime("%Y-%m"))["Amount"].sum().reset_index()
            line = px.line(monthly,x="Date",y="Amount",title="Monthly Trend")
            st.plotly_chart(line,use_container_width=True)
        except:
            pass

else:
    st.header("Dashboard")

    income = df[df["Type"]=="Income"]["Amount"].sum() if len(df) else 0
    expense = df[df["Type"]=="Expense"]["Amount"].sum() if len(df) else 0
    balance = income - expense
    savings = (balance/income*100) if income else 0

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Income", f"₹{income:,.0f}")
    c2.metric("Expense", f"₹{expense:,.0f}")
    c3.metric("Balance", f"₹{balance:,.0f}")
    c4.metric("Savings %", f"{savings:.1f}%")

    st.subheader("Recent Transactions")
    st.dataframe(df.tail(10), use_container_width=True)

    if len(df):
        expense_df = df[df["Type"]=="Expense"]
        if len(expense_df):
            chart = px.pie(expense_df,names="Category",values="Amount")
            st.plotly_chart(chart,use_container_width=True)
