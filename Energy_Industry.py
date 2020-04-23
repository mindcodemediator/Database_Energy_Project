# imports
import streamlit as st
import cx_Oracle
from Energy_reliability import *
from Energy_CO2 import *
from Energy_fuel import *
from Energy_sales import *
from Energy_reliability import *
from PIL import Image

# vars
states = ["""""", """AL""", """AK""", """AZ""", """AR""", """CA""", """CO""", """CT""", """DE""", """FL""", """GA""",
          """HI""", """ID""", """IL""", """IN""", """IA""", """KS""", """KY""", """LA""", """ME""", """MD""", """MA""",
          """MI""", """MN""", """MS""", """MO""", """MT""", """NE""", """NV""", """NH""", """NJ""", """NM""", """NY""",
          """NC""", """ND""", """OH""", """OK""", """OR""", """PA""", """RI""", """SC""", """SD""", """TN""", """TX""",
          """UT""", """VT""", """VA""", """WA""", """WV""", """WI""", """WY"""]

# Oracle connection
dsn = cx_Oracle.makedsn("oracle.cise.ufl.edu", 1521, service_name="orcl")
userpwd = "ApexLegend2020"

#################
# Functions
#################
def getFuelTrendCall():
    # initialize
    connection = cx_Oracle.connect("vprater", userpwd, dsn, encoding="UTF-8")

    # display
    fuelTypes = st.multiselect('Select Fuel Type',
                                       ('Solar', 'Geothermal', 'Coal', 'Natural Gas', 'Nuclear', 'Wind'), 'Solar')
    # if st.button('Get Fuel Trends'):
    st.subheader('Number of Utilities that use a Given Fuel Exclusively')
    if len(fuelTypes) >= 1:
        (chart, query) = getFuelTrend(connection, fuelTypes)
        st.altair_chart(chart)
        st.code(query, language='sql')

    # cleanup
    connection.close()


def displayCO2Call():
    #initialize
    connection = cx_Oracle.connect("vprater", userpwd, dsn, encoding="UTF-8")

    # display
    st.subheader('Best/Worst CO2 Emissions Net Change')
    # QUERY FOR CO2 for five best and five worst over one year
    display_order = st.selectbox("", ('Five best states', 'Five worst states'))
    if display_order == 'Five best states':
        setChart = """asc"""
    elif display_order == 'Five worst states':
        setChart = """desc"""

    year_select = st.selectbox('Comparison- Year Start:', ('2013', '2014', '2015', '2016', '2017'))
    year_select2 = st.selectbox('Comparison- Year End:', ('2014', '2015', '2016', '2017', '2018'))
    # show all years
    chartone = displayCO2(connection, setChart, int(year_select),int(year_select2), True)
    # show time selected
    charttwo = displayCO2(connection, setChart, int(year_select),int(year_select2), False)
    st.altair_chart(chartone)
    st.altair_chart(charttwo)

    # cleanup
    connection.close()


def displayCO2byStateCall():
    # initialize
    connection = cx_Oracle.connect("vprater", userpwd, dsn, encoding="UTF-8")

    # display
    st.subheader('State CO2 Emissions Comparison Tool')
    # QUERY FOR CO2 by state

    st.markdown('**Select Year Range**')
    stateCO2_start_year = st.selectbox('Start Year', ('2013', '2014', '2015', '2016', '2017'))
    stateCO2_end_year = st.selectbox('End Year', ('2014', '2015', '2016', '2017', '2018'), 4)
    st.markdown('**Select States to Compare**')
    stateCO2_state1 = st.selectbox('State 1', states, 1)
    stateCO2_state2 = st.selectbox('State 2', states)
    stateCO2_state3 = st.selectbox('State 3', states)
    stateCO2_state4 = st.selectbox('State 4', states)
    stateCO2_state5 = st.selectbox('State 5', states)

    chartone = displayCO2byState(connection, stateCO2_start_year, stateCO2_end_year,
                              stateCO2_state1, stateCO2_state2, stateCO2_state3,
                              stateCO2_state4, stateCO2_state5)

    charttwo = displayNormalizedCO2(connection, stateCO2_start_year, stateCO2_end_year,
                                 stateCO2_state1, stateCO2_state2, stateCO2_state3,
                                 stateCO2_state4, stateCO2_state5)


    st.markdown('**Gross Tons CO2 Produced**')
    st.altair_chart(chartone)
    st.markdown('**Normalized Lbs CO2 Produced**')
    st.altair_chart(charttwo)

    map_year = st.selectbox('Select Year for CO2 Map', ('2013', '2014', '2015', '2016', '2017', '2018'))
    st.markdown('**Normalized Lbs CO2 Produced Choropleth Map**')
    chartthree = makeMeAFreakingMap(connection, map_year)
    st.altair_chart(chartthree)

    # cleanup
    connection.close()


def displayReliabilityCall():
    # initialize
    connection = cx_Oracle.connect("vprater", userpwd, dsn, encoding="UTF-8")

    # display
    st.subheader('Outage Trends (With and Without Major Events)')
    chart = displayReliability(connection)
    st.altair_chart(chart)

    # cleanup
    connection.close()


def displaySalesCall():
    # initialize
    connection = cx_Oracle.connect("vprater", userpwd, dsn, encoding="UTF-8")

    # display
    st.subheader('Residential Power Revenue per County')
    chart = displaySales(connection)
    st.altair_chart(chart)

    # cleanup
    connection.close()


#######################
# Sidebar menu#
#######################
# imports

# Streamlit Display
st.title = 'Energy Industry'
image = Image.open('database_project_banner.jpg')
st.image(image, use_column_width=True)

# functions
functionDict = {
    'Fuel Utilization': getFuelTrendCall,
    'CO2 Change': displayCO2Call,
    'CO2 State Comparison': displayCO2byStateCall,
    'Grid Reliability': displayReliabilityCall,
    'Sales': displaySalesCall
}
menu = st.sidebar.radio('Pick a topic', ('Fuel Utilization', 'CO2 Change', 'CO2 State Comparison', 'Grid Reliability','Sales'))

functionCall = functionDict[menu]
functionCall()
