import re
import sqlite3
import pandas as pd

if __name__ == "__main__":
    connector_obj = sqlite3.connect("spain_gdpr_fines_gdpr.db")
    query = "SELECT * FROM fines"
    df = pd.read_sql_query(query, connector_obj)

    results = set()

    for _, row in df.iterrows():
        for raw_text in row['gdpr_articles'].split(','):
            results.add(raw_text)
    
    print(results)
