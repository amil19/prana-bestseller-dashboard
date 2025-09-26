import polars as pl
import streamlit as st

import bestseller_main_funcs as bs_funcs

##################################################################
st.set_page_config(
    page_title="Monthly Bestseller Lists",
)

st.title("Monthly Bestseller Lists")

##################################################################
# Load base data
base_data = st.session_state["base_data"]
##################################################################

# Create titles_df
titles_df = bs_funcs.create_titles_df(base_data)

rd = bs_funcs.create_reporting_date_multiselect(titles_df)

agg_by_title = st.checkbox("Aggregate by Title?")

# Create top 100 dataframe
top_100 = bs_funcs.create_top_titles_df(titles_df, rd, "top100",agg_by_title)

# Create Indie 25 dataframe
indie_25 = bs_funcs.create_top_titles_df(titles_df, rd, "indie25",agg_by_title)


# Write both tables
st.subheader(f"Top 100 ({[bs_funcs.monYear(rpt_dt) for rpt_dt in rd]})")
st.write(top_100)

st.subheader(f"Indie 25 ({[bs_funcs.monYear(rpt_dt) for rpt_dt in rd]})")
st.write(indie_25)
