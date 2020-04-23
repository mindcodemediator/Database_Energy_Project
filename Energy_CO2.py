#Return C02 functions
import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data

@st.cache
def getCO2Query(order):
    return  """
    select terr_state, year, sum(tons_co2) as total_co2 from
        (
        select * from JOLIU.emissions
        inner join
            (
            select util_id, plant_id, terr_state from JOLIU.plant
            inner join
                (
                select year, state as terr_state, util_id from JOLIU.territory
                where state in
                    (
                    select s from
                        (
                        select distinct s, co2_end - co2_start as diff from
                            (select distinct s, y as year_end, sum(c) as co2_end from
                                (
                                select  distinct emissions.year as y,
                                        plant_id,
                                        util_id,
                                        territory.state as s,
                                        emissions.tons_co2 as c
                                from JOLIU.plant
                                inner join JOLIU.territory using(util_id)
                                inner join JOLIU.emissions using(plant_id)
                                where (JOLIU.emissions.year = :end_year)
                                )
                            group by s, y
                            )
                        inner join
                            (
                            select distinct s, y as year_start, sum(c) as co2_start from
                                (
                                select  distinct emissions.year as y,
                                        plant_id,
                                        util_id,
                                        territory.state as s,
                                        emissions.tons_co2 as c
                                from JOLIU.plant
                                inner join JOLIU.territory using(util_id)
                                inner join JOLIU.emissions using(plant_id)
                                where (JOLIU.emissions.year = :start_year)
                                )
                            group by s, y
                            )
                        using(s)
                        order by diff """ + order + """
                        fetch first 5 rows only
                        )
                    )
                )
            using(util_id)
            )
        using(plant_id))
    where year >= :disp_start and year <= :disp_end
    group by terr_state, year
    order by terr_state asc, year desc"""

#CO2 change over year function
def displayCO2(connection, order, year, endyear, allyears):

    if allyears == True:
        start = 2013
        end = 2018
    else:
        start = year
        end = endyear


    df = pd.read_sql(getCO2Query(order), con = connection, params = [endyear, year, start, end])
    df.columns = ('State', 'Year', 'CO2, Trillions of Tons')
    df['CO2, Trillions of Tons'] = df.apply(
        lambda row: row['CO2, Trillions of Tons'] / 1000000000, axis = 1
    )

    lc = alt.Chart(df).mark_line().encode(
    alt.Y('CO2, Trillions of Tons:Q', scale=alt.Scale(zero=False)),
    x = 'Year:O',
    color = 'State:N'
    ).properties(
        width=600,
        height=400
    )

    return lc
   # st.write(df)


@st.cache
def getCO2State(states):
    return"""
        SELECT s, sn, y , SUM(c) 
 FROM

(

SELECT JOLIU.emissions.year AS y,

JOLIU.emissions.plant_id,

util_id,

county,

state AS s,

state_name AS sn,

tons_co2 AS c

FROM JOLIU.emissions

INNER JOIN JOLIU.transmits_pwr_to ON

(

JOLIU.emissions.year = JOLIU.transmits_pwr_to.year AND

JOLIU.emissions.plant_id = JOLIU.transmits_pwr_to.plant_id

)

INNER JOIN JOLIU.territory USING(util_id)

INNER JOIN JOLIU.state_abbv USING (state)

WHERE

(

(

JOLIU.emissions.year >= :startyear AND

JOLIU.emissions.year <= :endyear

)

AND

(

""" + states + """

)

)

)

GROUP BY s, sn, y

ORDER BY s ASC, y DESC"""




def displayCO2byState(connection, year_start, year_end, state1, state2, state3, state4, state5):
    # open connection


    state_sql = """"""
    if state1 != """""":
        state_sql += """state = '""" + state1 + """' OR """
    if state1 != """""":
        state_sql += """state = '""" + state2 + """' OR """
    if state1 != """""":
        state_sql += """state = '""" + state3 + """' OR """
    if state1 != """""":
        state_sql += """state = '""" + state4 + """' OR """
    if state1 != """""":
        state_sql += """state = '""" + state5 + """'"""

    if state_sql == """""":
        return

    if state_sql[-3] == 'O' and state_sql[-2] == 'R' and state_sql[-1] == ' ':
        del state_sql[-3]
        del state_sql[-2]
        del state_sql[-1]

    df = pd.read_sql(getCO2State(state_sql), con=connection, params=[year_start, year_end])
    df.columns = ('StateAb', 'State', 'Year', 'CO2, Trillions of Tons')

    df['CO2, Trillions of Tons'] = df.apply(
        lambda row: row['CO2, Trillions of Tons'] / 1000000000, axis = 1
    )

    lc = alt.Chart(df).mark_line().encode(
        alt.Y('CO2, Trillions of Tons', scale=alt.Scale(zero=False)),
        alt.X('Year:O', scale=alt.Scale(zero=False)),
        color='State:N'
    ).properties(
        width=600,
        height=400
    )
    return lc


