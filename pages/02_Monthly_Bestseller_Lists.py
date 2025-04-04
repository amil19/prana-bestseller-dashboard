import streamlit as st
import polars as pl
import bestseller_main_funcs as bs_funcs
import sqlite3 as sql
import numpy as np
import pandas as pd
#import bestseller_plots as bs_plots
#import altair as alt

##################################################################
st.set_page_config(
    page_title="Monthly Bestseller Lists",
    #page_icon="👋",
)
#st.sidebar.success("Fan Confidence Rating")
st.title("Monthly Bestseller Lists")

st.write("Insert explanation of rating and importance")
##################################################################
# Set connection to SQL DB
conn = sql.connect('prana_bestseller.db')

# Load base data
base_data = bs_funcs.load_data_from_sql(conn).lazy()
##################################################################

most_recent_RD = base_data.select(pl.max('ReportingDate')).collect().item()

title_cols = ['MAIN_DESC', 'ISSUE_NO', 'PUBLISHER', 'ReportingDate','ConsumerCopies']

titles_df = base_data.with_columns(pl.col("MAIN_DESC").str.to_titlecase().alias("MAIN_DESC")).select(title_cols).group_by(['MAIN_DESC','ISSUE_NO','PUBLISHER','ReportingDate']).agg(pl.sum('ConsumerCopies')).sort('ConsumerCopies',descending=True).rename({'MAIN_DESC': 'Title','ISSUE_NO': 'Issue','PUBLISHER':'Publisher'}).collect()

rd_options = titles_df['ReportingDate'].unique().sort(descending=True)

rd = st.selectbox(label='Select reporting month',options=rd_options, index=0)

top_100 = bs_funcs.get_reporting_month(titles_df,rd)\
.with_columns(pl.col("ConsumerCopies").rank(descending=True).alias("Rank"))\
.sort('Rank').head(100).drop('ReportingDate','ConsumerCopies').select('Rank','Title','Issue','Publisher')

indie_25 = bs_funcs.get_reporting_month(titles_df,rd).filter(~pl.col("Publisher").is_in(bs_funcs.big_3))\
.with_columns(pl.col("ConsumerCopies").rank(descending=True).alias("Rank"))\
.sort('Rank').head(25).drop('ReportingDate','ConsumerCopies').select('Rank','Title','Issue','Publisher')

st.subheader(f'Top 100 ({bs_funcs.monYear(rd)})')
st.write(top_100)

st.subheader(f'Indie 25 ({bs_funcs.monYear(rd)})')
st.write(indie_25)

#top_100['Rank'] = top_100['ConsumerCopies'].rank(ascending=False)

