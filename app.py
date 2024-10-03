import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd
import base64
from io import StringIO
from datetime import datetime
import json
from datafunctions.data_processing import preserve_phone_format, load_data, format_and_apply_title_case, clean_and_tag_data, simplify_data_format, combine_multiple_files, dataframe_to_csv

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, 'assets/styles.css'], suppress_callback_exceptions=True)
app.title = "CRM Audience Data Processing App"

# New component for the toggle button
sidebar_toggle = html.Div([
    html.Button("≡", id="sidebar-toggle", className="toggle-btn"),
    dbc.Tooltip(
        id="sidebar-tooltip",  # Ensure this ID matches the callback
        target="sidebar-toggle",
        placement="right"
    )
], className="sidebar-toggle-container")

app.layout = html.Div([
    dbc.Container([
        # Title Bar with Company Logo
        dbc.Row([
            dbc.Col(html.Img(src="assets/images/TrafficConvert-500.png", height="50px"), width="auto"),
            dbc.Col(html.H1("Audience Data Processor", className="app-title text-center mb-4"), width=True),
        ], className="sticky-header align-items-center", style={"backgroundColor": "#01101c", "color": "primary", "padding": "10px"}),

        dbc.Row([
            # Sidebar with Instructions
            dbc.Col([
                sidebar_toggle,
                html.Div([
                    html.H5("Menu", className="text-center"),
                    html.A("Click for Help", id="toggle-instructions", href="#", className="link-button"),
                    html.Div([
                        html.Ul([
                            html.Li("1. Select an operation from the dropdown."),
                            html.Li("2. Upload a CSV or Excel file using the button below."),
                            html.Li("3. Choose columns and filter values to refine data."),
                            html.Li("4. Add or delete custom tags if desired."),
                            html.Li("5. Download the processed or filtered data."),
                        ], className="instructions-list", style={"text-align": "left"})
                    ], id="instructions-div", style={"display": "none"}),

                    html.Hr(),
                    # Dropdown for Selecting Operation Type
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
                    # File Upload
                    dcc.Upload(
                        id='upload-data',
                        children=dbc.Button(
                            "Upload File",
                            color="primary",
                            className="upload-btn",
                            style={"width": "100%", "margin-bottom": "10px"}
                        ),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px',
                            'backgroundColor': '#f8f9fa'
                        },
                        multiple=True
                    ),
                    # Tag Management
                    html.Div([
                        html.H5("Manage Tags"),
                        dcc.Input(
                            id='tag-input',
                            type='text',
                            placeholder='Enter tag(s), comma-separated',
                            style={'width': '100%', 'padding': '10px', 'margin': '10px 0'}
                        ),
                        html.Small("Note: Deleting tags will remove them from all rows. Please review carefully before deleting.", style={"color": "red", "margin-bottom": "10px", "display": "block"}),
                        dbc.Button("Add Tag(s)", id='add-tag-button', n_clicks=0, className="btn btn-primary mt-2 mr-2 tag-button"),
                        dbc.Button("Delete Tag(s)", id='delete-tag-button', n_clicks=0, className="btn btn-danger mt-2 tag-button")
                    ], style={"marginTop": "20px"}),
                    # Filtering Components
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
                        dbc.Button("Apply Filter", id='filter-button', n_clicks=0, className="btn btn-primary mt-2")
                    ], id='filter-section', style={"marginTop": "20px"}),
                    # Reset Button
                    dbc.Button("Reset All", id='reset-button', color="secondary", className="mt-4 mb-4 w-100"),
                    # Download Button
                    html.Div(id='download-div'),
                    # Feedback Message
                    dbc.Alert(id='feedback-message', is_open=False, duration=4000, style={"marginTop": "20px"}),
                ], id="sidebar-content", className="sidebar-content")
            ], id="sidebar", className="sidebar", style={"backgroundColor": "#f0f8ff", "padding": "20px", "borderRadius": "8px"}),

            # Main Content Area for Processed Data Display
            dbc.Col([
                html.H5("Processed Data", className="text-center", style={"color": "#007bff", "font-weight": "bold", "margin-top": "40px"}),
                html.Div(id='data-table-div'),
                # Display the structure of the data
                html.Div(id='data-structure', style={"color": "#007bff", "font-weight": "bold", "margin-top": "40px"}),
            ], id="main-content", className="main-content", width=9),
            
            dcc.Loading([html.Div(id="loading-demo")]),
        ], className="flex-container"),
        # Store component to share data between callbacks
        dcc.Store(id='processed-data'),
        
        # Footer
        dbc.Row([
            html.Div([
                html.P(f"© {datetime.now().year} trafficconver.ai", className="text-center")
            ], className="footer")
        ]),
    ], fluid=True, className="container-fluid")  # Use container-fluid to span full width
])

