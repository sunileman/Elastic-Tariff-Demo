import sys

from elasticsearch import Elasticsearch, helpers

from utils.es_helper import create_es_client
import streamlit as st


try:
    username = st.secrets['es_username']
    password = st.secrets['es_password']
    cloudid = st.secrets['es_cloudid']
    es = create_es_client(username, password, cloudid)
except Exception as e:
    print("Connection failed", str(e))
    sys.exit(1)



def fetch_all_records_from_index(es, index_name):
    """Generator that yields all records from an Elasticsearch index."""
    query_body = {
        "query": {
            "match_all": {}
        }
    }

    # Use the scan helper to fetch records without a size limit
    for record in helpers.scan(es, query=query_body, index=index_name):
        yield record['_source']


def main():
    # Connect to Elasticsearch

    # Name of the index you want to pull records from
    index_name = "workplace-app-tariffs-summary-ada-002"

    # Output file
    output_file = "../output/workplace-app-tariffs-summary-ada-002.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        for record in fetch_all_records_from_index(es, index_name):
            # Write each document as a single line (serialized as JSON)
            f.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    import json

    main()
