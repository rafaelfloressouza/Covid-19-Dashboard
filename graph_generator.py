import constants as const
import plotly.graph_objs as go


def tracer(graph_type, data_df):
    """Functions return a list with the right TRACER"""
    tracer_list = None
    if graph_type == const.GRAPH_TYPE.SCATTER_TOTAL_CASES:
        tracer_list = __total_cases_scatter(data_df)
    elif graph_type == const.GRAPH_TYPE.BAR_DAILY_CONFIRMED:
        tracer_list = __daily_cases_bar(data_df)
    elif graph_type == const.GRAPH_TYPE.BAR_DAILY_RECOVERED:
        tracer_list = __daily_recovered_bar(data_df)
    elif graph_type == const.GRAPH_TYPE.BAR_DAILY_DEATHS:
        tracer_list = __daily_deaths_bar(data_df)
    elif graph_type == const.GRAPH_TYPE.BAR_DAILY_DEATHS_RECOVERED_STACKED:
        tracer_list = __daily_confirmed_recovered_deaths_stacked_bar(data_df)

    return tracer_list


def generic_layout_generator(graphType, country, showLegend):
    """Function generates the LAYOUT for a desired graph"""
    if graphType == const.GRAPH_TYPE.SCATTER_TOTAL_CASES:
        return __layout_generator_scatter(country, showLegend)
    elif graphType == const.GRAPH_TYPE.BAR_DAILY_CONFIRMED:
        return __layout_generator_bar(country, showLegend, const.MODE_DAILY_CASES)
    elif graphType == const.GRAPH_TYPE.BAR_DAILY_RECOVERED:
        return __layout_generator_bar(country, showLegend, const.MODE_DAILY_RECOVERED)
    elif graphType == const.GRAPH_TYPE.BAR_DAILY_DEATHS:
        return __layout_generator_bar(country, showLegend, const.MODE_DAILY_DEATHS)
    elif graphType == const.GRAPH_TYPE.BAR_DAILY_DEATHS_RECOVERED_STACKED:
        return __layout_generator_bar(country, showLegend, const.MODE_STACK)
    else:
        return {}


def get_map(country, summary_df):
    return dict(data=[__continent_map(summary_df)], layout=__layout_generator_map(country))


# ALL TRACERS
def __total_cases_scatter(data_df):
    """Function defines the TRACER for the total cases scatter plot"""
    tracer_list = []
    count = 0
    for label in const.LABELS:
        tracer_list.append(go.Scatter(x=data_df[label]['Date'],
                                      y=data_df[label]['Cases'],
                                      name=label.title(),
                                      line=dict(color=const.COLORS[count])))
        count += 1
    return tracer_list


def __daily_cases_bar(data_df):
    """Function defines the TRACER for the daily cases bar chart"""
    tracer_list = []
    if data_df['Daily'].max() == 0:
        raise Exception('There are No Reported Daily Cases')

    tracer_list.append(go.Bar(
        name='Daily Cases', x=data_df['Date'], y=data_df['Daily'], marker_color=const.COLORS[0]))
    return tracer_list


def __daily_recovered_bar(data_df):
    tracer_list = []
    if data_df['Daily'].max() == 0:
        raise Exception('There are No Reported Daily Recoveries')

    tracer_list.append(
        go.Bar(name='Daily Recovered', x=data_df['Date'], y=data_df['Daily'], marker_color=const.COLORS[1]))
    return tracer_list


def __daily_deaths_bar(data_df):
    tracer_list = []
    if data_df['Daily'].max() == 0:
        raise Exception('There are No Reported Daily Deaths')

    tracer_list.append(go.Bar(
        name='Daily Deaths', x=data_df['Date'], y=data_df['Daily'], marker_color=const.COLORS[2]))
    return tracer_list


def __daily_confirmed_recovered_deaths_stacked_bar(data_df):
    tracer_list = []
    names = ['Daily Cases', 'Daily Recovered', 'Daily Deaths']
    for label, name, color in zip(const.LABELS, names, const.COLORS):
        if data_df[label]['Daily'].max() == 0:
            raise Exception('There are No Reported Cases')
        tracer_list.append(go.Bar(name=name,
                                  x=data_df[label]['Date'],
                                  y=data_df[label]['Daily'],
                                  marker_color=color))
    return tracer_list


