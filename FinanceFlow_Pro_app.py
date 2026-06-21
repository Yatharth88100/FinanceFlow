
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

st.set_page_config(page_title="FinanceFlow Pro", page_icon="💸", layout="wide")

# ---------- CSS ----------
st.markdown("""
<style>
.stApp{
background: radial-gradient(circle at top left,#0f172a,#020617 60%);
color:white;
}
[data-testid="stSidebar"]{
background: linear-gradient(180deg,#0b1020,#111c44);
border-right:1px solid rgba(255,255,255,0.1);
}
.hero{
padding:20px;
border-radius:24px;
background:rgba(255,255,255,0.05);
backdrop-filter:blur(10px);
border:1px solid rgba(255,255,255,0.08);
}
.metric-card{
padding:20px;
border-radius:22px;
background:linear-gradient(135deg,rgba(99,102,241,.15),rgba(236,72,153,.15));
border:1px solid rgba(255,255,255,.08);
box-shadow:0 0 25px rgba(99,102,241,.2);
text-align:center;
}
.bigtitle{
font-size:52px;
font-weight:800;
background:linear-gradient(90deg,#ffffff,#a855f7,#ec4899);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
}
.section{
padding:25px;
border-radius:24px;
background:rgba(255,255,255,.04);
border:1px solid rgba(255,255,255,.08);
margin-top:15px;
}
</style>
""", unsafe_allow_html=True)

FILE="transactions.csv"
if not os.path.exists(FILE):
    pd.DataFrame(columns=["Date","Title","Category","Type","Amount"]).to_csv(FILE,index=False)

def load():
    return pd.read_csv(FILE)

def save(df):
    df.to_csv(FILE,index=False)

df=load()

st.sidebar.markdown("## 💸 FinanceFlow")
st.sidebar.caption("Smart Money, Better Future")
page=st.sidebar.radio("Navigation",
["Dashboard","Add Transaction","Transactions","Analytics"])

if page=="Dashboard":
    income=df[df["Type"]=="Income"]["Amount"].sum() if len(df) else 0
    expense=df[df["Type"]=="Expense"]["Amount"].sum() if len(df) else 0
    balance=income-expense
    save_rate=(balance/income*100) if income else 0

    st.markdown('<div class="bigtitle">FinanceFlow</div>',unsafe_allow_html=True)
    st.caption("Premium Personal Finance Dashboard")

    c1,c2,c3,c4=st.columns(4)
    cards=[("💚 Total Income",income),("❤️ Total Expense",expense),("💙 Balance",balance),("🎯 Savings %",save_rate)]
    for col,(t,v) in zip([c1,c2,c3,c4],cards):
        with col:
            st.markdown(f'<div class="metric-card"><h4>{t}</h4><h2>₹{v:,.0f}</h2></div>',unsafe_allow_html=True)

    st.markdown("### Recent Transactions")
    st.dataframe(df.tail(10),use_container_width=True)

elif page=="Add Transaction":
    st.markdown('<div class="bigtitle">Add Transaction</div>',unsafe_allow_html=True)

    with st.container():
        date=st.date_input("Date")
        title=st.text_input("Title")
        col1,col2=st.columns(2)
        with col1:
            category=st.selectbox("Category",
            ["Food","Travel","Shopping","Education","Bills","Entertainment","Other"])
        with col2:
            typ=st.selectbox("Type",["Income","Expense"])

        amount=st.number_input("Amount",0.0)
        notes=st.text_area("Notes")

        if st.button("✨ Add Transaction",use_container_width=True):
            new=pd.DataFrame([{
                "Date":date,
                "Title":title,
                "Category":category,
                "Type":typ,
                "Amount":amount
            }])
            df=pd.concat([df,new],ignore_index=True)
            save(df)
            st.success("Transaction Added Successfully")

elif page=="Transactions":
    st.markdown('<div class="bigtitle">Transactions</div>',unsafe_allow_html=True)
    search=st.text_input("Search")
    filtered=df[df["Title"].astype(str).str.contains(search,case=False,na=False)]
    st.dataframe(filtered,use_container_width=True)
    st.download_button("⬇ Download CSV",
                       filtered.to_csv(index=False),
                       "FinanceFlow_Report.csv")

elif page=="Analytics":
    st.markdown('<div class="bigtitle">Analytics</div>',unsafe_allow_html=True)

    if len(df):
        exp=df[df["Type"]=="Expense"]

        col1,col2=st.columns(2)

        with col1:
            if len(exp):
                pie=px.pie(exp,names="Category",values="Amount",
                           hole=.55,title="Expense Distribution")
                pie.update_layout(paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(pie,use_container_width=True)

        with col2:
            if len(exp):
                bar=px.bar(exp.groupby("Category",as_index=False)["Amount"].sum(),
                           x="Category",y="Amount",
                           title="Category Spending")
                bar.update_layout(paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(bar,use_container_width=True)

        try:
            df["Date"]=pd.to_datetime(df["Date"])
            monthly=df.groupby(df["Date"].dt.strftime("%Y-%m"))["Amount"].sum().reset_index()
            line=px.line(monthly,x="Date",y="Amount",markers=True,
                         title="Monthly Trend")
            line.update_layout(paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(line,use_container_width=True)
        except:
            pass

        st.info("💡 Smart Tip: Keep savings above 20% of your monthly income.")
