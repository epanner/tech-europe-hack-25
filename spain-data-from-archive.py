import requests
import pandas as pd 
import sqlite3
import time
import logging
import os
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(
    level=logging.ERROR,
    format='[%(levelname)s] %(message)s'
)

def download_pdf(primary_url, filename):
    logging.info(f"Trying to download from primary source: {primary_url}")
    response = requests.get(primary_url, stream=True)

    if response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info(f"Downloaded from primary source: {filename}")
    else:
        logging.warning(f"Primary download failed (status code {response.status_code}). Trying archive.org...")
        download_from_archive(primary_url, filename)

def get_first_snapshot_url(original_url):
    cdx_api = "http://web.archive.org/cdx/search/cdx"
    params = {
        "url": original_url,
        "output": "json",
        "fl": "timestamp",
        "filter": "statuscode:200",
        "limit": 1,
        "sort": "ascending"
    }

    response = requests.get(cdx_api, params=params)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 1:
            first_timestamp = data[1][0]
            archive_url = f"https://web.archive.org/web/{first_timestamp}/{original_url}"
            return archive_url
    return None

def download_from_archive(original_url, filename):
    snapshot_url = get_first_snapshot_url(original_url)
    if snapshot_url:
        logging.info(f"Trying first archive snapshot: {snapshot_url}")
        response = requests.get(snapshot_url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logging.warning(f"Downloaded from archive.org: {filename}")
        else:
            logging.error(f"Failed to download from archive snapshot for {original_url} \n\t (status {response.status_code})")
    else:
        logging.error(f"No snapshot found in archive.org for {original_url}")

def download_if_pdf(row):
    verdict_link = row['verdict_link']
    if verdict_link.split('.')[-1].lower() == "pdf":
        local_filename = verdict_link.split('/')[-1]
        download_pdf(verdict_link, os.path.join("verdicts", local_filename))
        time.sleep(1)

if __name__ == "__main__":
    connector_obj = sqlite3.connect("gdpr_fines.db")
    query = "SELECT * FROM fines WHERE country = 'spain'"
    df = pd.read_sql_query(query, connector_obj)

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(download_if_pdf, [row for _, row in df.iterrows()])
