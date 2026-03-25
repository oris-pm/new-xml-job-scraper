import pd as pd
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
            # Clean column names (e.g., "Company Logo" becomes <company_logo>)
            tag = str(col_name).strip().replace(' ', '_').lower()
            
            # Convert value to string and handle empty cells
            val = str(row[col_name]) if pd.notna(row[col_name]) else ""
            
            # XML Safety: Escape problematic characters
            # We use a more robust replace to handle URLs (like logos) that contain '&'
            val = val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
            
            xml.append(f'    <{tag}>{val}</{tag}>')
                
        xml.append('  </job>')
    
    xml.append('</jobs>')
    return '\n'.join(xml)

def main():
    try:
        print(f"Connecting to Google Sheet Table 3 (GID: {GID})...")
        
        response = requests.get(URL)
        response.raise_for_status() 
        
        # Force UTF-8 encoding to fix the "â" character issues
        response.encoding = 'utf-8' 
        
        # Load CSV and drop completely empty rows
        df = pd.read_csv(StringIO(response.text)).dropna(how='all')
        
        if df.empty:
            print("Warning: Table 3 is empty. Check your Google Apps Script execution.")
            return

        print(f"Successfully retrieved {len(df)} jobs.")
        # This will now include 'Company Logo' in the list
        print(f"Columns found: {list(df.columns)}")
        
        xml_data = create_xml(df)
        
        with open('jobs_feed.xml', 'w', encoding='utf-8', errors='replace') as f:
            f.write(xml_data)
            
        print("Successfully updated jobs_feed.xml with UTF-8 safety and Logo support.")
        
    except Exception as e:
        print(f"Error during execution: {e}")
        exit(1)

if __name__ == "__main__":
    main()
