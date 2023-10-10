import openai
import time
import utils.es_config
from utils import es_config
from variables import openai_embedding_deployment_name
from variables import openai_api_type, openai_api_base, openai_api_version
import streamlit as st

def get_embedding(input_text):

    openai.api_type = openai_api_type
    openai.api_base = openai_api_base
    openai.api_version = openai_api_version


    # Set the GPT-3 API key
    openai.api_key = st.secrets['pass']

    response = openai.Embedding.create(
        input=input_text,
        engine=openai_embedding_deployment_name,
        max_tokens=25
    )
    #print (input_text)

    embeddings = response['data'][0]['embedding']
    print(embeddings)
    time.sleep(es_config.rate_throttle)
    return embeddings