# Add this callback to handle the sidebar toggle
@app.callback(
    [Output("sidebar", "className"),
     Output("main-content", "className"),
     Output("sidebar-toggle", "children"),
     Output("sidebar-tooltip", "children")],  # Tooltip text update
    [Input("sidebar-toggle", "n_clicks")],
    [State("sidebar", "className")]
)
def toggle_sidebar(n_clicks, sidebar_class):
    if n_clicks is None:
        raise PreventUpdate
    
    if "collapsed" in sidebar_class:
        return "sidebar", "main-content", "≡", "Hide sidebar"  # Show the sidebar
    else:
        return "sidebar collapsed", "main-content expanded", "≫", "Show sidebar"  # Hide the sidebar
@app.callback(
    Output('instructions-div', 'style'),
    Input('toggle-instructions', 'n_clicks'),
    State('instructions-div', 'style')
)
def toggle_instructions(n_clicks, current_style):
    if n_clicks:
        return {'display': 'block'} if current_style['display'] == 'none' else {'display': 'none'}
    return current_style
@app.callback(
    [Output('data-table-div', 'children'),
     Output('data-structure', 'children'),
     Output('processed-data', 'data'),
     Output('column-filter-select', 'options'),
     Output('download-div', 'children'),
     Output('loading-demo', 'children'),
     Output('feedback-message', 'children'),
     Output('feedback-message', 'is_open'),
     Output('feedback-message', 'color')],
    [Input('upload-data', 'contents'),
     Input('filter-button', 'n_clicks'),
     Input('add-tag-button', 'n_clicks'),
     Input('delete-tag-button', 'n_clicks'),
     Input('reset-button', 'n_clicks')],
    [State('upload-data', 'filename'),
     State('upload-data', 'last_modified'),
     State('operation-select', 'value'),
     State('processed-data', 'data'),
     State('column-filter-select', 'value'),
     State('filter-value-input', 'value'),
     State('tag-input', 'value')]
)
def update_output(contents, filter_clicks, add_tag_clicks, delete_tag_clicks, reset_clicks, filename, last_modified, operation, json_data, selected_column, filter_values, tag_input):
    ctx = dash.callback_context
    if not ctx.triggered:
        return [dash.no_update] * 9
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    try:
        if triggered_id == 'reset-button':
            return [None, None, None, [], None, None, "All inputs have been reset.", True, "info"]
        
        if triggered_id == 'upload-data' and contents:
            dfs = []
            for content, name in zip(contents, filename):
                content_type, content_string = content.split(',')
                decoded = base64.b64decode(content_string)
                df = pd.read_csv(StringIO(decoded.decode('utf-8')))
                dfs.append(df)
            
            if operation == 'combine':
                combined_df = combine_multiple_files(dfs)
                if combined_df is not None:
                    df = combined_df
                    feedback = f"Datasets combined successfully. Total rows: {len(df)}"
                    color = "success"
                else:
                    feedback = "Failed to combine datasets. Ensure all files have matching columns."
                    color = "warning"
                    return [dash.no_update] * 6 + [feedback, True, color]
            
            elif operation == 'clean':
                cleaned_columns = ['Contact ID', 'First Name', 'Last Name', 'Business Email', 'Mobile Phone',
                                   'Personal Address', 'Personal City', 'Personal State', 'Personal Zip',
                                   'Personal Email', 'Tag']
                required_columns = ['MOBILE_PHONE', 'PERSONAL_ADDRESS', 'BUSINESS_EMAIL', 'PERSONAL_EMAIL', 'DNC']
                
                if set(cleaned_columns).issubset(df.columns):
                    feedback = "The uploaded data is already in the clean and tag format. No additional processing needed."
                    color = "info"
                elif set(required_columns).issubset(df.columns):
                    df = clean_and_tag_data(df, filename[0])
                    if df is not None:
                        feedback = "File uploaded and processed successfully"
                        color = "success"
                    else:
                        feedback = "Unable to process the file. The data may not be in the expected format."
                        color = "warning"
                        return [dash.no_update] * 6 + [feedback, True, color]
                else:
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    feedback = f"The uploaded file is missing required columns for cleaning: {', '.join(missing_columns)}. Please check your data and try again."
                    color = "warning"
                    return [dash.no_update] * 6 + [feedback, True, color]
                
            elif operation == 'simplify':
                simplified_columns = ['Personal Address', 'Personal City', 'Personal Zip', 'Personal State']
                required_columns = ['PERSONAL_ADDRESS', 'PERSONAL_CITY', 'PERSONAL_ZIP', 'PERSONAL_STATE']
                
                if set(simplified_columns) == set(df.columns):
                    feedback = "The uploaded data is already in the simplified format. No additional processing needed."
                    color = "info"
                elif set(required_columns).issubset(df.columns):
                    df = simplify_data_format(df)
                    if df is not None:
                        feedback = "File uploaded and simplified successfully"
                        color = "success"
                    else:
                        feedback = "Unable to simplify the file. The data may not be in the expected format."
                        color = "warning"
                        return [dash.no_update] * 6 + [feedback, True, color]
                else:
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    feedback = f"The uploaded file is missing required columns for simplification: {', '.join(missing_columns)}. Please check your data and try again."
                    color = "warning"
                    return [dash.no_update] * 6 + [feedback, True, color]
            
            processed_data = df.to_json(date_format='iso', orient='split')
            initial_structure = f"Data Structure: {len(df)} rows and {len(df.columns)} columns"

            data_table = create_data_table(df)
            column_options = [{'label': col, 'value': col} for col in df.columns]
            download_button = create_download_button()
            
            return data_table, initial_structure, processed_data, column_options, download_button, None, feedback, True, color

        elif triggered_id == 'filter-button':
            if json_data and selected_column and filter_values:
                df = pd.read_json(StringIO(json_data), orient='split')
                values = [v.strip() for v in filter_values.split(',')]

                # Preserve phone number format during filtering
                df = preserve_phone_format(df)

                if selected_column not in df.columns:
                    return [dash.no_update] * 6 + [f"Selected column '{selected_column}' does not exist in the data.", True, "warning"]

                present_values = [v for v in values if v in df[selected_column].values]
                missing_values = [v for v in values if v not in df[selected_column].values]

                if not present_values:
                    return [dash.no_update] * 6 + [f"None of the provided values exist in the '{selected_column}' column.", True, "warning"]

                filtered_df = df[df[selected_column].isin(present_values)]
                filtered_df = preserve_phone_format(filtered_df)  # Ensure phone format remains during filtering
                filtered_data = filtered_df.to_json(date_format='iso', orient='split')
                filtered_structure = f"Filtered Data Structure: {len(filtered_df)} rows and {len(filtered_df.columns)} columns"

                data_table = create_data_table(filtered_df)

                feedback_message = f"Data filtered successfully. {len(filtered_df)} rows match the filter criteria."
                if missing_values:
                    feedback_message += f"\nNote: The following values were not found in the '{selected_column}' column: {', '.join(missing_values)}"

                return data_table, filtered_structure, filtered_data, dash.no_update, dash.no_update, None, feedback_message, True, "success"
            else:
                return [dash.no_update] * 6 + ["Please select a column and enter filter values before applying the filter.", True, "warning"]

        elif triggered_id in ['add-tag-button', 'delete-tag-button'] and tag_input:
            if json_data:
                df = pd.read_json(StringIO(json_data), orient='split')
                tags = [tag.strip() for tag in tag_input.split(',') if tag.strip()]

                # Preserve phone number format before tag operations
                df = preserve_phone_format(df)

                if triggered_id == 'add-tag-button':
                    new_tags = []
                    existing_tags = []
                    for tag in tags:
                        if df['Tag'].apply(lambda x: tag not in (x.split(', ') if pd.notna(x) else [])).all():
                            new_tags.append(tag)
                        else:
                            existing_tags.append(tag)

                    if new_tags:
                        df['Tag'] = df['Tag'].apply(lambda x: ', '.join(set((x.split(', ') if pd.notna(x) else []) + new_tags)))
                        message = f"New tag(s) added successfully: {', '.join(new_tags)}"
                        if existing_tags:
                            message += f"\nExisting tag(s) not added: {', '.join(existing_tags)}"
                    else:
                        message = f"No new tags added. All tags already exist: {', '.join(existing_tags)}"
                    color = "success" if new_tags else "warning"

                else:  # delete-tag-button
                    deleted_tags = []
                    non_existent_tags = []
                    for tag in tags:
                        if df['Tag'].apply(lambda x: tag in (x.split(', ') if pd.notna(x) else [])).any():
                            deleted_tags.append(tag)
                        else:
                            non_existent_tags.append(tag)

                    if deleted_tags:
                        df['Tag'] = df['Tag'].apply(lambda x: ', '.join([t for t in (x.split(', ') if pd.notna(x) else []) if t not in deleted_tags]))
                        message = f"Tag(s) deleted successfully: {', '.join(deleted_tags)}"
                        if non_existent_tags:
                            message += f"\nNon-existent tag(s) not deleted: {', '.join(non_existent_tags)}"
                    else:
                        message = f"No tags deleted. All specified tags do not exist: {', '.join(non_existent_tags)}"
                    color = "success" if deleted_tags else "warning"

                # Preserve phone number format after tag operations
                df = preserve_phone_format(df)
                processed_data = df.to_json(date_format='iso', orient='split')
                initial_structure = f"Data Structure: {len(df)} rows and {len(df.columns)} columns"

                data_table = create_data_table(df)
                column_options = [{'label': col, 'value': col} for col in df.columns]
                download_button = create_download_button()

                return data_table, initial_structure, processed_data, column_options, download_button, None, message, True, color

        return [dash.no_update] * 9

    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}. Please check your data and try again."
        return [dash.no_update] * 6 + [error_message, True, "danger"]
