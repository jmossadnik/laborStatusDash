import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px

# Load your data from "dta.csv"
df = pd.read_csv('dta.csv')
df = df[df.year >= 1988] # missing months in 1985; hard to impute because it is the beginning
                         # of the timeseries, hence I cut the data for displaying

# create date variable
df['date'] = pd.to_datetime(df['year'].astype(int).astype(str) + '-' + df['month'].astype(int).astype(str) + '-12')

# Recession periods
recession_periods = [("1990-07-01", "1991-03-01"), ("2001-03-01", "2001-11-01"),
                     ("2007-12-01", "2009-06-01"), ("2020-02-01", "2020-04-01")]

app = dash.Dash(__name__)

# Declare server for Render deployment. Needed for Procfile.
server = app.server

# Define the app layout
app.layout = html.Div([
    html.H1("Labor Market Timeseries Dashboard"),
    dcc.Dropdown(
        id='sex-dropdown',
        options=[{'label': sex, 'value': sex} for sex in ['f', 'm', 't']],
        multi=True,
        value=['f', 'm', 't']  # Default selection
    ),
    dcc.Dropdown(
        id='age-dropdown',
        options=[{'label': age, 'value': age} for age in ['16-64', '16-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-64']],
        multi=True,
        value=['16-64']  # Default selection
    ),
    dcc.Dropdown(
        id='timeseries-dropdown',
        options=[
            {'label': 'Unemployment Rate', 'value': 'u_rate'},
            {'label': 'Part-Time Rate', 'value': 'part_rate'},
            {'label': 'Labor Force Participation Rate', 'value': 'lab_rate'}
        ],
        multi=True,
        value=['u_rate']  # Default selection
    ),
    dcc.Dropdown(
        id='seasonal-dropdown',
        options=[
            {'label': 'seasonally adjusted', 'value': 1},
            {'label': 'not seasonally adjusted', 'value': 0}
        ],
        multi=False,
        value=[0]  # Default selection
    ),
    dcc.Graph(id='timeseries-plot'),
])

# Define callback to update the plot
@app.callback(
    Output('timeseries-plot', 'figure'),
    Input('sex-dropdown', 'value'),
    Input('age-dropdown', 'value'),
    Input('timeseries-dropdown', 'value'),
    Input('seasonal-dropdown', 'value')
)
def update_plot(selected_sexes, selected_ages, selected_timeseries, seasonal):
    if seasonal == 1:
        selected_timeseries = ['{}_sa'.format(c) for c in selected_timeseries]
        	
    reference_data = df[(df['sex']=='t') & (df['age_group']=='16-64')]
    reference_data.sex = 't 16-64'

    filtered_data = df[(df['sex'].isin(selected_sexes)) & (df['age_group'].isin(selected_ages))][['age_group', 'sex', 'date'] + selected_timeseries]

    filtered_data = pd.concat([filtered_data, reference_data])
        
    filtered_data = filtered_data.sort_values(by=['date'])                
    fig = px.line(
        filtered_data,
        x='date',
        y=selected_timeseries,
        color='sex',
        title='Labor Market Timeseries',
        labels={"sex": "sex", "age group": "age_group"}
    )
    # Add shaded rectangles for NBER recession dates
    for start_date, end_date in recession_periods:
        fig.add_vrect(x0=start_date, x1=end_date, fillcolor='grey', opacity=0.3)
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
