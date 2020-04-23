#Return C02 functions
import streamlit as st
import pandas as pd
import altair as alt

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
                                where (JOLIU.emissions.year = :diff_year)
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
    df.columns = ('terr_state', 'year', 'total_co2')
    df['total_co2'] = df.apply(
        lambda row: row['total_co2'] / 1000000000, axis = 1
    )

    lc = alt.Chart(df).mark_line().encode(
    alt.Y('total_co2:Q', scale=alt.Scale(zero=False)),
    x = 'year:O',
    color = 'terr_state:N'
    ).properties(
        width=600,
        height=400
    )

    return lc
   # st.write(df)


@st.cache
def getCO2State(states):
    return """
       SELECT s, y, SUM(c) as total FROM
       (
           SELECT  DISTINCT JOLIU.emissions.year AS y,
                   plant_id,
                   util_id,
                   JOLIU.territory.state AS s,
                   JOLIU.emissions.tons_co2 AS c
           FROM JOLIU.plant
           INNER JOIN JOLIU.territory USING(util_id)
           INNER JOIN JOLIU.emissions USING(plant_id)
           WHERE
           (
               (JOLIU.emissions.year >= :starting_year AND JOLIU.emissions.year <= :ending_year) AND
               (
                  """ + states + """
               )
           )    
       )
       GROUP BY s, y
       ORDER BY s ASC, y DESC"""


def displayCO2byState(connection, year_start, year_end, state1, state2, state3, state4, state5):
    # open connection


    state_sql = """"""
    if state1 != """""":
        state_sql += """JOLIU.territory.state = '""" + state1 + """' OR """
    if state1 != """""":
        state_sql += """JOLIU.territory.state = '""" + state2 + """' OR """
    if state1 != """""":
        state_sql += """JOLIU.territory.state = '""" + state3 + """' OR """
    if state1 != """""":
        state_sql += """JOLIU.territory.state = '""" + state4 + """' OR """
    if state1 != """""":
        state_sql += """JOLIU.territory.state = '""" + state5 + """'"""

    if state_sql == """""":
        return

    if state_sql[-3] == 'O' and state_sql[-2] == 'R' and state_sql[-1] == ' ':
        del state_sql[-3]
        del state_sql[-2]
        del state_sql[-1]

    df = pd.read_sql(getCO2State(state_sql), con=connection, params=[year_start, year_end])
    df.columns = ('state', 'year', 'total')

    lc = alt.Chart(df).mark_line().encode(
        alt.Y('total:Q', scale=alt.Scale(zero=False)),
        alt.X('year:O', scale=alt.Scale(zero=False)),
        color='state:N'
    ).properties(
        width=600,
        height=400
    )
    return lc
