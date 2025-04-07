import streamlit as st
import polars as pl
import bestseller_main_funcs as bs_funcs
import bestseller_plots as bs_plots

##################################################################
st.set_page_config(
    page_title="Publishers",
)

st.title("Publisher Data")


##################################################################
# Load base data
base_data = st.session_state['base_data']
##################################################################

# Extract number of stores reporting each month
store_counts = base_data.group_by('ReportingDate').agg(pl.max("Ordering_Reporting").alias("Stores_Ordering")).collect()

def create_multiselect(df: pl.DataFrame, column: str, message: str, sort_order: str=None, default_idx: int=None):

    selection_list = df.select(column).unique()

    if sort_order != None:
        selection_list = selection_list.sort(column, descending=sort_order)
    else:
        selection_list = selection_list.sort(column, descending=False)

    if default_idx:
        default_selection = selection_list[default_idx]
    else:
        default_selection = None
        
    options = st.multiselect(f'{message}',selection_list, default=default_selection)

    return options

def get_publisher_df(df, publisher_names):

    df = df.filter(pl.col("PUBLISHER").is_in(publisher_names)).sort('PUBLISHER',descending=False)

    return df
    
# Select Publishers
pub_names = create_multiselect(base_data.collect(),'PUBLISHER','Select Publisher')

# Create Publisher DF
pub_df = get_publisher_df(base_data,pub_names).collect()

# Select Date Range
start_date,end_date = bs_funcs.select_dates(pub_df)

# Set Subset Publisher DF by date
pub_df_with_dates = pub_df.filter(
    (pl.col("ReportingDate") >= start_date) & (pl.col("ReportingDate") <= end_date)
    ).join(store_counts,on='ReportingDate',how='inner')

# Get CC Per Store Data
cc_data = pub_df_with_dates.group_by('PUBLISHER','ReportingDate')\
.agg((pl.sum("ConsumerCopies")/pl.max("Ordering_Reporting")).alias("CC_Per_Store"))\
.sort('ReportingDate','PUBLISHER',descending=False)

# Plot CC data
st.subheader("Average Consumer Copies per Store (by Month)")
st.altair_chart(bs_plots.plot_offset_bar(cc_data,xaxis="ReportingDate:O",yaxis="CC_Per_Store:Q",
                                        color='PUBLISHER:N',xOffset='PUBLISHER:N'))

# Benchmarks section
st.subheader("Benchmarks")
launch_df = pub_df_with_dates.drop_nulls('GF_Series_Code')\
.filter(pl.col("ISSUE_NO").is_in([0,1])).sort("ReportingDate","MAIN_DESC")

# Create benchmark df
benchmarks = pub_df_with_dates.group_by('PUBLISHER','GF_Series_Code','Stores_Ordering')\
.agg(pl.sum("ConsumerCopies"))\
.with_columns(
    (pl.col("ConsumerCopies")/pl.col("Stores_Ordering")).alias("Avg_CC_Per_Store")).group_by('PUBLISHER').agg(pl.mean('Avg_CC_Per_Store'))

# Plot Data
st.subheader("New Launches - Average Consumer Copies Per Store")
nl_bench_0, nl_bench_1 = st.columns(2)
with nl_bench_0:
    st.bar_chart(data=benchmarks,x='PUBLISHER',y='Avg_CC_Per_Store',color='#008000')
with nl_bench_1:
    st.write(benchmarks.sort("Avg_CC_Per_Store",descending=True))  