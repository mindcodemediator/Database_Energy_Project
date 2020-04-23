# imports
import streamlit as st 
import cx_Oracle
import pandas as pd
import altair as alt

#vars
states = ["""""", """AL""", """AK""", """AZ""", """AR""", """CA""", """CO""", """CT""", """DC""", """DE""", """FL""", """GA""", """HI""", """ID""", """IL""", """IN""", """IA""", """KS""", """KY""", """LA""", """ME""", """MD""", """MA""", """MI""", """MN""", """MS""", """MO""", """MT""", """NE""", """NV""", """NH""", """NJ""", """NM""", """NY""", """NC""", """ND""", """OH""", """OK""", """OR""", """PA""", """RI""", """SC""", """SD""", """TN""", """TX""", """UT""", """VT""", """VA""", """WA""", """WV""", """WI""", """WY"""]

#queries
@st.cache



def getStates():
    return """
    select distinct state from
    (
        select * from JOLIU.outages
        inner join JOLIU.territory
        using(util_id, state, year)
    )
    order by state"""

def getCounties():
    return """
    select distinct county from
    (
        select * from JOLIU.outages
        inner join JOLIU.territory
        using(util_id, state, year)
    )
    where state = :input_state
    order by county"""



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
def displayCO2(order, year, allyears): 
    #open connection
    dsn = cx_Oracle.makedsn("oracle.cise.ufl.edu", 1521, service_name="orcl")
    userpwd = "ApexLegend2020"
    connection = cx_Oracle.connect("vprater", userpwd, dsn, encoding="UTF-8")

    if allyears == True:
        start = 2013
        end = 2018
    else:
        start = year
        end = year + 1

    df = pd.read_sql(getCO2Query(order), con = connection, params = [year + 1, year, start, end])
    df.columns = ('terr_state', 'year', 'total_co2')
    df['total_co2'] = df.apply(
        lambda row: row['total_co2'] / 100000000, axis = 1
    )
    connection.close()

    lc = alt.Chart(df).mark_line().encode(
    alt.Y('total_co2:Q', scale=alt.Scale(zero=False)),
    x = 'year:O',
    color = 'terr_state:N'
    ).properties(
        width=600,
        height=400
    )
    st.altair_chart(lc)
   # st.write(df)

@st.cache
def getCO2State(states):
    return  """
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

def displayCO2byState(year_start, year_end, state1, state2, state3, state4, state5): 
    #open connection
    dsn = cx_Oracle.makedsn("oracle.cise.ufl.edu", 1521, service_name="orcl")
    userpwd = "ApexLegend2020"
    connection = cx_Oracle.connect("vprater", userpwd, dsn, encoding="UTF-8")

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


    df = pd.read_sql(getCO2State(state_sql), con = connection, params = [year_start, year_end])
    df.columns = ('s', 'y', 'total')
    connection.close()

    lc = alt.Chart(df).mark_line().encode(
    alt.Y('total:Q', scale=alt.Scale(zero=False)),
    x = 'y:O',
    color = 's:N'
    ).properties(
        width=600,
        height=400
    )
    st.altair_chart(lc)
    #st.write(df)



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

def displayReliability(): 
    #open connection
    dsn = cx_Oracle.makedsn("oracle.cise.ufl.edu", 1521, service_name="orcl")
    userpwd = "ApexLegend2020"
    connection = cx_Oracle.connect("vprater", userpwd, dsn, encoding="UTF-8")

    #State & county select
    dfState = pd.read_sql(getStates(), con = connection)
    state_select = st.selectbox('Select the state:', dfState['STATE'])
    dfCounty = pd.read_sql(getCounties(), con = connection, params=[state_select])
    county_select= st.selectbox('Select the county', dfCounty['COUNTY'])

    #read in reliability query
    df = pd.read_sql(getReliabilityQuery(), con = connection, params=[state_select, county_select])
    df_melted = df.melt(id_vars = [df.columns[0]], value_vars = [df.columns[1], df.columns[2]])

    #bar chart
    st.write(df_melted)
    bc = alt.Chart(df_melted).mark_bar().encode(
        x=df.columns[0] + ':O',
        y= 'value:Q',
        color='variable:N'
    ).properties(
        width=600,
        height=400
    )
    st.altair_chart(bc)

    connection.close()


   



#Streamlit Display
st.title = 'Interface Prototype'

#QUERY FOR CO2 for five best and five worst over one year
st.write('CO2 Change Over Time')
display_order = st.selectbox("",('Five best states', 'Five worst states'))
if display_order == 'Five best states':
    setChart = """asc"""
elif display_order == 'Five worst states':
    setChart = """desc"""


year_select = st.selectbox('for CO2 output improvement over the year', ('2013', '2014', '2015', '2016', '2017'))
if st.button('Get CO2 Trend'):    
    #show all years
    displayCO2(setChart, int(year_select), True)
    #show time selected
    displayCO2(setChart, int(year_select), False)

#QUERY FOR CO2 by state
st.write('Choose time period')
stateCO2_start_year = st.selectbox('From', ('2013', '2014', '2015', '2016', '2017'))
stateCO2_end_year = st.selectbox('To', ('2014', '2015', '2016', '2017', '2018'))

st.write('Choose display states')
stateCO2_state1 = st.selectbox('State 1', states)
stateCO2_state2 = st.selectbox('State 2', states)
stateCO2_state3 = st.selectbox('State 3', states)
stateCO2_state4 = st.selectbox('State 4', states)
stateCO2_state5 = st.selectbox('State 5', states)

if st.button('Get CO2 by State'):
    displayCO2byState(stateCO2_start_year, stateCO2_end_year, stateCO2_state1, stateCO2_state2, stateCO2_state3, stateCO2_state4, stateCO2_state5)

if st.button('Get Reliability Trends'):
    displayReliability()











