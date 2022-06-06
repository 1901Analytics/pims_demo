import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from PIL import Image
from datetime import date
import plotly.express as px
import matplotlib.pyplot as plt
from pims_database import *


st.set_page_config(layout="wide")

# Hide menu and streamlit footer
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
st.markdown(hide_menu_style, unsafe_allow_html = True)

# Initialize path - later change to AWS directory
# file_path = '/Volumes/Stark 1TB/MTSU_DSI/DataManagementDemo/'

image = Image.open('DSI.jpg')
st.image(image, width = 500)



# creates the sql alchemy engine to query a database
engine = return_engine()

# Data Entry, Analysis, and Retrieval
st.title('Data Entry Analysis and Retrieval (DEAR) Platform: PIMS Demo')

# Initialize first Session State for Role
if 'user_role' not in st.session_state:
    st.session_state.user_role = False

# Initialize second Session State for User ID
if 'user_id' not in st.session_state:
    st.session_state.user_id = False

# Initialize third Session State for choice of dataframe
if 'data_choice' not in st.session_state:
    st.session_state.data_choice = False

# Initialize fourth Session State for successful logins as Admin
if 'login_success' not in st.session_state:
    st.session_state.login_success = False

# Initialize fifth Session State for purpose of interaction with site
if 'user_purpose' not in st.session_state:
    st.session_state.user_purpose = False

# Initialize sixth Session State for the updated master data to use in retrieval and analysis
if 'data_master' not in st.session_state:
    st.session_state.data_master = pd.DataFrame()

# Initialize seventh Session State for the file download naming
if 'data_retrieval_selection' not in st.session_state:
    st.session_state.data_retrieval_selection = pd.DataFrame()

# Initialize eigth session state for calling database tables by name
if 'database_choice' not in st.session_state:
    st.session_state.database_choice = False

# Enter basic data
with st.sidebar.form(key = 'sidebar_form'):
    choice = st.selectbox('Choose your role', ['', 'Employee', 'Admin'])
    st.session_state.user_role = choice
    user_id = st.text_input('User ID')
    st.session_state.user_id = user_id
    sidebar_form_submit = st.form_submit_button(label = 'Submit')

# Setup program flow for different users, including Admin login
if st.session_state.user_role == 'Admin':
    with st.sidebar.form(key = 'admin_form', clear_on_submit = True):
        admin_password = st.text_input('Admin Password', type = 'password')
        login_form_submit = st.form_submit_button(label = 'Login')
        if login_form_submit:
            if admin_password == '12345':
                login_success = st.sidebar.success('You have successfully logged in as an administrator')
                st.session_state.login_success = True
            else:
                st.sidebar.warning('Incorrect login information entered')
    if st.session_state.login_success:

        # Create a logout button to log an admin out of the app
        if st.button('Logout from Admin role'):
            st.write('You are now logged out of the **Admin** role. Please log back in if you want to continue.')
            st.session_state.login_success = False
            st.stop()

if st.session_state.login_success:
    st.write('You are currently logged in as an **Admin**, be sure to click **Logout** if you would like to logout.')

    dataframe = st.selectbox('Select your data', ['', 'service area and consortium', 'prevalence', 'activities'])
    st.session_state.data_choice = dataframe
    st.session_state.user_purpose = st.selectbox('Section', ['', 'Data Entry', 'Data Analysis', 'Data Retrieval'])

if st.session_state.user_role == 'Employee':
    st.session_state.user_purpose = 'Data Entry'

    # Create a logout button to log an admin out of the app if they switch to employee w/o logging out first
    if st.session_state.login_success:
        st.write('You are still logged in as an **Admin**, be sure to click **Logout** if you would like to logout.')
        if st.button('Logout from Admin role'):
            st.write('You are now logged out of the **Admin** role. Please log back in if you want to continue.')
            st.session_state.login_success = False
            st.stop()

    dataframe = st.selectbox('Select your data for data entry as an Employee', ['', 'service area and consortium', 'prevalence', 'activities'])
    st.session_state.data_choice = dataframe

