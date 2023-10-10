# Import the required libraries
from elasticsearch import helpers
import json

from utils.es_config import elser_index_name, settings, elser_mapping, deleteExistingIndex
from utils.es_helper import create_es_client, manage_index
import streamlit as st

try:

    username = st.secrets['es_username']
    password = st.secrets['es_password']
    cloudid = st.secrets['es_cloudid']

    # get es object
    es = create_es_client(username, password, cloudid)

    print(es.info())
except Exception as e:
    print("Connection failed", e.errors)


file_paths = ["../output/workplace-app-tariffs-elser.json"]


##create index
manage_index(es, elser_index_name, settings, elser_mapping, deleteExistingIndex)


def generate_actions(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip():  # Skip empty lines
                continue
            record = json.loads(line.strip())
            yield {
                "_index": elser_index_name,
                "_source": record
            }



for file_path in file_paths:
    try:
        print(f"Indexing documents from {file_path}...")

        success_count = 0
        failed_count = 0
        for success, _ in helpers.parallel_bulk(es, generate_actions(file_path), thread_count=2, chunk_size=500):
            if success:
                success_count += 1
            else:
                failed_count += 1

        print(f"Successfully indexed {success_count} documents.")
        print(f"Failed to index {failed_count} documents.")
    except helpers.BulkIndexError as e:
        print(e)
        for error_detail in e.errors:
            print(error_detail)


