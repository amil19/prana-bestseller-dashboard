# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import sqlite3 as sql
import polars as pl
import streamlit as st
import numpy as np
import math
import datetime
import altair as alt
import bestseller_main_funcs as bs_funcs

# Set connection to SQL DB
conn = sql.connect('prana_bestseller.db')


base_data = bs_funcs.load_data_from_sql(conn).lazy()

st.title("Prana Bestseller Dashboard")

if st.checkbox('Show Raw Data?'):
    st.dataframe(base_data.collect())

reporting_dates = base_data.select('ReportingDate').unique().sort('ReportingDate',descending=True).collect()

selected_month = st.selectbox('Select Solicitation Month', options=reporting_dates,index=0)

# FCR Data
st.header('Fan Confidence Rating')
fcr_data = base_data.group_by('ReportingDate').agg(pl.sum("ConsumerCopies")).sort("ReportingDate",descending=False).collect()

rd_dates = [bs_funcs.monYear(x) for x in fcr_data["ReportingDate"]]
log_values = [math.log(x) for x in fcr_data["ConsumerCopies"]]
fcr_data = fcr_data.with_columns(
    pl.Series(log_values).alias("ConsumerCopies"))

start = fcr_data.select('ReportingDate').row(-12)[0]
end = fcr_data.select('ReportingDate').row(-1)[0]

fcr_plot_data = fcr_data.filter(pl.col("ReportingDate") >= start)
y_min = fcr_plot_data.select(pl.min("ConsumerCopies")).item()
y_max = fcr_plot_data.select(pl.max("ConsumerCopies")).item()

# st.line_chart(fcr_plot_data, x="ReportingDate", y="ConsumerCopies", color="#008000", x_label='Reporting Month',y_label='Fan Confidence Rating')

# Plot with Altair
c = (alt.Chart(fcr_plot_data, title=f'Fan Confidence Rating ({bs_funcs.monYear(start)} - {bs_funcs.monYear(end)})').mark_line(point=True).encode(x='ReportingDate',y='ConsumerCopies',color=alt.value("#008000")))


st.altair_chart(c.encode(y=alt.Y('ConsumerCopies',scale=alt.Scale(domain=[y_min, y_max]))))


# Consumer Copies
cc_data = base_data.group_by('ReportingDate').agg(
    (pl.sum("ConsumerCopies")/pl.max("Ordering_Reporting")).alias("CC_Per_Store")).sort('ReportingDate',descending=False).collect()

st.subheader("Average Consumer Copies per Store (by Month)")
st.bar_chart(data=cc_data,x="ReportingDate",y="CC_Per_Store",color="#008000")

# Marketshare
cols_needed = ['MAIN_DESC', 'ISSUE_NO', 'PUBLISHER', 'ReportingDate', 'QTY_Subscription', 'QTY_Pre_Order', 'QTY_Shelf','Ordering_Reporting','PRICE']

marketshare_df = base_data.select(cols_needed).filter(pl.col("ReportingDate") == pl.max("ReportingDate")).collect()

marketshare_df = marketshare_df.with_columns(
    (pl.col("QTY_Subscription") + pl.col("QTY_Pre_Order")).alias("ConsumerCopies")
    ).with_columns(
        (pl.col("ConsumerCopies") * pl.col("PRICE")).alias("RetailDollars")
        )

marketshare_dollars = marketshare_df.group_by("PUBLISHER").agg(pl.col("RetailDollars").sum())\
.with_columns((pl.col("RetailDollars")/pl.sum("RetailDollars")).alias("Marketshare_Dollars"))\
.sort("Marketshare_Dollars",descending=True).head(10)

marketshare_units = marketshare_df.group_by("PUBLISHER").agg(pl.col("ConsumerCopies").sum())\
.with_columns((pl.col("ConsumerCopies")/pl.sum("ConsumerCopies")).alias("Marketshare_Units"))\
.sort("Marketshare_Units",descending=True).head(10)

dollars_per_sku = marketshare_df.group_by("PUBLISHER").agg(pl.col("RetailDollars").sum(),\
                                                  pl.col("PUBLISHER").count().alias("SKU_Count"))\
.with_columns((pl.col("RetailDollars")/pl.col("SKU_Count")).alias("Dollars_Per_SKU"))\
.sort("Dollars_Per_SKU",descending=True).head(10)

# st.subheader(f"Publisher Marketshare by Units ({bs_funcs.monYear(marketshare_df.select(pl.max("ReportingDate")).item())})")
# st.bar_chart(data=marketshare_units,x="PUBLISHER",y="Marketshare_Units",color="#008000", horizontal=True)

st.write(alt.Chart(marketshare_units).mark_bar(color="#008000").encode(x=alt.X('PUBLISHER',sort='-y'),y=alt.Y('Marketshare_Units',axis=alt.Axis(format='%'))).properties(title=f"Publisher Marketshare by Units ({bs_funcs.monYear(marketshare_df.select(pl.max("ReportingDate")).item())})"))

st.write(alt.Chart(marketshare_units).mark_bar(color="#008000").encode(x=alt.X('Marketshare_Units',axis=alt.Axis(format='%')),y=alt.Y('PUBLISHER',sort='-x')).properties(title=f"Publisher Marketshare by Units ({bs_funcs.monYear(marketshare_df.select(pl.max("ReportingDate")).item())})"))