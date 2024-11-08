
# CRM Audience Data Processing App

This is a Dash application integrated with a Flask API to process and manage audience data, apply filters, tags, and load data into a CRM (GoHighLevel) system. The app also allows users to download the processed data as a CSV file.

## Table of Contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Project Structure](#project-structure)
6. [API Endpoints](#api-endpoints)
7. [License](#license)

## Features

- **Upload and Process Data**: Upload CSV files for processing with multiple operations (data cleaning, simplifying, combining).
- **Tag Management**: Add or delete tags to categorize data entries.
- **Data Filtering**: Filter data by specific column values for targeted viewing.
- **Load Data to CRM**: Send processed data to the GoHighLevel CRM.
- **Download Processed Data**: Export the cleaned and tagged data as a CSV file.

## Requirements

- Python 3.7+
- Flask
- Dash
- pandas
- dash-bootstrap-components
- requests
- python-dotenv (for environment variable management)

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/crm-audience-data-processing-app.git
cd crm-audience-data-processing-app
```

### Step 2: Create and Activate a Virtual Environment

```bash
python -m venv myenv
myenv\Scripts\activate   # On Windows
source myenv/bin/activate   # On macOS/Linux
```

### Step 3: Install Required Packages

Install all dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the root directory with your GoHighLevel API key:

```plaintext
GOHIGHLEVEL_API_KEY=your_actual_gohighlevel_api_key
```

### Step 5: Run the Flask API

In one terminal, start the Flask API:

```bash
python api.py
```

### Step 6: Run the Dash App

In another terminal, start the Dash app:

```bash
python app.py
```

## Usage

1. **Access the App**: Open a web browser and go to `http://127.0.0.1:8050`.
2. **Select an Operation**: Choose from available operations:
   - **GoHighLevel Data Formatter**
   - **Simplif Data Formatter**
   - **Combine Data**
3. **Upload File**: Click on "Upload File" and select a CSV file.
4. **Apply Filters**: Use the filter section to narrow down data by specific columns.
5. **Tag Management**: Add or delete tags to categorize entries.
6. **Load Data to CRM**: Send the data to GoHighLevel CRM using the "Load Data to CRM" button.
7. **Download Processed Data**: Click "Download Processed Data" to save the data as a CSV.

## Project Structure

```plaintext
crm-audience-data-processing-app/
├── app.py                # Main Dash application
├── api.py                # Flask API for data processing
├── .env                  # Environment variables file (contains GoHighLevel API key)
├── requirements.txt      # Required Python packages
├── assets/
│   ├── styles.css        # Custom CSS for styling
│   └── images/
│       └── TrafficConvert-500.png  # App logo
└── README.md             # Project documentation
```

## API Endpoints

The Flask API provides two endpoints:

1. **`/upload`**: Processes the uploaded CSV file, applies tags, filters, and cleans data.
2. **`/load-leads`**: Sends processed data to GoHighLevel CRM.

## License

This project is licensed under the MIT License.
