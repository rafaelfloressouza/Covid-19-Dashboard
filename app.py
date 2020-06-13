import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import constants as const
import data
import ast
import pandas as pd
from datetime import datetime as dt
import graph_generator as graph_gen
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

# Initializing the web application.
app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])

# Navigation bar

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Countries", href="#")),
        dbc.NavItem(dbc.NavLink("World", href="#")),
    ],
    brand=("COVID-19 Dashboard"),
    brand_style=dict(fontSize=30),
    brand_href="#",
    color="primary",
    fluid=True,
    dark=True,
)

# Dropdowns

country_dropdown = dcc.Dropdown(
    id='countries-dropdown',
    options=const.COUNTRY_DROPDOWN,
    value='united-states',
    clearable=False,
)

graph_dropdown = dcc.Dropdown(
    id='graphs-dropdown',
    options=const.GRAPH_DROPDOWN_OPTIONS,
    value=const.GRAPH_TYPE.SCATTER_TOTAL_CASES,
    clearable=False
)

# Tabs

summary_tab = dbc.Card(
    dbc.CardBody(
        [
            html.H4('Total Cases', id='total_cases_in_table',
                    className="card-text", ),
            html.H4('Total Deaths', id='total_deaths_in_table',
                    className="card-text", ),
            html.H4('Total Recovered ', id='total_recovered_in_table',
                    className="card-text", ),
            html.H4('Recovery Rate', id='recovery_rate_in_table',
                    className="card-text", ),
            html.H4('Death Rate', id='death_rate_in_table',
                    className="card-text", ),
        ], style={'text-align': 'center', 'background': const.PRIMARY_HEX}
    ), style=dict(background='white')
)

overview_tab = dbc.Card(
    dbc.CardBody(
        [
            dcc.DatePickerSingle(
                id='overview-date-picker',
                initial_visible_month=dt.now(),
                placeholder='Select Date',
                display_format='MMM Do, YY',
                style=dict(padding=10)
            ),
            html.H4('Daily Cases', id='daily-cases'),
            html.H4('Daily Recovered', id='daily-recovered'),
            html.H4('Daily Deaths', id='daily-deaths'),
        ], style={'text-align': 'center', 'background': const.PRIMARY_HEX}
    ), style=dict(background='white')
)

stat_selector = dbc.Tabs(
    [
        dbc.Tab(
            summary_tab,
            label="Summary",
            tab_style={'margin-top': '1rem', 'background': const.PRIMARY_RGB},
            label_style={'font-size': '20px'},
        ),
        dbc.Tab(
            overview_tab,
            label="Overview",
            tab_style={'margin-top': '1rem', 'background': const.PRIMARY_RGB},
            label_style={'font-size': '20px'},
        )
    ], className='nav-justified'
)

app.layout = html.Div([

    html.Div([
        dcc.Store(id='confirmed-data', storage_type='local'),
        dcc.Store(id='recovered-data', storage_type='local'),
        dcc.Store(id='deaths-data', storage_type='local'),
        dcc.Store(id='world-summary-data', storage_type='local',
                  data=data.get_summary()),
        dcc.Store(id='current-country', storage_type='local'),
    ], id='local-storage'),

    html.Div([
        navbar
    ], id='banner'),

    html.Div([
        country_dropdown,
        graph_dropdown,

        dbc.Alert(
            "Unable to perform query! Showing previous selected country data",
            id="alert",
            dismissable=False,
            fade=True,
            is_open=False,
            color='danger',
            duration=2000
        ),

    ], id='dropdowns'),

    dcc.ConfirmDialog(
        id='warning',
        message=const.WARNING_MESSAGE,
    ),

    html.Div([
        dcc.Graph(id="main-graph", config=dict(displaylogo=False), figure=go.Figure(data=[], layout=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False), paper_bgcolor='#222222', plot_bgcolor='#222222'))),
    ], className='graph'),

    html.Div([
        stat_selector
    ]),

    html.Div([
        dcc.Graph(id='map', config=dict(scrollZoom=False, displaylogo=False, displayModeBar=False))
    ]),
])


@app.callback(
    Output('map', 'figure'),
    [Input('current-country', 'data'),
     Input('world-summary-data', 'data'),
     Input('confirmed-data', 'data')])
def create_map(country, summary, confirmed):
    if confirmed:
        return graph_gen.get_map(country, string_to_df(summary))
    else:
        raise PreventUpdate


@app.callback(
    [Output('daily-cases', 'children'),
     Output('daily-deaths', 'children'),
     Output('daily-recovered', 'children'),
     Output('overview-date-picker', 'min_date_allowed'),
     Output('overview-date-picker', 'max_date_allowed')],
    [Input('overview-date-picker', 'date'),
     Input('confirmed-data', 'data'),
     Input('recovered-data', 'data'),
     Input('deaths-data', 'data')
     ])
