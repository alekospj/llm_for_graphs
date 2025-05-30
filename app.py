import pandas as pd
import dash
from dash import html, dcc, Input, Output, State, dash_table
import plotly.express as px
import dash_bootstrap_components as dbc
import os

from interpreter import interpret_query
from code_generator import build_code_from_filter
from interpreter import get_interpreter_model


# Load and prepare data
df = pd.read_csv('data/train.csv')
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True, errors='coerce')

# Dash App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H2("2-Step LLM Sales Explorer"),
    dbc.Row([
        dbc.Col(dcc.Input(id='user-query', type='text', placeholder='e.g. sales in September 2017', style={'width': '100%'}), width=10),
        dbc.Col(html.Button('Generate', id='run-query', className='btn btn-primary'), width=2)
    ], className='mb-3'),
    dcc.Graph(id='sales-graph'),
    html.Hr(),
    html.H5("Filtered Data:"),
    dash_table.DataTable(id='filtered-table', page_size=10, style_table={'overflowX': 'auto'})
])

@app.callback(
    [Output('sales-graph', 'figure'),
     Output('filtered-table', 'data'),
     Output('filtered-table', 'columns')],
    Input('run-query', 'n_clicks'),
    State('user-query', 'value')
)
def handle_query(n, user_query):
    if not user_query:
        return dash.no_update

    print("User Query:", user_query)

    # Step 1: Interpret
    filter_spec = interpret_query(user_query)
    print(" Filter Spec:", filter_spec)

    # Step 2: Generate Code
    filter_code = build_code_from_filter(filter_spec)
    print("🛠 Code to Execute:\n", filter_code)

    local_vars = {'df': df.copy(), 'pd': pd}
    try:
        exec(filter_code, {}, local_vars)
        filtered_df = local_vars.get('filtered_df', pd.DataFrame())
    except Exception as e:
        print(" Code Execution Error:", e)
        filtered_df = pd.DataFrame()

    print("Filtered Preview:\n", filtered_df.head())
    os.makedirs("temp", exist_ok=True)
    filtered_df.to_csv("temp/filtered_output.csv", index=False)

    # Build graph
    if not filtered_df.empty and 'Order Date' in filtered_df.columns:
        fig = px.line(filtered_df, x='Order Date', y='Sales', title='Sales Over Time')
    else:
        fig = px.bar(title="⚠️ No data or invalid filter.")

    # Build table
    data = filtered_df.to_dict('records')
    columns = [{'name': col, 'id': col} for col in filtered_df.columns]

    return fig, data, columns

if __name__ == '__main__':
    from waitress import serve
    print("Starting production server with Waitress (no thread conflicts)...")
    serve(app.server, host="0.0.0.0", port=8050)

