import requests
import pandas as pd
from datetime import datetime, date
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dateutil.relativedelta


import streamlit as st


st.set_page_config(
    page_title="MYR Exchange Rate",
    page_icon=(":heavy_dollar_sign:"),
    # layout="wide",
    # initial_sidebar_state="auto",
)
list_of_currencies = [
    'USD',
 'AUD',
 'EUR',
 'GBP',
 'CAD',
 'JPY',
 'INR',
 'SGD',
]

# https://docs.streamlit.io/en/stable/api.html?highlight=cache#streamlit.cache
@st.cache(ttl=60*60*1, suppress_st_warning=True)
def get_rate():
    latest_forex_dict = {}
    api_progress = st.progress(0)
    api_count = 0
    for cur in list_of_currencies:
        list_of_df = []

        this_month = datetime.now()
        last_month = this_month - dateutil.relativedelta.relativedelta(months=1)
        for eac_date in [last_month, this_month]: # Scrap this month and last month
            response = requests.get(f"https://api.bnm.gov.my/public/exchange-rate/"+cur.lower()+"/year/"+str(eac_date.year)+"/month/"+str(eac_date.month)+"?session=1200&quote=rm",
            headers={
            "Accept": "application/vnd.BNM.API.v1+json",
            }
            )
            try:
                eac_df = pd.DataFrame(response.json()['data']['rate'])
                list_of_df.append(eac_df)
            except:
                st.write(response.json())

            api_count += 1
            api_progress.progress(api_count/(len(list_of_currencies)*2))
        

        df = pd.concat(list_of_df)
        df['date'] = pd.to_datetime(df['date'])
        latest_forex_dict[cur] = df
    api_progress.empty()
    return latest_forex_dict

@st.cache(ttl=60*60*1, suppress_st_warning=True)
def get_compare_rate(currency1,currency2,start_date,end_date):


    try:
        forex_compare_dict = {}
        api_progress = st.progress(0)
        api_count = 0
        api_caption = st.empty()
        for cur in [currency1,currency2]:
            list_of_df = []

            for eac_date in months_between(start_date,end_date):
                api_caption.caption("Getting " + cur +" "+ str(eac_date))
                response = requests.get(f"https://api.bnm.gov.my/public/exchange-rate/"+cur.lower()+"/year/"+str(eac_date.year)+"/month/"+str(eac_date.month)+"?session=1200&quote=rm",
                headers={
                "Accept": "application/vnd.BNM.API.v1+json",
                }
                )
                try:
                    eac_df = pd.DataFrame(response.json()['data']['rate'])
                    list_of_df.append(eac_df)
                except:
                    st.write(response.json())
                api_count += 1
                api_progress.progress(api_count/(sum(1 for _ in months_between(start_date, end_date))*2))
            df = pd.concat(list_of_df)
            df['date'] = pd.to_datetime(df['date'])
            forex_compare_dict[cur] = df
    except ValueError:
        forex_compare_dict = {}
        api_progress = st.progress(0)
        api_count = 0
        api_caption = st.empty()
        start_date = start_date + dateutil.relativedelta.relativedelta(months=-1)
        end_date = end_date + dateutil.relativedelta.relativedelta(months=-1)
        for cur in [currency1,currency2]:
            list_of_df = []

            for eac_date in months_between(start_date,end_date):
                api_caption.caption("Getting " + cur +" "+ str(eac_date))
                response = requests.get(f"https://api.bnm.gov.my/public/exchange-rate/"+cur.lower()+"/year/"+str(eac_date.year)+"/month/"+str(eac_date.month)+"?session=1200&quote=rm",
                headers={
                "Accept": "application/vnd.BNM.API.v1+json",
                }
                )
                try:
                    eac_df = pd.DataFrame(response.json()['data']['rate'])
                    list_of_df.append(eac_df)
                except:
                    st.write(response.json())
                api_count += 1
                api_progress.progress(api_count/(sum(1 for _ in months_between(start_date, end_date))*2))
            df = pd.concat(list_of_df)
            df['date'] = pd.to_datetime(df['date'])
            forex_compare_dict[cur] = df
        
    api_progress.empty()
    api_caption.empty()
    return forex_compare_dict


