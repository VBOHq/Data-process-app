import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd
import base64
from io import StringIO
from datetime import datetime
import requests
import json

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, 'assets/styles.css'], suppress_callback_exceptions=True)
app.title = "CRM Audience Data Processing App"

# Define API URLs
UPLOAD_API_URL = "http://127.0.0.1:3000/upload"
LOAD_LEADS_API_URL = "http://127.0.0.1:3000/load-leads"

# Define the layout
app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.Img(src="assets/images/TrafficConvert-500.png", height="50px"), width="auto"),
            dbc.Col(html.H1("Audience Data Processor", className="app-title text-center mb-4"), width=True),
        ], className="sticky-header align-items-center", style={"backgroundColor": "#01101c", "padding": "10px"}),

        dbc.Row([
            dbc.Col([
                html.H5("Menu", className="text-center"),
                dcc.Dropdown(
                    id='operation-select',
                    options=[
                        {'label': 'GoHighLevel Data Formatter', 'value': 'clean'},
                        {'label': 'Simplif Data Formatter', 'value': 'simplify'},
                        {'label': 'Combine Data', 'value': 'combine'}
                    ],
                    placeholder="Select Operation",
                    className="mb-4"
                ),
                dcc.Upload(
                    id='upload-data',
                    children=dbc.Button(
                        "Upload File", color="primary", className="upload-btn", style={"width": "100%"}
                    ),
                    style={
                        'width': '100%',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'backgroundColor': '#f8f9fa'
                    },
                    multiple=False
                ),
                html.Div([
                    html.H5("Manage Tags"),
                    dcc.Input(
                        id='tag-input',
                        type='text',
                        placeholder='Enter tag(s), comma-separated',
                        style={'width': '100%', 'padding': '10px', 'margin': '10px 0'}
                    ),
                    dbc.Button("Add Tag(s)", id='add-tag-button', n_clicks=0, className="btn btn-custom mt-2"),
                    dbc.Button("Delete Tag(s)", id='delete-tag-button', n_clicks=0, className="btn btn-danger mt-2 tag-button")
                ], style={"marginTop": "20px"}),

                html.Div([
                    html.H5("Filter Data"),
                    dcc.Dropdown(
                        id='column-filter-select',
                        placeholder="Select column to filter",
                        className="mb-4"
                    ),
                    dcc.Input(
                        id='filter-value-input',
                        type='text',
                        placeholder='Enter filter values (comma-separated)',
                        style={'width': '100%', 'padding': '10px', 'margin': '10px 0'}
                    ),
                    dbc.Button("Apply Filter", id='filter-button', n_clicks=0, className="btn btn-custom mt-2")
                ], style={"marginTop": "20px"}),

                dbc.Button("Reset All", id='reset-button', color="secondary", className="btn btn-custom mt-2"),
                dbc.Button("Load Data to CRM", id="load-leads-button", color="success", style={"width": "100%", "margin-top": "10px"}),

                dbc.Alert(id='feedback-message', is_open=False, duration=4000, style={"marginTop": "20px"}),

                # Download button
                html.Div([
                    dbc.Button('Download Processed Data', id='download-button', className="btn btn-custom mt-2"),
                    dcc.Download(id="download-dataframe-csv"),
                ]),
            ], className="sidebar", width=3),

            dbc.Col([
                html.Div(id='data-table-div'),
                dcc.Loading([html.Div(id="loading-demo")]),
            ], width=9),
        ], className="flex-container"),
        
        dcc.Store(id='processed-data'),  # Store component for processed data

        # Footer
        dbc.Row([
            html.Div([html.P(f"© {datetime.now().year} trafficconver.ai", className="text-center")], className="footer")
        ]),
    ], fluid=True)
])

def create_data_table(df):
    return dash_table.DataTable(
        id='data-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.head(50).to_dict('records'),
        page_size=10,
        style_table={'overflowX': 'auto', 'width': '100%'},
    )

