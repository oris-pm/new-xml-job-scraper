import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# Your specific Google Sheet ID and Export URL
SHEET_ID = '1SHM5ut3bUQP6NUZ3_a9Q7Bkp60EY5NEM4oNIFaMMHL4'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv'

def create_xml(df):
    # Current time ensures GitHub always sees a file change
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<jobs>')
    xml.append(f'  <last_build_date>{now}</last_build_date>')
    
    for _, row in df.iterrows():
        xml.append('  <job>')
        
        # This loop looks at your Sheet's headers and creates tags automatically
        for col_name in df.columns:
            # Clean column names: no spaces, all lowercase (e.g., "Company Name" -> "company_name")
            tag = str(col_name).strip().replace(' ', '_').lower()
            
            # Handle the data in the row
            val = str(row[col_name]) if pd.notna(row[col_name]) else ""
            
            # XML Safety: Escaping characters that break XML structure
            val = val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            
            xml.append(f'    <{tag}>{val}</{tag}>')
                
        xml.append('  </job>')
    
    xml.append('</jobs>')
    return '\n'.join(xml)

def main():
    try:
        print("Connecting to Google Sheets...")
        response = requests.get(URL)
        response.raise_for_status() 
        
        # Load data
        df = pd.read_csv(StringIO(response.text)).dropna(how='all')
        
        # Logic to ensure we actually have data
        if df.empty:
            print("Warning: Google Sheet appears to be empty.")
            return

        print(f"Found columns: {list(df.columns)}")
        print(f"Processing {len(df)} jobs...")
        
        # Generate the XML
        xml_data = create_xml(df)
        
        # Save to the repository
        with open('jobs_feed.xml', 'w', encoding='utf-8') as f:
            f.write(xml_data)
            
        print("Successfully updated jobs_feed.xml")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()