# Data entry section available to all users (employee and admin)
if st.session_state.user_purpose == 'Data Entry' and st.session_state.data_choice != '':
    with st.form(key = 'data_entry_form', clear_on_submit = True):
        st.write('Welcome to the Data Entry Page for the ' + st.session_state.data_choice + ' dataset.')
        #dataset = pd.read_csv(st.session_state.data_choice + '.csv') # Empty DF that sets up the column titles
        dataset = pd.DataFrame()

        # Based on dataset, enter new data and then submit it for addition to the master file.
        if st.session_state.data_choice == 'service area and consortium':
            service_area = st.text_input('Please enter your service area:')
            dataset['service_area'] = [service_area]
            state_list = ['TN', 'AL', 'KY', 'MS', 'OH', 'MO', 'GA']
            states = st.selectbox('Please enter the state serviced:', state_list)
            dataset['states_or_territories'] = [states]
            population = st.slider('Please enter the service area population:', 0, 10000000, 0)
            dataset['service_area_population'] = [population]
            hospital_cah = st.slider('Number of critical access hospitals', 0, 100, 0)
            dataset['moa_hospitals_critical_access'] = [hospital_cah]
            emergency = st.slider('Number of emergency medical services', 0, 100, 0)
            dataset['emergency_medical_services'] = [emergency]


        if st.session_state.data_choice == 'prevalence':
            non_fatal = st.slider('Number of non fatal opioid overdoses:', 0, 100, 0)
            dataset['number_non_fatal_opioid_overdoses'] = [non_fatal]
            reporting_issues = ['None', 'Data are reported above, but outdated', 'This is another option']
            non_fatal_issues = st.selectbox('Any issues with reporting non fatal data?', reporting_issues)
            dataset['issues_reporting_above_data_non_fatal'] = [non_fatal_issues]
            fatal = st.slider('Number of fatal opioid overdoses:', 0, 100, 0)
            dataset['number_fatal_opioid_overdoses'] = [fatal]
            fatal_issues = st.selectbox('Any issues with reporting fatal data?', reporting_issues)
            dataset['issues_reporting_above_data_fatal'] = [fatal_issues]
            prevalence_comments = st.text_input('Any additional comments?')
            dataset['prevalence_form_comments'] = [prevalence_comments]

        if st.session_state.data_choice == 'activities':
            sud = st.number_input('Enter the number screened for SUD', 0, 1000)
            dataset['number_screened_for_sud'] = [sud]
            reporting_issues = ['None', 'Data are reported above, but outdated', 'This is another option']
            sud_issues = st.selectbox('Any issues with reporting sud data?', reporting_issues)
            dataset['issues_reporting_above_data_sud'] = [sud_issues]
            subcommittees = st.selectbox('Creating subcommittees is included in your program.', ['False', 'True'])
            dataset['aiyp_creating_subcommittees'] = bool(subcommittees)
            reversal_reporting = st.selectbox('Overdose reversal reporting is included in your program.', ['False', 'True'])
            dataset['aiyp_overdose_reversal_reporting'] = bool(reversal_reporting)

        data_entry_form_submit = st.form_submit_button(label = 'Please confirm your data looks correct before clicking to update. '
                                                               'This submission is final and cannot be undone. Please only click once per submission.')

    # After submitting the data, we update the master file with the new info.
    # We then save the updated master file for each of the datasets.
    # This updated master data is available for Analysis and Retrieval
    if data_entry_form_submit:
        st.subheader('You have successfully entered your data')
        st.write('This is a preview of the data you have just entered')
        st.table(dataset)

        # Read in master (database) file with observations
        #master_data = st.session_state.data_choice

        # quick if/loop to move from prevalence to database table name pims_prevalence
        if st.session_state.data_choice == 'service area and consortium':
            st.session_state.database_choice = 'pims_service_area_and_consortium'
        elif st.session_state.data_choice == 'prevalence':
            st.session_state.database_choice = 'pims_prevalence'
        else:
            st.session_state.database_choice = 'pims_activities'

        master_data = get_data(engine, st.session_state.database_choice)
        st.write(master_data)
        # Append new entry to dataset
        master_data = master_data.append(dataset)
        st.write(master_data)

        # Save new entry to the database
        insert_to_db(dataset, engine, st.session_state.database_choice)

        # Create session_state variable for the full data that allows for subsequent analysis and exporting to personal
        st.session_state.data_master = master_data


        ### AFTER SUBMITTING ONE DATASET, ASK THE USER IF THEY WANT TO WORK ON ANOTHER.



