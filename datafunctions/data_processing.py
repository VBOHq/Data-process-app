import pandas as pd
import re
import base64
import io
import logging


##=========Load data from a CSV or Excel file ==================================
def load_data(file):
    """
    Load data from a CSV or Excel file.

    Args:
        file (str or file-like object): The file path or file-like object to be loaded.

    Returns:
        pd.DataFrame: The loaded data as a DataFrame.

    Raises:
        ValueError: If the file type is unsupported or an error occurs during loading.
    """
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        elif file.name.endswith('.xlsx'):
            return pd.read_excel(file)
        else:
            raise ValueError("Unsupported file type")
    except Exception as e:
        raise ValueError(f"Error loading file: {e}")


## Format column names to title case  ===
def format_and_apply_title_case(df, columns=None):
    """
    Format column names to title case and replace underscores or hyphens with spaces.
    Apply title case to specified columns. If no columns are specified, apply title case to all columns.

    Args:
        df (pd.DataFrame): The DataFrame to be processed.
        columns (list, optional): List of column names to apply title case to. If None, all columns are processed.

    Returns:
        pd.DataFrame: The DataFrame with formatted column names and title-cased columns.
    """
    # Format column names to title case and replace underscores or hyphens with spaces
    df.columns = [re.sub(r'[_-]', ' ', col).title() for col in df.columns]

    # Apply title case to specified columns or all columns if none are specified
    if columns is None:
        columns = df.columns
    df[columns] = df[columns].applymap(lambda x: x.title() if isinstance(x, str) else x)

    return df


### ====== Convert DataFrame to CSV string ============

def to_csv_string(data):
    """Convert DataFrame to CSV string."""
    return data.to_csv(index=False)

##  Convert DataFrame to CSV bytes
def to_csv_bytes(data):
    """Convert DataFrame to CSV bytes."""
    return data.to_csv(index=False).encode('utf-8')


#======= Parse content to csv or strong for download========
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            return df, None
        elif 'xlsx' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
            return df, None
        else:
            return None, "Unsupported file format. Please upload a CSV or Excel file."
    except Exception as e:
        return None, str(e)


# clean and tag data

def format_and_apply_title_case(df):
    df.columns = [col.replace('_', ' ').title() for col in df.columns]
    return df

def format_and_apply_title_case(df):
    df.columns = [col.replace('_', ' ').title() for col in df.columns]
    return df

import pandas as pd
import re
import logging

