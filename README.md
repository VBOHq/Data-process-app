# Data-process-app

## Overview
The CRM Audience Data Processing App is designed to streamline and enhance the management of audience data. This application allows users to process, filter, and manage data efficiently, ensuring that it is ready for integration into platforms like GoHighLevel and Simplif. With its intuitive interface, users can upload data files, perform various operations, and download the processed data effortlessly.

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [User Interface](#user-interface)
4. [How to Use](#how-to-use)
5. [Technical Details](#technical-details)
6. [Getting Started](#getting-started)

## Features
- **Data Upload**: Easily upload CSV or Excel files containing audience data.
- **Data Processing**: Choose from multiple operations to clean, simplify, or combine data:
  - **GoHighLevel Data Formatter**: Cleans and tags data to match GoHighLevel's format.
  - **Simplif Data Formatter**: Simplifies data structure for easier analysis and integration.
  - **Combine Data**: Merges multiple datasets into a single, cohesive file.
- **Tag Management**: Add or delete custom tags to better categorize and manage data.
- **Data Filtering**: Refine data by selecting specific columns and applying filter criteria.
- **Download Processed Data**: Download the processed data in CSV format for further use.

## User Interface
- **Sidebar**: 
  - Provides instructions and menu options for selecting operations, uploading files, and managing tags.
  - Includes a toggle button to show or hide the sidebar for a more focused workspace.
- **Main Content Area**: 
  - Displays processed data in a tabular format.
  - Shows the structure of the data, including the number of rows and columns.
- **Footer**: Displays the current year and company name.

## How to Use
1. **Select an Operation**: Choose the desired data processing operation from the dropdown menu in the sidebar.
2. **Upload a File**: Click the "Upload File" button to select and upload your data file(s).
3. **Manage Tags**: Use the input field to add or delete tags as needed.
4. **Filter Data**: Select a column and enter filter values to refine the data.
5. **Download Data**: Once processing is complete, use the download button to save the processed data.

## Technical Details
- **Built with Dash**: Utilizes Dash and Dash Bootstrap Components for a responsive and interactive web application.
- **Data Handling**: Employs Pandas for efficient data manipulation and processing.
- **Custom Functions**: Includes functions for preserving phone formats, loading data, and more to ensure data integrity and consistency.

## Getting Started
To run the application, ensure you have Python installed along with the necessary packages listed in `requirements.txt`. Then, execute the following command in your terminal:

```bash
python app.py
```