def __continent_map(df):
    return go.Choropleth(
        locations=df['CountryCode'].apply(
            lambda iso2: const.ISO2_TO_ISO3.get(str(iso2))),
        z=df['TotalConfirmed'],
        text=df['Country'],
        colorscale='Reds',
        autocolorscale=False,
        reversescale=False,
        colorbar=dict(tickfont=dict(color='white'))
    )


# ALL LAYOUTS
def __layout_generator_bar(country, showLegend, mode):
    """Function generates the LAYOUT for the daily-case bar chart."""
    if mode == const.MODE_DAILY_CASES:
        return dict(
            title=dict(
                text='Daily Cases ' + country.title(),
                font=dict(
                    color='white',
                    size=20
                )
            ),
            xaxis=dict(
                color='white',
                title=dict(
                    text='Date',
                    font=dict(
                        color='white',
                        size=16
                    ),
                ),
                tickfont=dict(size=13),
                showgrid=True,
                rangeselector=dict(
                    bgcolor='#444444',
                    font=dict(
                        size=14,
                        color='white'
                    ),
                    buttons=list([
                        dict(count=1,
                             label="1 Month",
                             step="month",
                             stepmode="backward"),
                        dict(count=3,
                             label="3 Months",
                             step="month",
                             stepmode="backward"),
                        dict(count=6,
                             label="6 Months",
                             step="month",
                             stepmode="backward"),
                        dict(label='ALL',
                             step="all")
                    ]),
                )
            ),
            yaxis=dict(
                color='white',
                title=dict(
                    text='Number of Daily Cases',
                    font=dict(
                        color='white',
                        size=16,
                    )
                ),
                tickfont=dict(size=13)
            ),
            showLegend=showLegend,
            paper_bgcolor='#222222',
            plot_bgcolor='#222222'
        )
    elif mode == const.MODE_DAILY_DEATHS:
        return dict(
            title=dict(
                text='Daily Deaths ' + country.title(),
                font=dict(
                    color='white',
                    size=20
                )
            ),
            xaxis=dict(
                title=dict(
                    text='Date',
                    font=dict(
                        color='white',
                        size=16
                    )
                ),
                color='white',
                tickfont=dict(size=13),
                showgrid=True,
                rangeselector=dict(
                    bgcolor='#444444',
                    font=dict(
                        size=14,
                        color='white'
                    ),
                    buttons=list([
                        dict(count=1,
                             label="1 Month",
                             step="month",
                             stepmode="backward"),
                        dict(count=3,
                             label="3 Months",
                             step="month",
                             stepmode="backward"),
                        dict(count=6,
                             label="6 Months",
                             step="month",
                             stepmode="backward"),
                        dict(label='ALL',
                             step="all")
                    ])
                )
            ),
            yaxis=dict(
                title=dict(
                    text='Number of Daily Deaths',
                    font=dict(
                        color='white',
                        size=16
                    )
                ),
                color='white',
                tickfont=dict(size=13)
            ),
            showLegend=showLegend,
            paper_bgcolor='#222222',
            plot_bgcolor='#222222'
        )
    elif mode == const.MODE_DAILY_RECOVERED:
        return dict(
            title=dict(
                text='Daily Recovered ' + country.title(),
                font=dict(
                    color='white',
                    size=20
                )
            ),
            xaxis=dict(
                title=dict(
                    text='Date',
                    font=dict(
                        size=16,
                        color='white'
                    )
                ),
                tickfont=dict(size=13),
                color='white',
                showgrid=True,
                rangeselector=dict(
                    bgcolor='#444444',
                    font=dict(
                        size=14,
                        color='white'
                    ),
                    buttons=list([
                        dict(count=1,
                             label="1 Month",
                             step="month",
                             stepmode="backward"),
                        dict(count=3,
                             label="3 Months",
                             step="month",
                             stepmode="backward"),
                        dict(count=6,
                             label="6 Months",
                             step="month",
                             stepmode="backward"),
                        dict(label='ALL',
                             step="all")
                    ])
                )
            ),
            yaxis=dict(
                title=dict(
                    text='Number of Daily Recovered',
                    font=dict(
                        color='white',
                        size=16
                    )
                ),
                color='white',
                tickfont=dict(size=13)
            ),
            showLegend=showLegend,
            paper_bgcolor='#222222',
            plot_bgcolor='#222222'
        )
    elif mode == const.MODE_STACK:
        return dict(
            title=dict(
                text='Daily (Confirmed - Recovered - Deaths) ' +
                     country.title(),
                font=dict(
                    color='white',
                    size=20
                )
            ),
            xaxis=dict(
                title=dict(
                    text='Date',
                    font=dict(
                        color='white',
                        size=16
                    )
                ),
                color='white',
                showgrid=True,
                tickfont=dict(size=13),
                rangeselector=dict(
                    bgcolor='#444444',
                    font=dict(
                        size=14,
                        color='white'
                    ),
                    buttons=list([
                        dict(count=1,
                             label="1 Month",
                             step="month",
                             stepmode="backward"),
                        dict(count=3,
                             label="3 Months",
                             step="month",
                             stepmode="backward"),
                        dict(count=6,
                             label="6 Months",
                             step="month",
                             stepmode="backward"),
                        dict(label='ALL',
                             step="all")
                    ])
                )
            ),
            yaxis=dict(
                title=dict(
                    text='# Daily Confirmed, Recovered and Deaths',
                    font=dict(
                        color='white',
                        size=16,
                    )
                ),
                color='white',
                tickfont=dict(size=13)
            ),
            showLegend=showLegend,
            legend=dict(
                x=0.01, y=0.95,
                bgcolor="#333333",
                font=dict(
                    color='white',
                    size=16
                ),
            ),
            barmode=mode,
            paper_bgcolor='#222222',
            plot_bgcolor='#222222'
        )


