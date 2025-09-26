import polars as pl
import streamlit as st

import bestseller_main_funcs as bs_funcs

##################################################################
st.set_page_config(
    page_title="Creators",
)

st.title("Creator Data")

##################################################################
# Load base data
base_data = st.session_state["base_data"]
##################################################################

creator_types = ["WRITER", "ARTIST", "COVER_ARTIST"]


def get_top_10(df: pl.LazyFrame, date: str|list[str], grouping_var: str | list[str]):

    df = bs_funcs.get_reporting_month(df,date)
    
    result = (
        df.filter(pl.col(grouping_var).is_not_null())
        .group_by(grouping_var)
        .agg(pl.sum("ConsumerCopies"))
        .sort("ConsumerCopies", descending=True)
        .with_columns(pl.col("ConsumerCopies").rank(descending=True).alias("Rank"))
        .drop("ConsumerCopies")
    )

    return result.collect()


# Select Data Range
rpt_dts = bs_funcs.create_multiselect(
    base_data.collect(), "ReportingDate", "Select Reporting Date(s)", sort_order=True
)

st.subheader("Top 10 Lists")
col1, col2, col3 = st.columns(3)
col_list = [col1, col2, col3]
#for rpt_dt in rpt_dts:
for creator, col in zip(creator_types, col_list):
    with col:
        st.write(creator)
        st.dataframe(get_top_10(base_data, rpt_dts, creator))

# # Creator Type Dropdown
# creator_type = st.selectbox('Select which type of creator to view', options=[None,'WRITER','ARTIST','COVER_ARTIST'])

# if creator_type:

# # def cover_artist_stats(month: str):
# #   global cover_artist_stats_df
# #   cover_artist_stats_df = df_pl.drop_nulls(subset=["COVER_ARTIST"]).filter((pl.col("ReportingDate") == month) & (~pl.col("COVER_ARTIST").is_in(exempt_credits)))['COVER_ARTIST'].value_counts(sort=True,name='# of Covers').head(10)
# #   sns.barplot(data=cover_artist_stats_df,x='COVER_ARTIST',y='# of Covers',hue='COVER_ARTIST',palette='flare_r')
# #   plt.xlabel('Cover Artist')
# #   plt.xticks(rotation=75)
