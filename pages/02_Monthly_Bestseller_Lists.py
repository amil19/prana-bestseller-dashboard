import streamlit as st
import polars as pl
import bestseller_main_funcs as bs_funcs

##################################################################
st.set_page_config(
    page_title="Monthly Bestseller Lists",
)

st.title("Monthly Bestseller Lists")

##################################################################
# Load base data
base_data = st.session_state['base_data']
##################################################################

# Get most recent reporting date
most_recent_RD = base_data.select(pl.max('ReportingDate')).collect().item()

# Create titles_df
titles_df = bs_funcs.create_titles_df(base_data)

# Populate reporting dates for select box
rd_options = titles_df['ReportingDate'].unique().sort(descending=True)

# Select reporting date
rd = st.selectbox(label='Select reporting month',options=rd_options, index=0)

# Create top 100 dataframe
top_100 = bs_funcs.create_top_titles_df(titles_df,rd,'top100')

# Create Indie 25 dataframe
indie_25 = bs_funcs.create_top_titles_df(titles_df,rd,'indie25')


# Write both tables
st.subheader(f'Top 100 ({bs_funcs.monYear(rd)})')
st.write(top_100)

st.subheader(f'Indie 25 ({bs_funcs.monYear(rd)})')
st.write(indie_25)
