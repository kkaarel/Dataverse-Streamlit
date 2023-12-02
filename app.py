import http.client
import json
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Sales trial dataverse account",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

url = st.secrets["url"]

def get_token():

    accesstoken = ''

    try:

        client_id = st.secrets["client_id"]
        client_secret = st.secrets["client_secret"]
        tenant_id = st.secrets["tenant_id"]


        conn = http.client.HTTPSConnection("login.microsoftonline.com")

        # print(conn)

        payload = 'grant_type=client_credentials&client_id={}&client_secret={}&scope=https://{}.crm4.dynamics.com/.default'.format(
            client_id, client_secret, url)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        getbearer = conn.request(
            "GET", "/{}/oauth2/v2.0/token".format(tenant_id), payload, headers)

        res = conn.getresponse()
        # print(res)

        data = res.read()
        # print(data)

        data_json = json.loads(data.decode("utf-8"))

        accesstoken = data_json['access_token']
    except KeyError:

        # handle any missing key errors
        print('Could not get access token')
    return accesstoken

def get_account():

    account = "https://{}.api.crm4.dynamics.com/api/data/v9.2/accounts?$select=description,name,revenue_base,creditlimit,address1_stateorprovince,openrevenue,creditlimit_base".format(
        url)

    accesstoken = get_token()
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=utf-8'

    }
    response_data = json.loads(requests.get(
        account, headers=headers).text)
    df = pd.json_normalize(response_data['value'])

    return df

def kpis(df):

    kpi1 = df['creditlimit'].sum()
    kpi2 = df['creditlimit_base'].sum()

    col1, col2, = st.columns(2)

    # Display KPIs in the columns
    with col1:
        st.subheader('Credit limit')
        st.write(f"<p style='font-size:44px; color:#4fb443;'>{kpi1}</p>", unsafe_allow_html=True)

    with col2:
        st.subheader('Credit base')
        st.write(f"<p style='font-size:44px; color:#4fb443;'>{kpi2}</p>", unsafe_allow_html=True)


st.header('Dataverse streamlit demo for account', divider='rainbow')

kpis(get_account())

st.dataframe(get_account()) 