def clean_and_tag_data(df, file_name):
    """
    Processes a DataFrame by tagging rows based on conditions and updating 'Mobile Phone' values.
    Adds a 'Contact ID' column and checks the file name for specific tags.
    Ensures only valid phone numbers (10 digits or more) are retained.

    Args:
        df (pd.DataFrame): The DataFrame to be processed.
        file_name (str): The name of the uploaded file used for tagging.

    Returns:
        pd.DataFrame: Processed and tagged DataFrame.
        None: If the DataFrame is empty or required columns are missing.
    """
    if df is None or df.empty:
        logging.error("No data to process.")
        return None

    try:
        # Create a copy to avoid SettingWithCopyWarning
        df = df.copy()

        # Verify required columns are present
        required_columns = ['MOBILE_PHONE', 'PERSONAL_ADDRESS', 'BUSINESS_EMAIL', 'PERSONAL_EMAIL', 'DNC']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logging.error(f"Missing required columns: {', '.join(missing_columns)}")
            return None

        # Convert 'MOBILE_PHONE' to string type
        df['MOBILE_PHONE'] = df['MOBILE_PHONE'].astype(str)

        # Initialize the 'Tag' column
        df['Tag'] = ''

        # Patterns for identifying P.O. Box and formatting phone numbers
        po_box_pattern = re.compile(r'\b[Pp]\.? *[Oo]\.? *Box\b')
        phone_pattern = re.compile(r'\+?\d[\d\s-]*\d')

        # Tagging and processing logic
        for index, row in df.iterrows():
            tags = []

            # File-based tagging
            if 'B2B' in file_name.upper():
                tags.append('advertiser')
            elif 'B2C' in file_name.upper():
                tags.append('reader')

            # Address checks and tagging
            personal_address = str(row['PERSONAL_ADDRESS']) if pd.notna(row['PERSONAL_ADDRESS']) else ''
            if po_box_pattern.search(personal_address) or '-' in personal_address:
                df.loc[index, ['PERSONAL_ADDRESS', 'PERSONAL_STATE', 'PERSONAL_ZIP']] = pd.NA
            else:
                tags.append('programmatic')

            # Email and social tagging
            if pd.notna(row['BUSINESS_EMAIL']) and row['BUSINESS_EMAIL'] != '-':
                tags.append('email')
            if pd.notna(row['PERSONAL_EMAIL']) and row['PERSONAL_EMAIL'] != '-':
                tags.append('social')

            # SMS tagging and handling DNC
            if row['DNC'] == 'Y':
                df.loc[index, 'MOBILE_PHONE'] = pd.NA
            elif pd.notna(row['MOBILE_PHONE']) and row['MOBILE_PHONE'] != '-':
                phone_match = phone_pattern.search(str(row['MOBILE_PHONE']))
                if phone_match:
                    # Extract only digits from the phone number
                    digits_only = re.sub(r'[^\d]', '', phone_match.group())
                    
                    # Check if the number has at least 10 digits
                    if len(digits_only) >= 10:
                        # If the number starts with '1' and has 11 digits, remove the '1'
                        if len(digits_only) == 11 and digits_only.startswith('1'):
                            digits_only = digits_only[1:]
                        # Keep only the first 10 digits if there are more
                        standard_phone = digits_only[:10]
                        df.loc[index, 'MOBILE_PHONE'] = standard_phone
                        tags.append('sms')
                    else:
                        # Set phone numbers with fewer than 10 digits to NA
                        df.loc[index, 'MOBILE_PHONE'] = pd.NA
                else:
                    df.loc[index, 'MOBILE_PHONE'] = pd.NA

            # Update the 'Tag' column
            df.loc[index, 'Tag'] = ', '.join(tags)

        # Add 'Contact ID' as an auto-incrementing serial number
        df['Contact ID'] = range(1, len(df) + 1)

        # Define columns to be included in the final output
        selected_columns = [
            'Contact ID', 'FIRST_NAME', 'LAST_NAME', 'BUSINESS_EMAIL', 'MOBILE_PHONE',
            'PERSONAL_ADDRESS', 'PERSONAL_CITY', 'PERSONAL_STATE', 'PERSONAL_ZIP',
            'PERSONAL_EMAIL', 'Tag'
        ]
        # Ensure only existing columns are selected
        selected_columns = [col for col in selected_columns if col in df.columns]

        # Select and format columns
        df = df[selected_columns].replace('-', '', inplace=False)
        df_formatted = format_and_apply_title_case(df)
        df_formatted['Mobile Phone'] = df_formatted['Mobile Phone'].fillna("")  # Fill missing phone numbers with empty string

        # Preserve phone format only if the value is not blank, NaN, or empty
        df_formatted = preserve_phone_format(df_formatted, column_name='Mobile Phone')

        return df_formatted

    except Exception as e:
        logging.error(f"Error processing data: {str(e)}")
        return None

#==== convert Data to csv ======

def dataframe_to_csv(data, output_format='string'):
    """
    Convert a DataFrame to CSV format.

    Args:
        data (pd.DataFrame): The DataFrame to be converted.
        output_format (str): The format of the output. Can be 'string' or 'bytes'.
                             Default is 'string'.

    Returns:
        str or bytes: The DataFrame in CSV format as a string or bytes, depending on the specified output format.

    Raises:
        ValueError: If the specified output format is not 'string' or 'bytes'.
    """
    if output_format == 'string':
        return data.to_csv(index=False)
    elif output_format == 'bytes':
        return data.to_csv(index=False).encode('utf-8')
    else:
        raise ValueError("Invalid output format. Choose either 'string' or 'bytes'.")