def update_overview(date, confirmed, recovered, deaths):
    try:
        confirmed = string_to_df(confirmed)
        recovered = string_to_df(recovered)
        deaths = string_to_df(deaths)
        maxDate = confirmed['Date'].max()
        minDate = confirmed['Date'].min()

        if date != None:
            date = dt.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%SZ')
            daily_cases = int(confirmed[confirmed['Date'] == date]['Daily'])
            daily_deaths = int(deaths[deaths['Date'] == date]['Daily'])
            daily_recovered = int(recovered[deaths['Date'] == date]['Daily'])
            return "Daily Cases: {:,}".format(daily_cases), "Daily Deaths: {:,}".format(
                daily_deaths), 'Daily Recovered: {:,}'.format(daily_recovered), minDate, maxDate
        else:
            return "Daily Cases: None", "Daily Cases: None", "Daily Recovered: None", minDate, maxDate
    except Exception as e:
        raise PreventUpdate


@app.callback([Output('total_cases_in_table', 'children'),
               Output('total_deaths_in_table', 'children'),
               Output('total_recovered_in_table', 'children'),
               Output('recovery_rate_in_table', 'children'),
               Output('death_rate_in_table', 'children')],
              [Input('world-summary-data', 'data'),
               Input('current-country', 'data')])
def update_summary(summary, country):
    try:
        summary = string_to_df(summary)
        total_confirmed = int(
            summary[summary['Slug'] == country]['TotalConfirmed'])
        total_recovered = int(
            summary[summary['Slug'] == country]['TotalRecovered'])
        total_deaths = int(summary[summary['Slug'] == country]['TotalDeaths'])
        recovery_rate = total_recovered / total_confirmed
        death_rate = total_deaths / total_confirmed

        return 'Total Confirmed: {:,}'.format(total_confirmed), 'Total Recovered: {:,}'.format(
            total_recovered), 'Total Deaths: {:,}'.format(total_deaths), 'Recovery Rate: {:.2%}'.format(
            recovery_rate), 'Death Rate: {:.2%}'.format(death_rate)
    except:
        raise PreventUpdate


def string_to_df(string):
    """ Helper function to convert a string to a df"""
    if isinstance(string, str):
        return pd.DataFrame(ast.literal_eval(string))


@app.callback(
    [Output('confirmed-data', 'data'),
     Output('recovered-data', 'data'),
     Output('deaths-data', 'data'),
     Output('current-country', 'data')],
    [Input('countries-dropdown', 'value')])
def update_data(country):
    try:
        confirmed, recovered, deaths = data.get_data(country)
        return confirmed, recovered, deaths, country
    except:
        raise PreventUpdate


@app.callback(Output('main-graph', 'figure'),
              [Input('confirmed-data', 'data'),
               Input('recovered-data', 'data'),
               Input('deaths-data', 'data'),
               Input('current-country', 'data'),
               Input('graphs-dropdown', 'value')])
def update_graph(confirmed, recovered, deaths, country, graph_type):
    try:
        confirmed = string_to_df(confirmed)
        recovered = string_to_df(recovered)
        deaths = string_to_df(deaths)

        current_figure = None
        if graph_type == const.GRAPH_TYPE.SCATTER_TOTAL_CASES:
            data = {'confirmed': confirmed,
                    'recovered': recovered, 'deaths': deaths}
            current_figure = dict(
                data=graph_gen.tracer(
                    const.GRAPH_TYPE.SCATTER_TOTAL_CASES, data),
                layout=graph_gen.generic_layout_generator(
                    const.GRAPH_TYPE.SCATTER_TOTAL_CASES, country, True)
            )
        elif graph_type == const.GRAPH_TYPE.BAR_DAILY_CONFIRMED:
            current_figure = dict(
                data=graph_gen.tracer(
                    const.GRAPH_TYPE.BAR_DAILY_CONFIRMED, confirmed),
                layout=graph_gen.generic_layout_generator(
                    const.GRAPH_TYPE.BAR_DAILY_CONFIRMED, country, True)
            )
        elif graph_type == const.GRAPH_TYPE.BAR_DAILY_RECOVERED:
            current_figure = dict(
                data=graph_gen.tracer(
                    const.GRAPH_TYPE.BAR_DAILY_RECOVERED, recovered),
                layout=graph_gen.generic_layout_generator(
                    const.GRAPH_TYPE.BAR_DAILY_RECOVERED, country, True)
            )
        elif graph_type == const.GRAPH_TYPE.BAR_DAILY_DEATHS:
            current_figure = dict(
                data=graph_gen.tracer(
                    const.GRAPH_TYPE.BAR_DAILY_DEATHS, deaths),
                layout=graph_gen.generic_layout_generator(
                    const.GRAPH_TYPE.BAR_DAILY_DEATHS, country, True)
            )
        elif graph_type == const.GRAPH_TYPE.BAR_DAILY_DEATHS_RECOVERED_STACKED:
            data = {'confirmed': confirmed,
                    'recovered': recovered, 'deaths': deaths}
            current_figure = dict(
                data=graph_gen.tracer(
                    const.GRAPH_TYPE.BAR_DAILY_DEATHS_RECOVERED_STACKED, data),
                layout=graph_gen.generic_layout_generator(const.GRAPH_TYPE.BAR_DAILY_DEATHS_RECOVERED_STACKED, country,
                                                          True)
            )
        return current_figure
    except Exception as e:
        raise PreventUpdate


@app.callback(
    [Output("alert", "is_open"),
     Output('alert', 'children')],
    [Input("countries-dropdown", 'value'),
     Input('current-country', 'data')],
)
def toggle_alert(country, current_country):
    if country != current_country:
        return True, const.WARNING_MESSAGE.format(country=country.title())
    else:
        raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True)
