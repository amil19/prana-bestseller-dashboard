import datetime

import polars as pl
import streamlit as st

big_3 = ["Marvel", "Dc Comics", "Image"]


def load_data_from_sql():
    import psycopg2

    # Connect to the database
    connection = psycopg2.connect(
        user=st.secrets["USER"],
        password=st.secrets["PASSWORD"],
        host=st.secrets["HOST"],
        port=st.secrets["PORT"],
        dbname=st.secrets["DBNAME"],
    )

    base_schema = {
        "GF_ID": str,
        "PRETTY_TITLE": str,
        "MAIN_DESC": str,
        "ISSUE_NO": pl.Float32,
        "ISSUE_SEQ_NO": pl.Int64,
        "QTY_Subscription": pl.Int64,
        "QTY_Pre_Order": pl.Int64,
        "QTY_Shelf": pl.Int64,
        "QTY_Sold": pl.Int64,
        "Ordering_Reporting": pl.Int64,
        "Sold_Reporting": pl.Int64,
        "GF_Series_Code": str,
        "MAX_ISSUE": pl.Float32,
        "PRICE": pl.Float64,
        "PUBLISHER": str,
        "UPC_NO": str,
        "SHORT_ISBN_NO": str,
        "EAN_NO": str,
        "PRODUCT_TYPE": str,
        "MATURE": str,
        "ADULT": str,
        "RATIO": pl.Int64,
        "WRITER": str,
        "ARTIST": str,
        "COVER_ARTIST": str,
        "NUMBER_OF_PAGES": pl.Int64,
        "Diamond_Number": str,
        "LUNAR_CODE": str,
        "PRH_CODE": str,
        "Geekfetch_URL": str,
        "Geekfetch_Image": str,
        "ReportingDate": str,
        "ConsumerCopies": pl.Int64,
    }

    df = pl.read_database(
        "Select * from bestseller_data;", connection, schema_overrides=base_schema
    )
    df = df.lazy()

    connection.close()

    return df

def create_reporting_date_multiselect(df):
    reporting_dates = df.select("ReportingDate").unique().sort("ReportingDate")

    options = st.multiselect(
        "Select reporting month(s)", reporting_dates, default=reporting_dates[-1]
    )

    return options

def monYear(yyyymm):
    year = int(yyyymm[:4])
    month = int(yyyymm[4:])
    month_name = datetime.date(year, month, 1).strftime("%b")
    return f"{month_name} {year}"


def monYearToDate(yyyymm):
    year = int(yyyymm[:4])
    month = int(yyyymm[4:])

    return datetime.date(year, month, 1)


def convert_dates(df, date_column):
    df = df.with_columns(
        pl.col(date_column).map_elements(lambda x: monYearToDate(x),
                                         return_dtype=pl.Date), allow_object=True
    )

    return df


def select_start(df):
    option_range = df["ReportingDate"].unique().sort()

    return st.selectbox(label="Select start date for report", options=option_range)


def select_dates(df):
    start_options = df["ReportingDate"].unique().sort().to_list()
    start_def = len(start_options) - 12
    start = st.selectbox(
        label="Select start date for report", options=start_options, index=start_def
    )

    end_options = (
        df.filter(pl.col("ReportingDate") > start)["ReportingDate"].unique().sort()
    )
    end_def = len(end_options) - 1
    end = st.selectbox(
        label="Select end date for report", options=end_options, index=end_def
    )

    return start, end


def get_reporting_month(df, reporting_month: str|list[str]):

    if type(reporting_month) == str:
        filter_criteria = pl.col("ReportingDate") == reporting_month
    else:
        filter_criteria = pl.col("ReportingDate").is_in(reporting_month)
    
    df = df.filter(filter_criteria)

    return df


def create_titles_df(df: pl.LazyFrame):
    # Set columns needed for the title evaluation
    title_cols = [
        "MAIN_DESC",
        "ISSUE_NO",
        "PUBLISHER",
        "ReportingDate",
        "ConsumerCopies",
    ]

    titles_df = (
        df.with_columns(pl.col("MAIN_DESC").str.to_titlecase().alias("MAIN_DESC"))
        .select(title_cols)
        .group_by(["MAIN_DESC", "ISSUE_NO", "PUBLISHER", "ReportingDate"])
        .agg(pl.sum("ConsumerCopies"))
        .sort("ConsumerCopies", descending=True)
        .rename({"MAIN_DESC": "Title", "ISSUE_NO": "Issue", "PUBLISHER": "Publisher"})
        .collect()
    )

    return titles_df


def create_top_titles_df(titles_df: pl.DataFrame, reporting_date: str, list: str,agg_by_title: bool=False):
    
    df = get_reporting_month(titles_df, reporting_date)

    if list.lower() == "top100":
        if not agg_by_title:
            df = (
                df.with_columns(
                    pl.col("ConsumerCopies").rank(descending=True).alias("Rank")
                )
                .sort("Rank")
                .head(100)
                .drop("ReportingDate", "ConsumerCopies")
                .select("Rank", "Title", "Issue", "Publisher")
            )
        else:
            df = (
                df.group_by("Title","Publisher")
                .agg(pl.sum("ConsumerCopies"))
                .with_columns(
                    pl.col("ConsumerCopies").rank(descending=True).alias("Rank")
                              )
                .sort("Rank")
                .head(100)
                .drop("ConsumerCopies")
                .select("Rank", "Title", "Publisher")
                )

    if list.lower() == "indie25":
        if not agg_by_title:
            df = (
                df.filter(~pl.col("Publisher").is_in(big_3))
                .with_columns(pl.col("ConsumerCopies").rank(descending=True).alias("Rank"))
                .sort("Rank")
                .head(25)
                .drop("ReportingDate", "ConsumerCopies")
                .select("Rank", "Title", "Issue", "Publisher")
            )
        else:
            df = (
                df.filter(~pl.col("Publisher").is_in(big_3))
                .group_by("Title","Publisher")
                .agg(pl.sum("ConsumerCopies"))
                .with_columns(
                    pl.col("ConsumerCopies").rank(descending=True).alias("Rank")
                              )
                .sort("Rank")
                .head(25)
                .drop("ConsumerCopies")
                .select("Rank", "Title", "Publisher")
            )

    return df


def create_multiselect(
    df: pl.DataFrame,
    column: str,
    message: str,
    sort_order: str = None,
    default_idx: int = None,
):
    selection_list = df.select(column).unique()

    if sort_order is not None:
        selection_list = selection_list.sort(column, descending=sort_order)
    else:
        selection_list = selection_list.sort(column, descending=False)

    if default_idx:
        default_selection = selection_list[default_idx]
    else:
        default_selection = None

    options = st.multiselect(f"{message}", selection_list, default=default_selection)

    return options
