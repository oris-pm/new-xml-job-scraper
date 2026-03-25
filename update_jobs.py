import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# Configuration - Targeted specifically to Table 3
SHEET_ID = '1SHM5ut3bUQP6NUZ3_a9Q7Bkp60EY5NEM4oNIFaMMHL4'
GID = '736783278'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}'

def create_xml(df):
    """
    Converts the DataFrame into a structured XML format compatible with JBoard.
    Automatically handles new columns like 'Company Logo'.
    """
    # Timestamp ensures the file content changes, forcing GitHub/JBoard to see an update
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<jobs>')
    xml.append(f'  <last_build_date>{now}</last_build_date>')
    
    for _, row in df.iterrows():
        xml.append('  <job>')
        
        for col_name in df.columns:
            # Clean column names (e.g., "Company Logo" becomes <company_logo>)
            tag = str(col_name).strip().replace(' ', '_').lower()
            
            # Convert value to string and handle empty cells (NaN)
            val = str(row[col_name]) if pd.notna(row[col_name]) else ""
            
            # XML Safety: Escape problematic characters to prevent feed breaking.
            # This is critical for URLs (logos/links) containing '&' or query params.
            val = (val.replace("&", "&amp;")
                      .replace("<", "&lt;")
                      .replace(">", "&gt;")
                      .replace('"', "&quot;")
                      .replace("'", "&apos;"))
            
            xml.append(f'    <{tag}>{val}</{tag}>')
                
        xml.append('  </job>')
    
    xml.append('</jobs>')
    return '\n'.join(xml)

def main():
    try:
        print(f"Connecting to Google Sheet Table 3 (GID: {GID})...")
        
        # Fetching the data from Google Sheets
        response = requests.get(URL)
        response.raise_for_status() 
        
        # Force UTF-8 encoding to fix special character issues (like the 'â' symbol)
        response.encoding = 'utf-8' 
        
        # Load the CSV data exported from Google Sheets
        # StringIO turns the text response into a file-like object for Pandas
        df = pd.read_csv(StringIO(response.text)).dropna(how='all')
        
        if df.empty:
            print("Warning: Table 3 is empty. Check your Google Apps Script execution.")
            return

        print(f"Successfully retrieved {len(df)} jobs.")
        print(f"Columns found: {list(df.columns)}")
        
        # Generate the XML content
        xml_data = create_xml(df)
        
        # Write the file with explicit utf-8 encoding and error replacement 
        # to ensure the GitHub runner saves the file correctly.
        with open('jobs_feed.xml', 'w', encoding='utf-8', errors='replace') as f:
            f.write(xml_data)
            
        print("Successfully updated jobs_feed.xml with UTF-8 safety and Logo support.")
        
    except Exception as e:
        print(f"Error during execution: {e}")
        # Exit with 1 to notify GitHub Actions that the build failed
        exit(1)

if __name__ == "__main__":
    main()
