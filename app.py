import pandas as pd
import dash
from dash import html, dcc, Input, Output, State, dash_table
import plotly.express as px
import dash_bootstrap_components as dbc
import os

from interpreter import interpret_query
from code_generator import build_code_from_filter
from interpreter import get_interpreter

# Load and prepare data
df = pd.read_csv('data/train.csv')
df.columns = df.columns.str.lower()  # lowercase column names to avoid case sensitivity issues

df['order date'] = pd.to_datetime(df['order date'], dayfirst=True, errors='coerce')
df['ship date'] = pd.to_datetime(df['ship date'], dayfirst=True, errors='coerce')

# Convert all string elements in the DataFrame to lowercase
df = df.applymap(lambda x: x.lower() if isinstance(x, str) else x)

# Dash App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H2("LLM Query to Graph"),

    dbc.Row([
        dbc.Col(dcc.Input(id='user-query', type='text', placeholder='e.g. sales in September 2017', style={'width': '100%'}), width=10),
        dbc.Col(html.Button('Generate', id='run-query', className='btn btn-primary'), width=2)
    ], className='mb-3'),

    html.Div(id="debug-output", style={
        'whiteSpace': 'pre-wrap',
        'border': '1px solid #ccc',
        'padding': '10px',
        'backgroundColor': '#f9f9f9',
        'marginBottom': '15px'
    }),

    dcc.Graph(id='sales-graph'),
    html.Hr(),
    html.H5("Filtered Data:"),
    dash_table.DataTable(
        id='filtered-table',
        page_size=10,
        style_table={'overflowX': 'auto'}
    )
])

@app.callback(
    [Output('sales-graph', 'figure'),
     Output('filtered-table', 'data'),
     Output('filtered-table', 'columns'),
     Output('debug-output', 'children')],
    Input('run-query', 'n_clicks'),
    State('user-query', 'value')
)
def handle_query(n, user_query):
    if not user_query:
        return dash.no_update, dash.no_update, dash.no_update, ""

    print("User Query:", user_query)

    # Step 1: Interpret
    user_query = user_query.lower().strip()
    filter_spec = interpret_query(user_query)
    print(" Filter Spec:", filter_spec)

    # Step 2: Generate Code
    filter_code = build_code_from_filter(filter_spec)
    print("Code to Execute:\n", filter_code)

    # Step 3: Apply Filter Code
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

    # Step 4: Graph Generation
    if not filtered_df.empty and 'Order Date' in filtered_df.columns and 'Sales' in filtered_df.columns:
        grouped_df = (
            filtered_df.sort_values('Order Date')
                       .groupby('Order Date', as_index=False)
                       .agg({'Sales': 'sum'})
        )
        fig = px.line(grouped_df, x='Order Date', y='Sales', title='Sales Over Time')
    else:
        fig = px.bar(title="No data or invalid filter.")

    # Step 5: Table
    data = filtered_df.to_dict('records')
    columns = [{'name': col, 'id': col} for col in filtered_df.columns]

    # Debug Output
    debug_info = f"""User Query:
                {user_query}

                Model Output:
                {filter_spec}

                Applied Filter Code:
                {filter_code}"""

    return fig, data, columns, debug_info
git 

if __name__ == '__main__':
    print("http://127.0.0.1:8050/")
    from waitress import serve
    print("Starting production server")
    serve(app.server, host="0.0.0.0", port=8050)
