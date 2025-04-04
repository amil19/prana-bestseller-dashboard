import streamlit as st
import polars as pl
import sqlite3 as sql
import bestseller_main_funcs as bs_funcs
import bestseller_plots as bs_plots
import altair as alt

##################################################################
st.set_page_config(
    page_title="Marketshare",
    #page_icon="👋",
)
#st.sidebar.success("Fan Confidence Rating")
st.title("Direct Market Marketshare")

st.write("Insert explanation of rating and importance")

##################################################################

# Set connection to SQL DB
conn = sql.connect('prana_bestseller.db')

# Load base data
base_data = bs_funcs.load_data_from_sql(conn).lazy()

def create_marketshare_base(base_df):
    # Columns needed
    cols_needed = ['MAIN_DESC', 'ISSUE_NO', 'PUBLISHER', 'ReportingDate','PRICE','ConsumerCopies']
    
    marketshare_df = base_df.select(cols_needed).with_columns(
            (pl.col("ConsumerCopies") * pl.col("PRICE")
            ).alias("RetailDollars")).collect()

    return marketshare_df

def create_reporting_date_multiselect(df):
    reporting_dates = df.select('ReportingDate').unique().sort('ReportingDate')

    options = st.multiselect('Select reporting month(s)',reporting_dates, default=reporting_dates[-1])

    return options

def get_reporting_month(df,reporting_month):
    
    df = df.filter(pl.col("ReportingDate") == reporting_month)

    return df

def create_marketshare_df(df, grouping_var,basis_var,title):

    df = df\
    .group_by(grouping_var)\
    .agg(pl.col(basis_var).sum())\
    .with_columns((pl.col(basis_var)/pl.sum(basis_var)).alias(f'Marketshare_{title}'))\
    .sort(f'Marketshare_{title}',descending=True).drop(basis_var).head(10)
    return df

# Create function to format values as percentages
def format_pct(df, column_name):
    return df.with_columns(
        (pl.col(column_name) * 100).round(2).cast(pl.Utf8) + "%")


# Create marketshare base
marketshare_base = create_marketshare_base(base_data)

# Select Reporting Month(s)
rd_options = create_reporting_date_multiselect(marketshare_base)

for idx, rd in enumerate(rd_options):
    
    # Subset data
    marketshare_by_month = get_reporting_month(marketshare_base,rd)

    # Create dollars df
    marketshare_dollars = create_marketshare_df(marketshare_by_month,'PUBLISHER','RetailDollars','Dollars')

    # Create units df
    marketshare_units = create_marketshare_df(marketshare_by_month,'PUBLISHER','ConsumerCopies','Units')

    # Marketshare by Dollars
    st.subheader(f'Marketshare by Dollars ({bs_funcs.monYear(rd)})')

    # Create columns for table and chart
    globals()["dollars_"+str(idx)+'a'], globals()["dollars_"+str(idx)+'b'] = st.columns(2)
    with globals()["dollars_"+str(idx)+'a']:
        # Write dollars table
        st.dataframe(format_pct(marketshare_dollars,'Marketshare_Dollars').rename({'PUBLISHER': 'Publisher','Marketshare_Dollars': 'Marketshare Dollars PCT'}))
    with globals()["dollars_"+str(idx)+'b']:
        # Plot Pie Chart
        st.write(bs_plots.create_px_pie(marketshare_dollars,'Marketshare_Dollars','PUBLISHER'))

    # Marketsare by Units
    st.subheader(f'Marketshare by Units ({bs_funcs.monYear(rd)})')
    # Create columns for table and chart
    globals()["units_"+str(idx)+'a'], globals()["units_"+str(idx)+'b'] = st.columns(2)
    with globals()["units_"+str(idx)+'a']:
        # Write units table
        st.dataframe(format_pct(marketshare_units,'Marketshare_Units').rename({'PUBLISHER': 'Publisher','Marketshare_Units': 'Marketshare Units PCT'}))
    with globals()["units_"+str(idx)+'b']:
        # Plot Pie Chart
        st.write(bs_plots.create_px_pie(marketshare_units,'Marketshare_Units','PUBLISHER'))

    # # Plot marketshare dollars
    # pie_chart = bs_plots.create_pie_chart(marketshare_dollars,'Marketshare by Dollars','Marketshare_Dollars','PUBLISHER')
    
    # st.altair_chart(pie_chart)
    
    # color_scheme = st.selectbox("Select color scheme", options = ['accent', 'category10', 'category20', 'category20b', 'category20c', 'dark2', 'paired', 'pastel1', 'pastel2', 'set1', 'set2', 'set3', 'tableau10', 'tableau20'])
    
    
    # radial_chart = bs_plots.create_radial_chart(marketshare_dollars.sort("Marketshare_Dollars",descending=True),'Marketshare_Dollars','PUBLISHER', 'greens')
    
    # st.altair_chart(radial_chart)
