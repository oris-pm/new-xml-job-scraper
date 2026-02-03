import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# Your specific Google Sheet ID
SHEET_ID = '1SHM5ut3bUQP6NUZ3_a9Q7Bkp60EY5NEM4oNIFaMMHL4'
URL = f'https://docs.google.com/spreadsheets/d/1SHM5ut3bUQP6NUZ3_a9Q7Bkp60EY5NEM4oNIFaMMHL4/export?format=csv'

def create_xml(df):
    # Current time for the feed header (UTC)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append(f'')
    xml.append('<jobs>')
    
    for _, row in df.iterrows():
        xml.append('  <job>')
        for col in df.columns:
            # Clean column names for XML tags
            tag = col.replace(' ', '_').lower()
            # Handle empty values to prevent malformed XML
            val = str(row[col]) if pd.notna(row[col]) else ""
            # Basic character cleaning for XML safety
            val = val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            xml.append(f'    <{tag}>{val}</{tag}>')
        xml.append('  </job>')
    
    xml.append('</jobs>')
    return '\n'.join(xml)

def main():
    try:
        # Fetch data from Google Sheets
        response = requests.get(URL)
        response.raise_for_status() 
        
        # Load data and drop rows that are completely empty
        df = pd.read_csv(StringIO(response.text)).dropna(how='all')
        
        # Convert to XML
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