## Format data in Simplifi format
def simplify_data_format(data):
    """
    Simplifies the format of the provided DataFrame by cleaning and formatting addresses.

    Args:
        data (pd.DataFrame): The DataFrame to be processed.

    Returns:
        pd.DataFrame: The cleaned and formatted DataFrame.
        None: If the DataFrame is empty or required columns are missing.
    """
    if data is None or data.empty:
        logging.error("No data to process.")
        return None

    try:
        # Create a copy to avoid SettingWithCopyWarning
        data = data.copy()

        # Verify required columns are present
        required_columns = ['PERSONAL_ADDRESS', 'PERSONAL_CITY', 'PERSONAL_ZIP', 'PERSONAL_STATE']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            logging.error(f"Missing required columns: {', '.join(missing_columns)}")
            return None

        # Clean and format addresses
        po_box_pattern = re.compile(r'\b[Pp]\.? *[Oo]\.? *Box\b')
        data = data[~data['PERSONAL_ADDRESS'].str.contains(po_box_pattern, regex=True, na=True)]
        data = data[data['PERSONAL_ADDRESS'] != '-']
        clean_data = data[['PERSONAL_ADDRESS', 'PERSONAL_CITY', 'PERSONAL_ZIP', 'PERSONAL_STATE']].apply(
            lambda x: x.str.title() if x.dtype == 'object' else x
        )
        clean_data = format_and_apply_title_case(clean_data)

        return clean_data

    except Exception as e:
        logging.error(f"Error processing data: {str(e)}")
        return None
    
    
def combine_multiple_files(files):
    """
    Appends multiple DataFrames after verifying they have matching columns.

    Args:
        files (list): List of DataFrame objects or file paths to the DataFrames.

    Returns:
        pd.DataFrame: The appended DataFrame if columns match.
        None: If the columns do not match, returns None.
    """
    appended_data = pd.DataFrame()
    for file in files:
        try:
            data = load_data(file) if isinstance(file, str) else file
            if appended_data.empty:
                appended_data = data
            else:
                if set(appended_data.columns) == set(data.columns):
                    appended_data = pd.concat([appended_data, data], ignore_index=True)
                else:
                    logging.error("DataFrames do not have matching columns.")
                    return None
        except Exception as e:
            logging.error(f"Failed to load {file}: {e}")
            return None
    
    appended_data['Contact ID'] = range(1, len(appended_data) + 1)
    logging.info(f"Shape of the appended DataFrame: {appended_data.shape}")
    return appended_data

# Helper function to preserve phone number format


import pandas as pd
import re

# def preserve_phone_format(df, column_name='Mobile Phone'):
#     """
#     Ensure phone numbers retain the +1 prefix format only if the value is not blank, NaN, or empty.

#     Args:
#         df (pd.DataFrame): The DataFrame to process.
#         column_name (str): The name of the column containing phone numbers.

#     Returns:
#         pd.DataFrame: The DataFrame with formatted phone numbers.
#     """
#     if column_name in df.columns:
#         def format_phone_number(x):
#             # Check if the value is not NaN and is not an empty string
#             if pd.notna(x) and x != '':
#                 x = str(x).strip()  # Convert to string and strip whitespace
#                 if x.isdigit() or re.match(r'^\+?\d+', x):  # Check if it contains only numbers or starts with a +
#                     if '.' in x:
#                         x = x.split('.')[0]  # Remove the decimal part if present
#                     if not x.startswith('+'):
#                         x = f"'+{x}"  # Add + if it's not already present
#             return x
        
#         # Use .loc to ensure no SettingWithCopyWarning occurs
#         df.loc[:, column_name] = df[column_name].apply(format_phone_number)
    
#     return df


def preserve_phone_format(df, column_name='Mobile Phone'):
    """
    Format phone numbers for Excel display, removing nan values and ensuring consistent formatting.
    
    Args:
        df (pd.DataFrame): The DataFrame to process
        column_name (str): The name of the column containing phone numbers
        
    Returns:
        pd.DataFrame: The DataFrame with properly formatted phone numbers
    """
    if column_name in df.columns:
        def format_phone_number(x):
            # Return empty string for nan/None values
            if pd.isna(x) or x == '' or x == 'nan':
                return ''
            
            # Convert to string and clean the number
            x = str(x).strip()
            # Remove any non-digit characters except +
            cleaned = ''.join(c for c in x if c.isdigit() or c == '+')
            
            # If we have digits, format the number
            if any(c.isdigit() for c in cleaned):
                # Remove any existing + symbol
                cleaned = cleaned.replace('+', '')
                # Format as: +1##########
                if len(cleaned) == 10:
                    return f"+1{cleaned}"
                elif len(cleaned) == 11 and cleaned.startswith('1'):
                    return f"+{cleaned}"
                else:
                    return f"+{cleaned}"
            return ''
        
        # Apply the formatting function
        df.loc[:, column_name] = df[column_name].apply(format_phone_number)
    
    return df