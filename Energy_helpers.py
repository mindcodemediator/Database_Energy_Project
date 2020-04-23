

#Helper functions used by multiple modules
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
