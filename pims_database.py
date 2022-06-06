import streamlit as st
from sqlalchemy import *
import pandas as pd


### SETTING UP THE DATABASE LOGIN
def return_engine():
    # build engine url
    user = st.secrets["username"]
    pwd = st.secrets["password"]
    host = st.secrets["host"]
    engine_url = f"postgresql+psycopg2://{user}:{pwd}@{host}/dear_database"
    # creates the sql alchemy engine to query a database
    return create_engine(engine_url)

engine = return_engine()

### DEFINE DATABASE TABLES

# defined all of the different tables in the database
meta = MetaData()

pims_service_area_and_consortium = Table('pims_service_area_and_consortium', meta,
                    Column('service_area', String),
                    Column('states_or_territories', String),
                    Column('service_area_population', Integer),
                    Column('moa_hospitals_critical_access', Integer),
                    Column('emergency_medical_services', Integer))

pims_prevalence = Table('pims_prevalence', meta,
                  Column('number_non_fatal_opioid_overdoses', Integer),
                  Column('issues_reporting_above_data_non_fatal', String),
                  Column('number_fatal_opioid_overdoses', Integer),
                  Column('issues_reporting_above_data_fatal', String),
                  Column('prevalence_form_comments', String))

pims_activities = Table('pims_activities', meta,
                  Column('number_screened_for_sud', Integer),
                  Column('issues_reporting_above_data_sud', String),
                  Column('aiyp_creating_subcommittees', Boolean),
                  Column('aiyp_overdose_reversal_reporting', Boolean))

meta.create_all(engine)

### APPENDING NEWLY ENTERED DATA TO DATABASE

def insert_to_db(df, _engine, table_name):
    # this is an example of how to insert a pandas dataframe into a postgres database
    # you will need to ensure the dataframe column names match exactly what is in the database
    with _engine.connect() as conn:
        df.to_sql(name=table_name, schema="public", if_exists="append", index=False, con=conn)



# queries the database
@st.experimental_memo(ttl=1) # Set this to the value of seconds until database is refreshed/updated with data
def get_data(_engine, table_name):

    query = f"""
    select * 
    from dear_database.public.{table_name}
    """

    with engine.connect() as conn:
        queried_df = pd.read_sql(query, con=conn)

    return queried_df
