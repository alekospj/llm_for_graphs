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
     Output('debug-box', 'children')],
    Input('run-query', 'n_clicks'),
    State('user-query', 'value')
)
def handle_query(n, user_query):
    if not user_query:
        return dash.no_update, dash.no_update, dash.no_update, ""

    user_query = user_query.lower().strip()
    debug_info = f"User Query:\n{user_query}\n"

    try:
        # Step 1: Interpret
        filter_spec = interpret_query(user_query)
        debug_info += f"\nModel Output:\n{filter_spec}"

        # Step 2: Generate Code
        filter_code = build_code_from_filter(filter_spec)
        debug_info += f"\n\nApplied Filter Code:\n{filter_code}"

        local_vars = {'df': df.copy(), 'pd': pd}
        exec(filter_code, {}, local_vars)
        filtered_df = local_vars.get('filtered_df', pd.DataFrame())

        debug_info += f"\n\nFiltered Preview:\n{filtered_df.head()}"

    except Exception as e:
        debug_info += f"\n\n🚨 Error:\n{e}"
        filtered_df = pd.DataFrame()

    # Default table data
    data, columns = [], []

    if not filtered_df.empty and 'order date' in filtered_df.columns and 'sales' in filtered_df.columns:
        grouped_df = (
            filtered_df.sort_values('order date')
                       .groupby('order date', as_index=False)
                       .agg({'sales': 'sum'})
        )
        fig = px.line(grouped_df, x='order date', y='sales', title='Sales Over Time')
        data = filtered_df.to_dict('records')
        columns = [{'name': col, 'id': col} for col in filtered_df.columns]
    else:
        fig = px.bar(title="No data or invalid filter.")

    return fig, data, columns, debug_info

if __name__ == '__main__':
    print("http://127.0.0.1:8050/")
    from waitress import serve
    print("Starting production server")
    serve(app.server, host="0.0.0.0", port=8050)