def __layout_generator_scatter(country, showlegend):
    """Function generates the LAYOUT for total-case scatter plot."""
    return dict(
        legend_orientation="h",
        title=dict(
            text='Total Cases (' + country.title() + ')',
            font=dict(
                color='white',
                size=20
            )
        ),
        showlegend=showlegend,
        legend=dict(
            x=0.01, y=0.95,
            bgcolor="#333333",
            font=dict(
                color='white',
                size=16
            )
        ),
        color='white',
        yaxis=dict(
            color='white',
            title=dict(
                text='Number of People',
                font=dict(
                    size=16,
                    color='white'
                ),
            ),
            tickfont=dict(size=13)
        ),
        xaxis=dict(
            color='white',
            title=dict(
                text='Date',
                font=dict(
                    size=16,
                    color='white'
                )
            ),
            tickfont=dict(size=13),
            showgrid=True,
            rangeselector=dict(
                bgcolor='#444444',
                font=dict(
                    color='white'
                ),
                buttons=list([
                    dict(count=1,
                         label="1 Month",
                         step="month",
                         stepmode="backward"),
                    dict(count=3,
                         label="3 Months",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6 Months",
                         step="month",
                         stepmode="backward"),
                    dict(label='ALL',
                         step="all")
                ])
            )
        ), paper_bgcolor='#222222', plot_bgcolor='#222222'
    )


def __layout_generator_map(country):
    return dict(
        title=dict(
            text='Continent Overview',
            font=dict(
                size=22,
                color='white'
            )
        ),
        height=1000,
        dragmode=False,
        geo=dict(
            scope=const.CONTINENTS[const.ISO2_TO_CONTINENT[const.COUNTRY_ISO2[country]]],
            showframe=False,
            countrywidth=1.5,
            countrycolor='white',
            showcoastlines=False,
            projection_type='equirectangular',
            bgcolor='rgba(34,34,34,34)'
        ),
        paper_bgcolor='#222222',
    )
