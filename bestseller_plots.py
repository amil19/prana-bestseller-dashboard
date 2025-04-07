import altair as alt
import plotly.express as px
import datetime
import polars as pl
import bestseller_main_funcs as bs_funcs

def create_fcr_plot(fcr_df: pl.DataFrame, start_date: str, end_date: str):
    # Gather data for plotting
    fcr_plot_df = fcr_df.filter(pl.col("ReportingDate") >= start_date)
    # Convert dates
    fcr_plot_df = bs_funcs.convert_dates(fcr_plot_df,"ReportingDate")
    ## Set values for y-axis
    y_min = fcr_plot_df.select(pl.min("ConsumerCopies")).item()
    y_max = fcr_plot_df.select(pl.max("ConsumerCopies")).item()

    # Create Altair plot
    fcr_chart = (
        alt.Chart(fcr_plot_df, 
                  title=f'Fan Confidence Rating ({bs_funcs.monYear(start_date)} - {bs_funcs.monYear(end_date)})')\
        .mark_line(point=True)\
        .encode(x=alt.X('ReportingDate',
                        axis=alt.Axis(title='Reporting Date',
                                      format="%b %Y",
                                      labelAngle=-45,
                                      tickCount=len(fcr_plot_df))),
                y=alt.Y('ConsumerCopies',
                        title='Fan Confidence Rating',
                        scale=alt.Scale(domain=[y_min,y_max]))
                ,color=alt.value("#008000")
               )
    )

    return fcr_chart

def create_altair_pie(chart_df: pl.DataFrame,chart_title: str,value: str, category: str):
    base_chart = alt.Chart(chart_df,title=chart_title).encode(
    alt.Theta(f"{value}:Q").stack(True),
    alt.Color(f"{category}:N").legend(None)
)

    pie = base_chart.mark_arc(outerRadius=120)
    text = base_chart.mark_text(radius=140, size=8).encode(text=f"{category}:N")

    pie_chart = pie + text

    return pie_chart

def create_px_pie(df, values: str, names: str, colors=None):
    
    if not colors:
        
        fig = px.pie(df, values=values, names=names,
                     color_discrete_sequence=px.colors.qualitative.Set1)
        
    else:
        fig = px.pie(df, values=values, names=names,
         color_discrete_sequence=colors)

    fig.update_traces(textinfo='label')

    return fig

def create_radial_chart(source: pl.DataFrame, values: str, color: str, color_pallete: str):

    
    base = alt.Chart(source).encode(
    alt.Theta(f"{values}:Q").stack(True),
    alt.Radius(f"{values}").scale(type="sqrt", zero=True, rangeMin=20),
    color=alt.Color(f"{color}:N", scale=alt.Scale(scheme=color_pallete)),
    order=f"{values}:O"
)

    c1 = base.mark_arc(innerRadius=20, stroke="#fff")

    c2 = base.mark_text(radiusOffset=20).encode(text=alt.Text(f"{values}:Q", format=",.2%"))

    return c1 + c2

def plot_offset_bar(df: pl.DataFrame, xaxis: str, yaxis: str, color: str, xOffset: str):
    
    offset_bar_chart = alt.Chart(df).mark_bar().encode(
        alt.X(xaxis),
        alt.Y(yaxis),
        color=color,
        xOffset=xOffset)

    return offset_bar_chart