if st.session_state.user_purpose == 'Data Analysis' and st.session_state.login_success:
    st.write('Welcome to the Data Analysis Page for the ' + st.session_state.data_choice + ' dataset.')
    #st.session_state.data_retrieval_selection = pd.read_csv(st.session_state.data_choice + '_master.csv')
    st.session_state.data_retrieval_selection = get_data(engine, st.session_state.database_choice)

    st.write('Here is an overview of the numerical variables within the ', st.session_state.data_choice, ' dataframe')
    st.dataframe(st.session_state.data_retrieval_selection.describe())
    viz_cols = st.session_state.data_retrieval_selection.columns

    # Create an expander for data selection and wrap in a form to submit all at once
    viz_expander = st.expander(label = 'Click to select visualization options')
    with viz_expander:
        interactive_viz = st.checkbox('Make my visualizations interactive')
        num_viz = st.slider('How many visualizations would you like to make?',0,4)

        with st.form(key = 'data_viz_form'):

            viz_col1, viz_col2 = st.columns(2)

            if num_viz == 1:
                with viz_col1:
                    var1 = st.selectbox('Select the 1st variable you want to examine', viz_cols)
                with viz_col2:
                    viz1 = st.selectbox('Select the 1st type of visualization you would like', ['bar', 'line', 'scatter/area'])

            if num_viz == 2:
                with viz_col1:
                    var1 = st.selectbox('Select the 1st variable you want to examine', viz_cols)
                    var2 = st.selectbox('Select the 2nd variable you want to examine', viz_cols)
                with viz_col2:
                    viz1 = st.selectbox('Select the 1st type of visualization you would like', ['bar', 'line', 'scatter/area'])
                    viz2 = st.selectbox('Select the 2nd type of visualization you would like', ['bar', 'line', 'scatter/area'])

            if num_viz == 3:
                with viz_col1:
                    var1 = st.selectbox('Select the 1st variable you want to examine', viz_cols)
                    var2 = st.selectbox('Select the 2nd variable you want to examine', viz_cols)
                    var3 = st.selectbox('Select the 3rd variable you want to examine', viz_cols)
                with viz_col2:
                    viz1 = st.selectbox('Select the 1st type of visualization you would like', ['bar', 'line', 'scatter/area'])
                    viz2 = st.selectbox('Select the 2nd type of visualization you would like', ['bar', 'line', 'scatter/area'])
                    viz3 = st.selectbox('Select the 3rd type of visualization you would like', ['bar', 'line', 'scatter/area'])

            if num_viz == 4:
                with viz_col1:
                    var1 = st.selectbox('Select the 1st variable you want to examine', viz_cols)
                    var2 = st.selectbox('Select the 2nd variable you want to examine', viz_cols)
                    var3 = st.selectbox('Select the 3rd variable you want to examine', viz_cols)
                    var4 = st.selectbox('Select the 4th variable you want to examine', viz_cols)
                with viz_col2:
                    viz1 = st.selectbox('Select the 1st type of visualization you would like', ['bar', 'line', 'scatter/area'])
                    viz2 = st.selectbox('Select the 2nd type of visualization you would like', ['bar', 'line', 'scatter/area'])
                    viz3 = st.selectbox('Select the 3rd type of visualization you would like', ['bar', 'line', 'scatter/area'])
                    viz4 = st.selectbox('Select the 4th type of visualization you would like', ['bar', 'line', 'scatter/area'])

            data_viz_form_submit = st.form_submit_button(label = 'Click to generate visualizations')

    if data_viz_form_submit:
        if not interactive_viz:
            if num_viz == 1 or num_viz == 2 or num_viz == 3 or num_viz == 4:

                # Full visualization for first var
                if viz1 == 'bar':
                    st.bar_chart(st.session_state.data_retrieval_selection[var1])
                if viz1 == 'line':
                    st.line_chart(st.session_state.data_retrieval_selection[var1])
                if viz1 == 'scatter/area':
                    st.area_chart(st.session_state.data_retrieval_selection[var1])

            if num_viz == 2 or num_viz == 3 or num_viz == 4:
                # Basic visualization for var2 and viz2
                if viz2 == 'bar':
                    st.bar_chart(st.session_state.data_retrieval_selection[var2])
                if viz2 == 'line':
                    st.line_chart(st.session_state.data_retrieval_selection[var2])
                if viz2 == 'scatter/area':
                    st.area_chart(st.session_state.data_retrieval_selection[var2])

            if num_viz == 3 or num_viz == 4:
                # Basic visualization for var3 and viz3
                if viz3 == 'bar':
                    st.bar_chart(st.session_state.data_retrieval_selection[var3])
                if viz3 == 'line':
                    st.line_chart(st.session_state.data_retrieval_selection[var3])
                if viz3 == 'scatter/area':
                    st.area_chart(st.session_state.data_retrieval_selection[var3])

            if num_viz == 4:
                # Basic visualization for var4
                if viz4 == 'bar':
                    st.bar_chart(st.session_state.data_retrieval_selection[var4])
                if viz4 == 'line':
                    st.line_chart(st.session_state.data_retrieval_selection[var4])
                if viz4 == 'scatter/area':
                    st.area_chart(st.session_state.data_retrieval_selection[var4])

        if interactive_viz:
            if num_viz == 1 or num_viz == 2 or num_viz == 3 or num_viz == 4:

                # Full visualization for first var
                if viz1 == 'bar':
                    ibar_fig = px.bar(st.session_state.data_retrieval_selection, y = st.session_state.data_retrieval_selection[var1])
                    st.plotly_chart(ibar_fig)
                if viz1 == 'line':
                    iline_fig = px.line(st.session_state.data_retrieval_selection, y = st.session_state.data_retrieval_selection[var1])
                    st.plotly_chart(iline_fig)
                if viz1 == 'scatter/area':
                    iscatter_fig = px.scatter(st.session_state.data_retrieval_selection, y = st.session_state.data_retrieval_selection[var1])
                    st.plotly_chart(iscatter_fig)

            if num_viz == 2 or num_viz == 3 or num_viz == 4:
                # Basic visualization for var2 and viz2
                if viz2 == 'bar':
                    ibar_fig = px.bar(st.session_state.data_retrieval_selection, y = st.session_state.data_retrieval_selection[var2])
                    st.plotly_chart(ibar_fig)
                if viz2 == 'line':
                    iline_fig = px.line(st.session_state.data_retrieval_selection, y = st.session_state.data_retrieval_selection[var2])
                    st.plotly_chart(iline_fig)
                if viz2 == 'scatter/area':
                    iscatter_fig = px.scatter(st.session_state.data_retrieval_selection, y = st.session_state.data_retrieval_selection[var2])
                    st.plotly_chart(iscatter_fig)

            if num_viz == 3 or num_viz == 4:
                # Basic visualization for var3 and viz3
                if viz3 == 'bar':
                    ibar_fig = px.bar(st.session_state.data_retrieval_selection, y=st.session_state.data_retrieval_selection[var3])
                    st.plotly_chart(ibar_fig)
                if viz3 == 'line':
                    iline_fig = px.line(st.session_state.data_retrieval_selection, y = st.session_state.data_retrieval_selection[var3])
                    st.plotly_chart(iline_fig)
                if viz3 == 'scatter/area':
                    iscatter_fig = px.scatter(st.session_state.data_retrieval_selection, y = st.session_state.data_retrieval_selection[var3])
                    st.plotly_chart(iscatter_fig)

            if num_viz == 4:
                # Basic visualization for var4
                if viz4 == 'bar':
                    ibar_fig = px.bar(st.session_state.data_retrieval_selection, y = st.session_state.data_retrieval_selection[var4])
                    st.plotly_chart(ibar_fig)
                if viz4 == 'line':
                    iline_fig = px.line(st.session_state.data_retrieval_selection, y = st.session_state.data_retrieval_selection[var4])
                    st.plotly_chart(iline_fig)
                if viz4 == 'scatter/area':
                    iscatter_fig = px.scatter(st.session_state.data_retrieval_selection, y = st.session_state.data_retrieval_selection[var4])
                    st.plotly_chart(iscatter_fig)

# Allow Admin users one click access to download their data as an excel file.
if st.session_state.user_purpose == 'Data Retrieval' and st.session_state.login_success:
    st.write('Welcome to the Data Retrieval Page for the ' + st.session_state.data_choice + ' dataset.')
    #st.session_state.data_retrieval_selection = pd.read_csv(st.session_state.data_choice + '_master.csv')
    st.session_state.data_retrieval_selection = get_data(engine, st.session_state.database_choice)
    st.dataframe(st.session_state.data_retrieval_selection.tail())
    today = date.today()

    def to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        format1 = workbook.add_format({'num_format': '0.00'})
        worksheet.set_column('A:A', None, format1)
        writer.save()
        processed_data = output.getvalue()
        return processed_data

    df_xlsx = to_excel(st.session_state.data_retrieval_selection)

    download_data_button = st.download_button('Press to save the updated file to your computer', df_xlsx,
                       str(st.session_state.database_choice) + '_master_' + str(today) + '.xlsx')

