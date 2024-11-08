import pandas as pd
import requests
import time
import logging
from flask import Flask, request, jsonify
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the GoHighLevel API key
gohighlevel_api_key = os.getenv("GOHIGHLEVEL_API_KEY")



app = Flask(__name__)

# Ensure the log file is created in the root directory
log_file_path = os.path.join(os.getcwd(), 'process_logs.log')

# Configure logging to output to both the console and the file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

#set the based url 
# Corrected base URL for creating contacts
gohighlevel_base_url = "https://rest.gohighlevel.com/v1/contacts/"


headers = {
        "Authorization": f"Bearer {gohighlevel_api_key}",
        "Content-Type": "application/json"
    }

# In-memory storage for processed data
processed_data_store = []

# Data processing function
def clean_and_tag_data(df, file_name):
    if df is None or df.empty:
        logging.error("No data to process.")
        return None, "No data to process."

    required_columns = [
        'MOBILE_PHONE', 'PERSONAL_ADDRESS', 'BUSINESS_EMAIL',
        'PERSONAL_EMAIL', 'DNC', 'FIRST_NAME', 'LAST_NAME',
        'PERSONAL_CITY', 'PERSONAL_STATE', 'PERSONAL_ZIP'
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        error_msg = f"Missing required columns: {', '.join(missing_columns)}"
        logging.error(error_msg)
        return None, error_msg

    try:
        df = df[required_columns].copy()
        df['MOBILE_PHONE'] = df['MOBILE_PHONE'].astype(str)
        df['Tag'] = ''
        po_box_pattern = re.compile(r'\b[Pp]\.? *[Oo]\.? *Box\b')
        phone_pattern = re.compile(r'\+?\d[\d\s-]*\d')

        def tag_row(row):
            tags = []
            if 'B2B' in file_name.upper():
                tags.append('advertiser')
            elif 'B2C' in file_name.upper():
                tags.append('reader')

            if pd.notna(row['PERSONAL_ADDRESS']):
                if po_box_pattern.search(row['PERSONAL_ADDRESS']) or '-' in row['PERSONAL_ADDRESS']:
                    row[['PERSONAL_ADDRESS', 'PERSONAL_STATE', 'PERSONAL_ZIP']] = pd.NA
                else:
                    tags.append('programmatic')

            if pd.notna(row['BUSINESS_EMAIL']) and row['BUSINESS_EMAIL'] != '-':
                tags.append('email')
            if pd.notna(row['PERSONAL_EMAIL']) and row['PERSONAL_EMAIL'] != '-':
                tags.append('social')

            if row['DNC'] == 'Y':
                row['MOBILE_PHONE'] = pd.NA
            elif pd.notna(row['MOBILE_PHONE']) and row['MOBILE_PHONE'] != '-':
                phone_match = phone_pattern.search(row['MOBILE_PHONE'])
                if phone_match:
                    digits_only = re.sub(r'[^\d]', '', phone_match.group())
                    if len(digits_only) >= 10:
                        if len(digits_only) == 11 and digits_only.startswith('1'):
                            digits_only = digits_only[1:]
                        row['MOBILE_PHONE'] = digits_only[:10]
                        tags.append('sms')
                    else:
                        row['MOBILE_PHONE'] = pd.NA

            row['Tag'] = ', '.join(tags)
            return row

        df = df.apply(tag_row, axis=1)
        selected_columns = [
            'FIRST_NAME', 'LAST_NAME', 'BUSINESS_EMAIL', 'MOBILE_PHONE',
            'PERSONAL_ADDRESS', 'PERSONAL_CITY', 'PERSONAL_STATE', 'PERSONAL_ZIP',
            'PERSONAL_EMAIL', 'Tag'
        ]
        df = df[[col for col in selected_columns if col in df.columns]].replace('-', '')
        df['MOBILE_PHONE'] = df['MOBILE_PHONE'].fillna("")

        logging.info("Data processing completed successfully.")
        return df, None

    except Exception as e:
        logging.error(f"Error processing data: {str(e)}")
        return None, str(e)

# Function to structure data for GoHighLevel
def structure_data_for_gohighlevel(df):
    """
    Converts a DataFrame to a list of contact dictionaries suitable for GoHighLevel API.
    """
    # Replace NaN and set defaults at the DataFrame level for performance
    df.fillna({
        "FIRST_NAME": "", "LAST_NAME": "", "BUSINESS_EMAIL": "", "MOBILE_PHONE": "",
        "PERSONAL_ADDRESS": "", "PERSONAL_CITY": "", "PERSONAL_STATE": "", "PERSONAL_ZIP": "", "Tag": ""
    }, inplace=True)
    
    # Convert DataFrame to list of dicts for GoHighLevel API
    contacts_list = df.apply(lambda row: {
        "firstName": row["FIRST_NAME"],
        "lastName": row["LAST_NAME"],
        "email": row["BUSINESS_EMAIL"],
        "phone": row["MOBILE_PHONE"],
        "address1": row["PERSONAL_ADDRESS"],
        "city": row["PERSONAL_CITY"],
        "state": row["PERSONAL_STATE"],
        "postalCode": str(row["PERSONAL_ZIP"]),
        "tags": row["Tag"].split(", ")
    }, axis=1).tolist()

    logging.info(f"Structured {len(contacts_list)} contacts for GoHighLevel.")
    return contacts_list

# Function to create a contact with retry logic for rate limits
def create_contact(contact_data, retries=3, backoff_factor=2):
    """
    Attempts to create a contact in GoHighLevel, handling rate limits with exponential backoff.
    """
    try:
        response = requests.post(gohighlevel_base_url, json=contact_data, headers=headers)
        
        # Handle rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 10))  # Use 'Retry-After' header if available
            logging.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            if retries > 0:
                return create_contact(contact_data, retries - 1, backoff_factor)
            else:
                logging.error("Max retries reached. Contact not created due to rate limits.")
                return None

        # Raise exception for other HTTP errors
        response.raise_for_status()
        logging.info(f"Contact created successfully: {response.json()}")
        return response.json()

    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        logging.error(f"Request error occurred: {err}")

#Load contacts in batches with customizable batch size and pause duration
def load_contacts_in_batches(contacts_list, batch_size=100, pause_duration=10):
    """
    Loads contacts into GoHighLevel in batches, pausing to respect API rate limits.
    """
    for i, contact in enumerate(contacts_list):
        try:
            logging.info(f"Attempting to load contact {i + 1}: {contact}")  # Log contact data before sending
            response = create_contact(contact)
            if response:
                logging.info(f"Contact {i + 1} successfully loaded into CRM: {response}")
            else:
                logging.warning(f"Contact {i + 1} failed to load due to an issue with the response.")
        except Exception as e:
            logging.error(f"Failed to create contact {i + 1}: {e}")

        # Pause after each batch to respect API limits
        if (i + 1) % batch_size == 0:
            logging.info(f"Processed {i + 1} contacts. Pausing for {pause_duration} seconds.")
            time.sleep(pause_duration)

@app.route('/upload', methods=['POST'])
def upload_file():
    global processed_data_store

    if 'file' not in request.files:
        logging.error("No file provided in request.")
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        logging.error("No file selected by user.")
        return jsonify({"error": "No file selected"}), 400

    try:
        df_data = pd.read_csv(file)
        processed_df, error_msg = clean_and_tag_data(df_data, file.filename)

        if processed_df is not None:
            logging.info(f"Processed file '{file.filename}' successfully.")
            processed_data_store = processed_df.to_dict(orient='records')  # Store the cleaned data
            
            # Log the number of records stored
            logging.info(f"Stored {len(processed_data_store)} records in processed_data_store.")
            
            return jsonify({"message": "File processed successfully", "data": processed_data_store}), 200
        else:
            logging.error(f"Data processing failed for file '{file.filename}': {error_msg}")
            return jsonify({"error": error_msg or "Data processing failed"}), 500

    except Exception as e:
        logging.error(f"Error processing uploaded file '{file.filename}': {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/load-leads', methods=['POST'])
def load_leads():
    global processed_data_store
    if not processed_data_store:
        logging.error("No processed data available to load.")
        return jsonify({"error": "No processed data available to load. Please upload data first."}), 400

    try:
        contacts_list = structure_data_for_gohighlevel(pd.DataFrame(processed_data_store))
        load_contacts_in_batches(contacts_list)
        return jsonify({"message": "Leads processing initiated"}), 200

    except Exception as e:
        logging.error(f"Error in load-leads route: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(port=3000, debug=True)
