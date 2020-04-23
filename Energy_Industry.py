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
    st.subheader('Fuel Trends')
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
    st.subheader('CO2 changes for the better and worst')
    # QUERY FOR CO2 for five best and five worst over one year
    display_order = st.selectbox("", ('Five best states', 'Five worst states'))
    if display_order == 'Five best states':
        setChart = """asc"""
    elif display_order == 'Five worst states':
        setChart = """desc"""

    year_select = st.selectbox('for CO2 output improvement year start', ('2013', '2014', '2015', '2016', '2017'))
    year_select2 = st.selectbox('for CO2 output improvement year end', ('2014', '2015', '2016', '2017', '2018'))
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
    st.subheader('CO2 by state')
    # QUERY FOR CO2 by state

    stateCO2_start_year = st.selectbox('From', ('2013', '2014', '2015', '2016', '2017'))
    stateCO2_end_year = st.selectbox('To', ('2014', '2015', '2016', '2017', '2018'), 4)

    stateCO2_state1 = st.selectbox('State 1', states, 1)
    stateCO2_state2 = st.selectbox('State 2', states)
    stateCO2_state3 = st.selectbox('State 3', states)
    stateCO2_state4 = st.selectbox('State 4', states)
    stateCO2_state5 = st.selectbox('State 5', states)

    chart = displayCO2byState(connection, stateCO2_start_year, stateCO2_end_year,
                              stateCO2_state1, stateCO2_state2, stateCO2_state3,
                              stateCO2_state4, stateCO2_state5)
    st.altair_chart(chart)

    # cleanup
    connection.close()


def displayReliabilityCall():
    # initialize
    connection = cx_Oracle.connect("vprater", userpwd, dsn, encoding="UTF-8")

    # display
    st.subheader('Reliability Trends')
    chart = displayReliability(connection)
    st.altair_chart(chart)

    # cleanup
    connection.close()


def displaySalesCall():
    # initialize
    connection = cx_Oracle.connect("vprater", userpwd, dsn, encoding="UTF-8")

    # display
    st.subheader('Sales Trends')
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
