import os
import pandas as pd
import streamlit as st
import plotly.express as px

from config.settings import CURATED_DIR

st.set_page_config(page_title='Olist Analytics', layout='wide')

@st.cache_data
def load_data():
    path = CURATED_DIR / 'olist_curated.parquet'
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


df = load_data()

if df.empty:
    st.warning('Curated data not found. Run the pipeline first.')
    st.stop()

st.title('Olist Brazilian E-Commerce Analytics')
st.sidebar.header('Filters')
selected_state = st.sidebar.multiselect('Customer State', sorted(df['customer_state'].dropna().unique().tolist()))
selected_category = st.sidebar.multiselect('Category', sorted(df['product_category_name_english'].dropna().unique().tolist()))

if selected_state:
    df = df[df['customer_state'].isin(selected_state)]
if selected_category:
    df = df[df['product_category_name_english'].isin(selected_category)]

col1, col2, col3 = st.columns(3)
col1.metric('Revenue', f"${df['monthly_revenue'].sum():,.2f}")
col2.metric('Avg Delivery Days', f"{df['avg_delivery_days'].mean():.2f}")
col3.metric('Customers', f"{df['customer_id'].nunique()}")

st.subheader('Revenue Trend')
trend = df.groupby(['order_year', 'order_month'])['monthly_revenue'].sum().reset_index()
fig = px.line(trend, x='order_month', y='monthly_revenue', color='order_year', markers=True)
st.plotly_chart(fig, use_container_width=True)

st.subheader('Geographic Orders')
geo = df.groupby('customer_state').size().reset_index(name='orders')
fig2 = px.choropleth(geo, locations='customer_state', locationmode='USA-states', color='orders', hover_name='customer_state')
st.plotly_chart(fig2, use_container_width=True)

st.subheader('Delivery Analysis')
fig3 = px.box(df, x='customer_state', y='avg_delivery_days', points='outliers')
st.plotly_chart(fig3, use_container_width=True)

st.subheader('Customer Distribution')
fig4 = px.histogram(df, x='customer_state', y='monthly_revenue', histfunc='sum')
st.plotly_chart(fig4, use_container_width=True)