#### function to get months between two dates
def months_between(start_date, end_date):
    """
    Given two instances of ``datetime.date``, generate a list of dates on
    the 1st of every month between the two dates (inclusive).

    e.g. "5 Jan 2020" to "17 May 2020" would generate:

        1 Jan 2020, 1 Feb 2020, 1 Mar 2020, 1 Apr 2020, 1 May 2020

    """
    if start_date > end_date:
        raise ValueError(f"Start date {start_date} is not before end date {end_date}")

    year = start_date.year
    month = start_date.month

    while (year, month) <= (end_date.year, end_date.month):
        yield date(year, month, 1)

        # Move to the next month.  If we're at the end of the year, wrap around
        # to the start of the next.
        #
        # Example: Nov 2017
        #       -> Dec 2017 (month += 1)
        #       -> Jan 2018 (end of year, month = 1, year += 1)
        #
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1


def create_tabs(list_of_tabs, default_tab=0):
    st.markdown(
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">',
        unsafe_allow_html=True,
    )
    query_params = st.experimental_get_query_params()
    # tabs = ["POS Terminal", "CCRIS database", "Contact","st forms"]
    tabs = list_of_tabs
    if "tab" in query_params:
        active_tab = query_params["tab"][0]
    else:
        active_tab = list_of_tabs[default_tab]

    if active_tab not in tabs:
        st.experimental_set_query_params(tab="Home")
        active_tab = list_of_tabs[default_tab]

    li_items = "".join(
        f"""
        <li class="nav-item">
            <a class="nav-link{' active' if t==active_tab else ''}" href="/?tab={t}">{t}</a>
        </li>
        """
        for t in tabs
    )
    tabs_html = f"""
        <ul class="nav nav-tabs">
        {li_items}
        </ul>
    """

    st.markdown(tabs_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    return active_tab

# -------------------------------------------------------------------------------
# Introduction
# ------------------------------------------------------------------------------
st.header("MYR Foreign Currency Exchange Rate")
latest_forex_dict = get_rate()

# active_tab = create_tabs(
#     ["Exchange Rate", "About"],
#     default_tab=0,
# )

st.write(
    f"""<span style="color:#FFF8DC;font-size:22px"> Latest exchange rate as of <b>"""+ latest_forex_dict["USD"]['date'].iloc[-1].strftime("%d %B %Y")+ """, 12pm</b> </span> """,
    unsafe_allow_html=True,
    )

# -------------------------------------------------------------------------------
# Metric
# ------------------------------------------------------------------------------
# st.metric(label="Temperature", value="70 °F", delta="1.2 °F")
# st.write(latest_forex_dict.keys())
cols = st.columns(4)

for lst in [list_of_currencies[:4], list_of_currencies[4:]]:
    for col_ind, cur in enumerate(lst):
        temp_df = latest_forex_dict[cur].copy()
        latest_value = temp_df['middle_rate'].iloc[-1]
        previous_value = temp_df['middle_rate'].iloc[-2]
        cols[col_ind].metric(label=cur, value="{:.2f}".format(round(latest_value,2)), delta = "{:.3f}".format(round(latest_value-previous_value,3)) )

st.write("***")
# -------------------------------------------------------------------------------
# Trend
# ------------------------------------------------------------------------------
st.subheader('Show latest exchange rate trend')
selected_currency = st.selectbox("Select a currency to view exchange rate trend:",list_of_currencies, 0)

chosen_df = latest_forex_dict[selected_currency]

fig = go.Figure()
fig.add_trace(go.Scatter(x=chosen_df['date'], y=chosen_df['middle_rate'], 
    mode='lines', name = "middle_rate", line_color="cyan",showlegend=False))


fig.add_trace(go.Scatter(x=chosen_df['date'], y=chosen_df['buying_rate'], 
    line_dash='dot', name = "buying_rate",fill='tonexty',line_width=1,
    line_color="grey",showlegend=False))

fig.add_trace(go.Scatter(x=chosen_df['date'], y=chosen_df['selling_rate'], 
    line_dash='dot', name = "selling_rate",fill='tonexty',line_width=0.3,
    line_color="grey",showlegend=False))

fig.update_layout(title={
            'text': 'MYR exchange rate against '+ selected_currency,
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
            },
            hovermode='x',
            # yaxis = {
            #     'showticklabels':False
            # },
#             xaxis_title = 'Month',
#             yaxis_title = 'Rate (%)',
            # margin={"r":0,"t":80,"l":30,"b":0},
            # height=600,width=1200,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            )
fig.update_xaxes(showgrid=False, zeroline=False)
fig.update_yaxes(showgrid=False, zeroline=False)
st.plotly_chart(fig,use_container_width=True)


#### Download to csv
#### First combine all df
list_to_csv = []
for cur in latest_forex_dict.keys():
    temp_df = latest_forex_dict[cur].copy()
    temp_df.columns = [cur + '_' + col if 'rate' in col else col for col in temp_df.columns]
    list_to_csv.append(temp_df)
main_df = pd.DataFrame(data={'date':[]})
for df in list_to_csv:
    main_df =main_df.merge(df,on='date',how='outer')

st.download_button(
    label="Download latest exchange rate into csv",
    data=main_df.set_index('date').to_csv().encode('utf-8'),
    file_name="latest_exchange_rate.csv",
    mime="text/csv"
)
st.write("***")

# -------------------------------------------------------------------------------
# Comparison between two 
# ------------------------------------------------------------------------------
st.subheader("Compare exchange rate trend")
with st.form("Compare"):
    currency1 = st.selectbox("Select one currency to compare:",list_of_currencies, 0)
    currency2 = st.selectbox("Select another currency to compare:",list_of_currencies, 3)
    selected_date_range = st.date_input("Filter Date", value=[datetime.now().replace(day=1), datetime.now()],min_value=pd.to_datetime("1 Jan 2021"),max_value=datetime.now(), help = "Select date range to plot")
    st.form_submit_button("Compare and Plot!")

start_date, end_date = selected_date_range
# st.write(start_date)
# st.write(end_date)

forex_compare_dict = get_compare_rate(currency1,currency2,start_date,end_date)
fig = make_subplots(specs=[[{"secondary_y": True}]])



fig.add_trace(go.Scatter(x=forex_compare_dict[currency1]['date'], y=forex_compare_dict[currency1]['middle_rate'], 
    mode='lines', name = currency1+ " (LHS)", line_color="#FFA15A"))
fig.add_trace(go.Scatter(x=forex_compare_dict[currency2]['date'], y=forex_compare_dict[currency2]['middle_rate'], 
    mode='lines', name = currency2 + " (RHS)", line_color="#FF97FF"),secondary_y=True)

fig.update_layout(title={
            'text': 'MYR exchange rate against '+ currency1 +" and " + currency2,
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
            },
            hovermode='x',
            # yaxis = {
            #     'showticklabels':False
            # },
#             xaxis_title = 'Month',
#             yaxis_title = 'Rate (%)',
            # margin={"r":0,"t":80,"l":30,"b":0},
            height=500,
            # width=200,
            legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            )
fig.update_yaxes(title_text=currency1, secondary_y=False)
fig.update_yaxes(title_text= currency2, secondary_y=True)
fig.update_xaxes(showgrid=False, zeroline=False)
fig.update_yaxes(showgrid=False, zeroline=False)
st.plotly_chart(fig,use_container_width=True)


#### Download to csv
#### First combine all df
list_to_csv = []
for cur in forex_compare_dict.keys():
    temp_df = forex_compare_dict[cur].copy()
    temp_df.columns = [cur + '_' + col if 'rate' in col else col for col in temp_df.columns]
    list_to_csv.append(temp_df)
main_df = pd.DataFrame(data={'date':[]})
for df in list_to_csv:
    main_df =main_df.merge(df,on='date',how='outer')

st.download_button(
    label="Download filtered exchange rate into csv",
    data=main_df.set_index('date').to_csv().encode('utf-8'),
    file_name="filtered_exchange_rate.csv",
    mime="text/csv"
)

st.write("***")

with st.expander("About this page"):
    st.markdown("Exchange rate on this page is taken from [BNM Open API](https://api.bnm.gov.my/explorer). \
        \nThese rates are from the Interbank Foreign Exchange Market in Kuala Lumpur as at 12pm daily")