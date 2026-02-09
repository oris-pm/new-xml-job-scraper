import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# Your specific Google Sheet ID and Export URL
SHEET_ID = '1SHM5ut3bUQP6NUZ3_a9Q7Bkp60EY5NEM4oNIFaMMHL4'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv'

def create_xml(df):
    # Current time for the feed header (UTC) - ensures the file is always "new"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<jobs>')
    # This timestamp forces GitHub to see a change even if job data is the same
    xml.append(f'  <last_build_date>{now}</last_build_date>')
    
    for _, row in df.iterrows():
        xml.append('  <job>')
        
        # MAPPING: 'JBoard_Tag': 'Apify_Column_Name'
        # We translate your new Apify names back to standard JBoard tags
        mapping = {
            'title': 'title',
            'company': 'companyName',      # Mapped from companyName
            'url': 'applyUrl',             # Mapped from applyUrl
            'description': 'descriptionHtml', # Mapped from descriptionHtml
            'location': 'location',
            'date': 'postingDate'
        }

        for tag, col_name in mapping.items():
            if col_name in df.columns:
                val = str(row[col_name]) if pd.notna(row[col_name]) else ""
                # XML Safety: replace characters that break XML structure
                val = val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                xml.append(f'    <{tag}>{val}</{tag}>')
            else:
                # Add empty tag so JBoard doesn't encounter a missing field error
                xml.append(f'    <{tag}></{tag}>')
                
        xml.append('  </job>')
    
    xml.append('</jobs>')
    return '\n'.join(xml)

def main():
    try:
        # 1. Fetch data from Google Sheets
        print("Fetching data from Google Sheets...")
        response = requests.get(URL)
        response.raise_for_status() 
        
        # 2. Load data and drop completely empty rows
        df = pd.read_csv(StringIO(response.text)).dropna(how='all')
        
        # 3. Convert data to XML format
        print(f"Converting {len(df)} jobs to XML...")
        xml_data = create_xml(df)
        
        # 4. Save to the repository file
        with open('jobs_feed.xml', 'w', encoding='utf-8') as f:
            f.write(xml_data)
        print("Successfully updated jobs_feed.xml locally.")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()