@app.callback(
    [
        Output('data-table-div', 'children'),
        Output('processed-data', 'data'),
        Output('feedback-message', 'children'),
        Output('feedback-message', 'is_open'),
        Output('feedback-message', 'color'),
        Output('column-filter-select', 'options'),
    ],
    [
        Input('upload-data', 'contents'),
        Input('filter-button', 'n_clicks'),
        Input('add-tag-button', 'n_clicks'),
        Input('delete-tag-button', 'n_clicks'),
        Input('reset-button', 'n_clicks'),
        Input('load-leads-button', 'n_clicks')
    ],
    [
        State('upload-data', 'filename'),
        State('operation-select', 'value'),
        State('processed-data', 'data'),
        State('column-filter-select', 'value'),
        State('filter-value-input', 'value'),
        State('tag-input', 'value')
    ]
)
def update_data(contents, filter_clicks, add_tag_clicks, delete_tag_clicks, reset_clicks, load_leads_click, filename, operation, json_data, selected_column, filter_values, tag_input):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    feedback = ""
    color = "info"

    # Initialize DataFrame based on stored data or uploaded content
    if triggered_id == 'upload-data' and contents:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(StringIO(decoded.decode('utf-8')))
        try:
            response = requests.post(UPLOAD_API_URL, files={"file": (filename, StringIO(decoded.decode('utf-8')))})
            if response.status_code == 200:
                data = response.json().get("data")
                df = pd.DataFrame(data)
                feedback = "File processed successfully and data loaded."
                color = "success"
            else:
                error_message = response.json().get("error", "Unknown error during file processing.")
                return None, None, error_message, True, "danger", []

        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            return None, None, error_message, True, "danger", []
    
    elif json_data:
        df = pd.DataFrame(json_data)
    else:
        return None, None, "No data to process", True, "warning", []

    try:
        # Reset all inputs
        if triggered_id == 'reset-button':
            return None, None, "All inputs have been reset.", True, "info", []

        # Apply filtering
        elif triggered_id == 'filter-button' and selected_column and filter_values:
            values = [v.strip() for v in filter_values.split(',')]
            filtered_df = df[df[selected_column].isin(values)]
            feedback = f"Filtered {len(filtered_df)} records based on '{selected_column}'"
            color = "success"
            data_table = create_data_table(filtered_df)
            return data_table, filtered_df.to_dict(orient='records'), feedback, True, color, [{'label': col, 'value': col} for col in df.columns]

        # Add tags
        elif triggered_id == 'add-tag-button' and tag_input:
            tags = [t.strip() for t in tag_input.split(',')]
            df['Tag'] = df['Tag'].apply(lambda x: ', '.join(set((x.split(', ') if x else []) + tags)))
            feedback = "Tags added successfully."
            color = "success"

        # Delete tags
        elif triggered_id == 'delete-tag-button' and tag_input:
            tags = [t.strip() for t in tag_input.split(',')]
            df['Tag'] = df['Tag'].apply(lambda x: ', '.join([t for t in (x.split(', ') if x else []) if t not in tags]))
            feedback = "Tags deleted successfully."
            color = "warning"

        # Load leads to CRM
        elif triggered_id == 'load-leads-button':
            response = requests.post(LOAD_LEADS_API_URL, json=df.to_dict(orient='records'))
            if response.status_code == 200:
                feedback = "Leads processing initiated successfully."
                color = "success"
            else:
                error_message = response.json().get("error", "Unknown error during leads processing.")
                feedback = error_message
                color = "danger"

        # Update processed-data store with the latest DataFrame
        data_table = create_data_table(df)
        column_options = [{'label': col, 'value': col} for col in df.columns]
        return data_table, df.to_dict(orient='records'), feedback, True, color, column_options

    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        return None, json_data, error_message, True, "danger", []



# Callback to handle CSV download
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("download-button", "n_clicks"),
    State("processed-data", "data"),
    prevent_initial_call=True
)
def download_csv(n_clicks, data):
    if not data:
        raise PreventUpdate
    df = pd.DataFrame(data)
    return dcc.send_data_frame(df.to_csv, "processed_data.csv", index=False)

if __name__ == '__main__':
    app.run_server(debug=True)

