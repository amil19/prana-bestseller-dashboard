import streamlit as st
import sqlite3 as sql
import polars as pl
import math
import bestseller_main_funcs as bs_funcs
import bestseller_plots as bs_plots
##################################################################
st.set_page_config(
    page_title="Fan Confidence Rating",
    #page_icon="👋",
)
#st.sidebar.success("Fan Confidence Rating")
st.title("Fan Confidence Rating")

st.write("Insert explanation of rating and importance")

##################################################################

# Set connection to SQL DB
conn = sql.connect('prana_bestseller.db')

# Load base data
base_data = bs_funcs.load_data_from_sql(conn).lazy()

def create_fcr_data(base_data: pl.LazyFrame):
    # Subset FCR data
    df = base_data.group_by('ReportingDate')\
    .agg(pl.sum("ConsumerCopies"))\
    .sort("ReportingDate",descending=False).collect()

    # Convert consumer copies to log values
    df = df.with_columns(
        pl.Series([math.log(x) for x in df["ConsumerCopies"]]).alias("ConsumerCopies"))

    return df

# Subset FCR data
fcr_data = create_fcr_data(base_data)

# Create dropdowns for view
start,end = bs_funcs.select_dates(fcr_data)


# Plot with Altair
st.altair_chart(bs_plots.create_fcr_plot(fcr_data,start,end))