def getNormalizedCO2(states):
    return """
    SELECT s, sn, y,

TRUNC(SUM(c)/1000000, 0) AS "Millions Metric Tons CO2 Produced",

TRUNC(SUM(m)/1000000, 0) AS "Millions MWh Generated",

TRUNC((SUM(c)/SUM(m))*2204.62, 0) AS "Lbs CO2/MWh" FROM

(

SELECT JOLIU.emissions.year AS y,

JOLIU.emissions.plant_id,

util_id,

county,

state AS s,

state_name AS sn,

tons_co2 AS c,

tot_mwh_gen AS m

FROM JOLIU.emissions

INNER JOIN JOLIU.transmits_pwr_to ON

(

JOLIU.emissions.year = JOLIU.transmits_pwr_to.year AND

JOLIU.emissions.plant_id = JOLIU.transmits_pwr_to.plant_id

)

INNER JOIN

(

SELECT year, plant_id AS mpc_pid,

SUM(MWh_gen) as tot_mwh_gen FROM

(

SELECT * FROM JOLIU.mo_prod_consum

UNION

SELECT * FROM CBOGER.mo_prod_consum

)

GROUP BY year, plant_id

)

ON (mpc_pid = JOLIU.emissions.plant_id)

INNER JOIN JOLIU.territory USING(util_id)

INNER JOIN JOLIU.state_abbv USING (state)

WHERE

(

(

JOLIU.emissions.year >= :startyear AND

JOLIU.emissions.year <= :endyear

)

AND

(

""" + states + """

)

)

)

GROUP BY s, sn, y

ORDER BY s ASC, y DESC
    """


def displayNormalizedCO2(connection, year_start, year_end, state1, state2, state3, state4, state5):
    # open connection


    state_sql = """"""
    if state1 != """""":
        state_sql += """state = '""" + state1 + """' OR """
    if state1 != """""":
        state_sql += """state = '""" + state2 + """' OR """
    if state1 != """""":
        state_sql += """state = '""" + state3 + """' OR """
    if state1 != """""":
        state_sql += """state = '""" + state4 + """' OR """
    if state1 != """""":
        state_sql += """state = '""" + state5 + """'"""

    if state_sql == """""":
        return

    if state_sql[-3] == 'O' and state_sql[-2] == 'R' and state_sql[-1] == ' ':
        del state_sql[-3]
        del state_sql[-2]
        del state_sql[-1]

    df = pd.read_sql(getNormalizedCO2(state_sql), con=connection, params=[year_start, year_end])
    df.columns = ('StateAb', 'State', 'Year', 'x', 'y', 'Lbs CO2/MWh')



    lc = alt.Chart(df).mark_line().encode(
        alt.Y('Lbs CO2/MWh', scale=alt.Scale(zero=False)),
        alt.X('Year:O', scale=alt.Scale(zero=False)),
        color='State:N'
    ).properties(
        width=600,
        height=400
    )
    return lc



def mapQuery():
    return """
    SELECT ROW_NUMBER() over (ORDER BY s) id,

TRUNC(SUM(c)/1000000, 0) AS "Millions Metric Tons CO2 Produced",

TRUNC(SUM(m)/1000000, 0) AS "Millions MWh Generated",

TRUNC((SUM(c)/SUM(m))*2204.62, 0) AS "Lbs CO2/MWh" FROM

(

SELECT JOLIU.emissions.year AS y,

JOLIU.emissions.plant_id,

util_id,

county,

state AS s,

state_name AS sn,

tons_co2 AS c,

tot_mwh_gen AS m

FROM JOLIU.emissions

INNER JOIN JOLIU.transmits_pwr_to ON

(

JOLIU.emissions.year = JOLIU.transmits_pwr_to.year AND

JOLIU.emissions.plant_id = JOLIU.transmits_pwr_to.plant_id

)

INNER JOIN

(

SELECT year, plant_id AS mpc_pid,

SUM(MWh_gen) as tot_mwh_gen FROM

(

SELECT * FROM JOLIU.mo_prod_consum

UNION

SELECT * FROM CBOGER.mo_prod_consum

)

GROUP BY year, plant_id

)

ON (mpc_pid = JOLIU.emissions.plant_id)

INNER JOIN JOLIU.territory USING(util_id)

INNER JOIN JOLIU.state_abbv USING (state)

WHERE

(

(

JOLIU.emissions.year = :mapyear

)

AND

(

state != 'DC'

)

)

)

GROUP BY s, sn, y

ORDER BY s ASC, y DESC
    """




def makeMeAFreakingMap(connection, year_start):
    df = pd.read_sql(mapQuery(), con=connection, params=[year_start])
    df.columns = ('id', 'x', 'y', 'Lbs CO2/MWh')

    states = alt.topo_feature(data.us_10m.url, 'states')
    #st.write(df)
    map = alt.Chart(states).mark_geoshape().encode(
        color='Lbs CO2/MWh:Q'
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(df, 'id', ['Lbs CO2/MWh'])
    ).project(
        type='albersUsa'
    ).properties(
        width=500,
        height=300
    )

    return map
