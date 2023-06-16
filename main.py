
import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import math

# Load the data from the CSV file
df = pd.read_csv("/Users/daniyalkabir/Downloads/msu_wbe_data_20230505.csv")

# Data preprocessing
df['sample.date'] = pd.to_datetime(df['sample.date'])

# Define the Dash app
app = dash.Dash(__name__)

# Create dropdown options for sample.loc
locations = df['sample.loc'].unique()
dropdown_options = [{'label': 'All', 'value': 'all'}] + [{'label': loc, 'value': loc} for loc in locations]

# Create the layout
app.layout = html.Div([
    html.H1("MSU Wastewater Dashboard"),

    html.Div([
        html.Label("Choose a location:"),
        dcc.Dropdown(
            id='location-dropdown',
            options=dropdown_options,
            value='all'
        )
    ]),

    html.Div([
        html.Label("Choose a date range:"),
        dcc.DatePickerRange(
            id='date-range',
            start_date=df['sample.date'].min(),
            end_date=df['sample.date'].max(),
            min_date_allowed=df['sample.date'].min(),
            max_date_allowed=df['sample.date'].max(),
            initial_visible_month=df['sample.date'].min(),
        )
    ]),

    dcc.Checklist(
        id='logarithmic-checkbox',
        options=[
            {'label': 'Show concentrations in log-10', 'value': 'log'}
        ],
        value=[],
        style={'fontSize': '18px'}
    ),

    dcc.Graph(id='time-series-plot'),
    dcc.Graph(id='box-plot'),
    dcc.Graph(id='line-plot'),
    dcc.Graph(id='histogram')
])


# Define callback functions
@app.callback(
    Output('time-series-plot', 'figure'),
    Output('box-plot', 'figure'),
    Output('line-plot', 'figure'),
    Output('histogram', 'figure'),
    Input('location-dropdown', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date'),
    Input('logarithmic-checkbox', 'value')
)
def update_plot(selected_location, start_date, end_date, logarithmic):
    if selected_location == 'all':
        filtered_df = df.copy()
    else:
        filtered_df = df[df['sample.loc'] == selected_location]

    # Apply the condition and create a new column for TRUE/FALSE values
    filtered_df['wildtype'] = filtered_df['wildtype'].where(filtered_df['wildtype'] > filtered_df['LDL'],
                                                            filtered_df['LDL'] / 2)
    filtered_df['wildtype_flag'] = filtered_df['wildtype'] > filtered_df['LDL']

    # Filter the dataframe based on the selected date range and positive cases/trendiness
    filtered_df = filtered_df[(filtered_df['sample.date'] >= start_date) &
                              (filtered_df['sample.date'] <= end_date) &
                              (filtered_df['wildtype_flag'] == True)]

    # Create the time series plot
    fig1 = px.scatter(filtered_df, x='sample.date', y='wildtype', trendline='ols', color='wildtype_flag')
    fig1.update_layout(
        title="SARS COV2 vs Sample Date",
        xaxis_title="Sample Date",
        yaxis_title="SARS COV2 Concentration (GC/100ml)",
        showlegend=False
    )

    # Create the box plot
    fig2 = px.box(filtered_df, x='sample.loc', y='wildtype', color='wildtype_flag')
    fig2.update_layout(
        title="SARS COV2 Distribution by Location",
        xaxis_title="Location",
        yaxis_title="SARS COV2 Concentration (GC/100ml)",
        showlegend=False
    )

    # Create the line plot
    fig4 = px.line(filtered_df, x='sample.date', y='wildtype', color='sample.loc')
    fig4.update_layout(
        title="SARS COV2 Concentration Trend over Time",
        xaxis_title="Sample Date",
        yaxis_title="SARS COV2 Concentration (GC/100ml)",
        showlegend=True
    )

    # Create the histogram
    fig5 = px.histogram(filtered_df, x='wildtype', nbins=20)
    fig5.update_layout(
        title="SARS COV2 Distribution Frequency",
        xaxis_title="SARS COV2 Concentration (GC/100ml)",
        yaxis_title="Frequency",
        showlegend=False
    )

    # Apply logarithmic scale if selected
    if 'log' in logarithmic:
        fig1.update_yaxes(type="log")
        fig2.update_yaxes(type="log")
        fig4.update_yaxes(type="log")
        fig5.update_yaxes(type="log")

    return fig1, fig2, fig4, fig5


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
