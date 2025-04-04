import polars as pl
import datetime
import streamlit as st
import sqlite3 as sql

big_3 = ['Marvel','Dc Comics','Image']

def load_data_from_sql(conn):

    base_schema = {
        "GF_ID":pl.Int64,
        "PRETTY_TITLE":str,
        "MAIN_DESC":str,
        "ISSUE_NO":pl.Int64,
        "ISSUE_SEQ_NO":pl.Int64,
        "QTY_Subscription":pl.Int64,
        "QTY_Pre_Order":pl.Int64,
        "QTY_Shelf":pl.Int64,
        "QTY_Sold":pl.Int64,
        "Ordering_Reporting":pl.Int64,
        "Sold_Reporting":pl.Int64,
        "GF_Series_Code":pl.Int64,
        "MAX_ISSUE":pl.Int64,
        "PRICE":pl.Float64,
        "PUBLISHER":str,
        "UPC_NO":str,
        "SHORT_ISBN_NO":str,
        "EAN_NO":str,
        "PRODUCT_TYPE":str,
        "MATURE":str,
        "ADULT":str,
        "RATIO":pl.Int64,
        "WRITER":str,
        "ARTIST":str,
        "COVER_ARTIST":str,
        "NUMBER_OF_PAGES":pl.Int64,
        "Diamond_Number":str,
        "LUNAR_CODE":str,
        "PRH_CODE":str,
        "Geekfetch_URL":str,
        "Geekfetch_Image":str,
        "ReportingDate":str,
        "ConsumerCopies":pl.Int64,
        }
    
    df = pl.read_database("Select * from bestseller_data", 
                          conn, 
                          schema_overrides=base_schema)
    
    return df.select(pl.all().exclude(['Geekfetch_URL','Geekfetch_Image']))

def monYear (yyyymm):
  year = int(yyyymm[:4])
  month = int(yyyymm[4:])
  month_name = datetime.date(year, month, 1).strftime('%b')
  return f"{month_name} {year}"

def monYearToDate(yyyymm):
    year = int(yyyymm[:4])
    month = int(yyyymm[4:])
    
    return datetime.date(year, month, 1)

def convert_dates(df,date_column):
    df = df.with_columns(
        pl.col(date_column)\
        .map_elements(lambda x: monYearToDate(x)))
    
    return df

def select_start(df):

    option_range = df['ReportingDate'].unique().sort()
    
    return st.selectbox(label='Select start date for report',options=option_range)

def select_dates(df):

    start_options = df['ReportingDate'].unique().sort()
    start_def = len(start_options)-12
    start = st.selectbox(label='Select start date for report',
                         options=start_options,
                         index=start_def)

    end_options = df.filter(pl.col("ReportingDate") > start)['ReportingDate'].unique().sort()
    end_def = len(end_options)-1
    end = st.selectbox(label='Select end date for report',
                       options=end_options,
                       index=end_def)
    
    return start,end

def get_reporting_month(df,reporting_month):
    
    df = df.filter(pl.col("ReportingDate") == reporting_month)

    return df