import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# Configuration - Targeted specifically to Table 3
SHEET_ID = '1SHM5ut3bUQP6NUZ3_a9Q7Bkp60EY5NEM4oNIFaMMHL4'
GID = '736783278'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}'

def create_xml(df):
    # Timestamp ensures the file content changes, forcing JBoard/GitHub to see an update
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<jobs>')
    xml.append(f'  <last_build_date>{now}</last_build_date>')
    
    for _, row in df.iterrows():
        xml.append('  <job>')
        
        for col_name in df.columns:
            # Clean column names (e.g., "Job Description" becomes <job_description>)
            tag = str(col_name).strip().replace(' ', '_').lower()
            
            # Convert value to string and handle empty cells
            val = str(row[col_name]) if pd.notna(row[col_name]) else ""
            
            # XML Safety: Escape problematic characters to prevent feed breaking
            # This also helps handle those strange characters by keeping the XML valid
            val = val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            
            xml.append(f'    <{tag}>{val}</{tag}>')
                
        xml.append('  </job>')
    
    xml.append('</jobs>')
    return '\n'.join(xml)

def main():
    try:
        print(f"Connecting to Google Sheet Table 3 (GID: {GID})...")
        
        # Fetching the data
        response = requests.get(URL)
        response.raise_for_status() 
        
        # FIX: Force UTF-8 encoding on the incoming data to fix the "â" character issues
        response.encoding = 'utf-8' 
        
        # Load the CSV data exported from Google Sheets
        # We use StringIO to turn the text response into a file-like object for Pandas
        df = pd.read_csv(StringIO(response.text)).dropna(how='all')
        
        if df.empty:
            print("Warning: Table 3 is empty. Check your Google Apps Script execution.")
            return

        print(f"Successfully retrieved {len(df)} jobs.")
        print(f"Columns found: {list(df.columns)}")
        
        # Generate the XML content
        xml_data = create_xml(df)
        
        # FIX: Write the file with explicit utf-8 encoding and error replacement 
        # to ensure special characters don't turn into gibberish.
        with open('jobs_feed.xml', 'w', encoding='utf-8', errors='replace') as f:
            f.write(xml_data)
            
        print("Successfully updated jobs_feed.xml with UTF-8 safety.")
        
    except Exception as e:
        print(f"Error during execution: {e}")
        exit(1)

if __name__ == "__main__":
    main()
