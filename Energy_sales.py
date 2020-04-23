import streamlit as st
import pandas as pd
import altair as alt
from Energy_helpers import *

def getSalesQuery():
    return """
    select * from
        (
        select county as "Location", year as "Year", trunc(sum(revenue)*1000/sum(mwh_sold), 3) as "Avg Rev($)/MWh Sold" from JOLIU.sales
        inner join JOLIU.territory
        using(util_id, year)
        where
            (
            cust_sector_name = 'Residential' and
            JOLIU.territory.state = :inState and
            county = :inCounty
            )
        group by county, year
        order by year asc
        )
    union
        (
        select 'National Avg' as "Location", year as "Year", trunc(sum(revenue)*1000/sum(mwh_sold), 3) as "Avg Rev($)/MWh Sold" from JOLIU.sales
        where
            (
            cust_sector_name = 'Residential'
            )
        group by year
        )"""

def displaySales(connection):


    #State & county select
    dfStateSales = pd.read_sql(getStates(), con = connection)
    state_select_sales = st.selectbox('Select the state:', dfStateSales['STATE'], key='stateSalesSelect')
    dfCountySales = pd.read_sql(getCounties(), con = connection, params=[state_select_sales])
    county_select_sales= st.selectbox('Select the county:', dfCountySales['COUNTY'], key='countySalesSelect')

    # read in sales query
    dfStateSales = pd.read_sql(getSalesQuery(), con=connection, params=[state_select_sales, county_select_sales])
    dfStateSales.columns = (' ', 'Year', '$/MWh')
    # bar chart
    bc_sales = alt.Chart(dfStateSales).mark_bar().encode(
        x=' :N',
        y='$/MWh:Q',
        color=' :N',
        column='Year:O'
    )

    return bc_sales
