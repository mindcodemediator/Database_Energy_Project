import streamlit as st
import pandas as pd
import altair as alt
from Energy_helpers import *

@st.cache
def getReliabilityQuery():
    return """
    select year as saidi_year, trunc(avg(saidi_med), 1) as saidi_dis, trunc(avg(saidi),1) as saidi_no_dis from
    (
        select * from JOLIU.outages
        inner join
        (
            select * from JOLIU.territory
            where
            (
                JOLIU.territory.state = :inState and
                JOLIU.territory.county = :inCounty
            )    
        )
        using(util_id, year)
    )
    group by year
    order by year asc"""

def displayReliability(connection):


    #State & county select
    dfState = pd.read_sql(getStates(), con = connection)
    state_select = st.selectbox('Select the state:', dfState['STATE'])
    dfCounty = pd.read_sql(getCounties(), con = connection, params=[state_select])
    county_select= st.selectbox('Select the county:', dfCounty['COUNTY'])

    #read in reliability query
    df = pd.read_sql(getReliabilityQuery(), con = connection, params=[state_select, county_select])

    df.columns = ('Year', 'Including Disasters', 'Excluding Disasters')

    df_melted = df.melt(id_vars = [df.columns[0]], value_vars = [df.columns[1], df.columns[2]])
    df_melted.columns =('Year', ' ', 'Average Minutes w/o Electricity per Customer')
    #bar chart
    #st.write(df_melted)
    bc = alt.Chart(df_melted).mark_bar().encode(
        x=' :N',
        y='Average Minutes w/o Electricity per Customer:Q',
        color= ' :N',
        column='Year:O',
    )
    text = bc.mark_text(
    ).encode(
        text=''
    )

    return bc
