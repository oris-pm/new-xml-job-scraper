import pandas as pd
import requests
from io import StringIO

# Replace with your actual Sheet ID
SHEET_ID = 'YOUR_GOOGLE_SHEET_ID_HERE'
URL = f'https://docs.google.com/spreadsheets/d/1SHM5ut3bUQP6NUZ3_a9Q7Bkp60EY5NEM4oNIFaMMHL4/export?format=csv'

def create_xml(df):
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<jobs>']
    for _, row in df.iterrows():
        xml.append('  <job>')
        for col in df.columns:
            # Clean column names for XML tags (remove spaces)
            tag = col.replace(' ', '_').lower()
            xml.append(f'    <{tag}>{row[col]}</{tag}>')
        xml.append('  </job>')
    xml.append('</jobs>')
    return '\n'.join(xml)

def main():
    # Fetch data
    response = requests.get(URL)
    df = pd.read_csv(StringIO(response.text))
    
    # Convert and Save
    xml_data = create_xml(df)
    with open('jobs_feed.xml', 'w', encoding='utf-8') as f:
        f.write(xml_data)

if __name__ == "__main__":
    main()
