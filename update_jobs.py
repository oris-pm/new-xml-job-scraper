def create_xml(df):
    # Current time for the feed header (UTC)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<jobs>')
    
    for _, row in df.iterrows():
        xml.append('  <job>')
        
        # This mapping converts your new Apify/Google Sheet columns 
        # into the standard tags JBoard needs.
        mapping = {
            'title': 'title',
            'company': 'companyName',    # Changed per your request
            'url': 'applyUrl',           # Changed per your request
            'description': 'descriptionHtml', # Changed per your request
            'location': 'location',
            'date': 'postingDate'
        }

        for tag, col_name in mapping.items():
            # Check if the column exists in your sheet
            if col_name in df.columns:
                val = str(row[col_name]) if pd.notna(row[col_name]) else ""
                # XML Safety: escape special characters
                val = val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                xml.append(f'    <{tag}>{val}</{tag}>')
            else:
                # Provide an empty tag if the column is missing to avoid breaking JBoard
                xml.append(f'    <{tag}></{tag}>')
                
        xml.append('  </job>')
    
    xml.append('</jobs>')
    return '\n'.join(xml)
