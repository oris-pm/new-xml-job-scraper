import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# Configuration
SHEET_ID = '1SHM5ut3bUQP6NUZ3_a9Q7Bkp60EY5NEM4oNIFaMMHL4'
GID = '736783278'  # Your Table 3 GID
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}'

def create_xml(df):
    # Timestamp to force GitHub to recognize a change
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<jobs>')
    xml.append(f'  <last_build_date>{now}</last_build_date>')
    
    for _, row in df.iterrows():
        xml.append('  <job>')
        
        for col_name in df.columns:
            # Converts "Job Description" to "job_description" and "ID" to "id"
            tag = str(col_name).strip().replace(' ', '_').lower()
            
            # Handle data and convert to string
            val = str(row[col_name]) if pd.notna(row[col_name]) else ""
            
            # XML Safety: Escape problematic characters
            val = val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            
            xml.append(f'    <{tag}>{val}</{tag}>')
                
        xml.append('  </job>')
    
    xml.append('</jobs>')
    return '\n'.join(xml)

def main():
    try:
        print(f"Fetching data from Table 3 (GID: {GID})...")
        response = requests.get(URL)
        response.raise_for_status() 
        
        # Load the CSV data exported from Google Sheets
        df = pd.read_csv(StringIO(response.text)).dropna(how='all')
        
        if df.empty:
            print("No data found in Table 3.")
            return

        print(f"Processing {len(df)} jobs with columns: {list(df.columns)}")
        
        # Create XML content
        xml_data = create_xml(df)
        
        # Write to file
        with open('jobs_feed.xml', 'w', encoding='utf-8') as f:
            f.write(xml_data)
            
        print("Successfully updated jobs_feed.xml")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
