import streamlit as st
import pandas as pd
import altair as alt
import datetime


@st.cache
def getFuelTypesQuery():
    return """select * from JOLIU.aer_fuel_type"""


@st.cache
def getFuelTrendQuery(yesFuel, noFuel):
    return """
    with t1 as
        (
            (
            select * from joliu.mo_prod_consum
            )
            union
            (
            select * from cboger.mo_prod_consum
            )
        )
    select fuel_type_code, year, month, count(*) from
        (
        select fuel_type_code, year, month, util_id from
                    (
                    select * from t1 
                    inner join joliu.plant
                    using(plant_id)
                    where """ + yesFuel + """
                    )
        minus
            (
            select distinct * from
                (
                select fuel_type_code, year, month, util_id from
                            (
                            select * from joliu.mo_prod_consum 
                            inner join joliu.plant
                            using(plant_id)
                            where """ + noFuel + """
                            )
                )
            )
        )
    group by fuel_type_code, year, month
    order by fuel_type_code, year, month"""

def getFuelQuery(yesFuel,noFuel):
    return """
        with t1 as
            (
                (
                select * from joliu.mo_prod_consum
                )
                union
                (
                select * from cboger.mo_prod_consum
                )
            )
        select aer_fuel_type_code, year, month, count(*) as Total from
            (
            select aer_fuel_type_code, year, month, util_id from
                        (
                        select * from t1
                        inner join joliu.plant
                        using(plant_id)
                        inner join joliu.fuel_type
                        on (t1.fuel_type_code = fuel_type.fuel_type_code)
                        where """ + yesFuel + """
                        )
            minus
                (
                select distinct * from
                    (
                    select aer_fuel_type_code, year, month, util_id from
                                (
                                select * from joliu.mo_prod_consum
                                inner join joliu.plant using(plant_id)
                                inner join joliu.fuel_type using (fuel_type_code)
                                inner join joliu.aer_fuel_type using(aer_fuel_type_code)
                                where """ + noFuel + """
                                )
                    )
                )
            )
        group by aer_fuel_type_code, year, month
        order by aer_fuel_type_code, year, month
    """


def returnFuelSQL(names):
    fuelSQL = """"""
    nofuelSQL = """"""
    fuelLookup = {
        'Solar': 'SUN',
        'Coal': 'COL',
        'Geothermal': 'GEO',
        'Natural Gas': 'NG',
        'Nuclear': 'NUC',
        'Wind': 'WND'
    }

    for i in names:
        fuelSQL += """aer_fuel_type_code = '""" + fuelLookup[i] + "'"
        nofuelSQL += """aer_fuel_type_code != '""" + fuelLookup[i] + "'"
        if i != names[-1]:
            fuelSQL += " OR "
            nofuelSQL += " AND "

    return fuelSQL, nofuelSQL


def getFuelTrend(connection, fuelTypes):
    dfFuelTypes = pd.read_sql(getFuelTypesQuery(), con=connection)
    dfFuelTypes.columns = ('code', 'desc')

    (yesSQL, noSQL) = returnFuelSQL(fuelTypes)

    # query
    query = getFuelQuery(yesSQL, noSQL)
    dfFuel = pd.read_sql(query, con=connection)
    dfFuel.columns = ('Fuel', 'year', 'month', '# of Utilities')
    dfFuel['Date'] = pd.to_datetime(dfFuel[['year', 'month']].assign(day=1))

    lcFuel = alt.Chart(dfFuel).mark_line().encode(
        alt.Y('# of Utilities:Q', scale=alt.Scale(zero=False)),
        x = 'yearmonth(Date):O',
        color='Fuel'
    ).properties(
        width=700,
        height=400
    )

    return lcFuel, query