def create_data_table(df):
    return dash_table.DataTable(
        id='data-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.head(50).to_dict('records'),
        page_size=10,
        style_table={'overflowX': 'auto', 'width': '100%'},
        style_header={
            'backgroundColor': '#009879',
            'color': 'white',
            'fontWeight': 'bold'
        },
        style_cell={
            'padding': '12px 15px',
            'border': '1px solid #ddd',
            'textAlign': 'left',
            'width': '100%'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'even'},
                'backgroundColor': '#f3f3f3'
            },
            {
                'if': {'state': 'active'},
                'backgroundColor': '#f1f1f1',
                'border': '1px solid #ddd'
            }
        ]
    )
 #   
def create_download_button():
    # Create a download button for processed data
    return html.Div([
        dbc.Button(
            'Download Processed Data',
            id='download-button',
            color="success",
            className="mt-2"
        ),
        dcc.Download(id="download-dataframe-csv"),
    ])

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("download-button", "n_clicks"),
    State("processed-data", "data"),
    prevent_initial_call=True,
)
def download_csv(n_clicks, data):
    # Callback to handle the download of processed data as a CSV file
    if n_clicks is None:
        return dash.no_update
    df = pd.read_json(StringIO(data), orient='split')
    return dcc.send_data_frame(df.to_csv, "processed_data.csv", index=False)

@app.callback(
    [Output('operation-select', 'value'),
     Output('upload-data', 'contents'),
     Output('column-filter-select', 'value'),
     Output('filter-value-input', 'value'),
     Output('tag-input', 'value')],
    Input('reset-button', 'n_clicks'),
    prevent_initial_call=True
)
def reset_all(n_clicks):
    # Callback to reset all input fields
    if n_clicks is None:
        return dash.no_update
    return [None, None, None, None, None]

if __name__ == '__main__':
    app.run_server(debug=True)