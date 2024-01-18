# Elastic Tariff Demo


## Setup

***1*** Import Embedding and NER model into ESS
```commandline
docker run -it --rm elastic/eland
    eland_import_hub_model
    --cloud-id xxxxx -u xxxxxxxx -p xxxxxxxx
    --hub-model-id sentence-transformers/all-MiniLM-L6-v2
    --task-type text_embedding
    --start
```

```commandline
docker run -it --rm elastic/eland
    eland_import_hub_model
    --cloud-id xxxxx -u xxxxxxxx -p xxxxxxxx
    --hub-model-id elastic__distilbert-base-uncased-finetuned-conll03-english
    --task-type ner
    --start
```
***2*** Start ELSER model in ESS


***3*** Update variables

`.streamlit/secrets.toml`
```
pass = "xxxxxxx"
sa_pass = "xxxxx" ##used for large token model

es_username = 'xxxxx'
es_password = 'xxxxx'
es_cloudid = 'xxxx'
```


'variables.py'
```commandline
openai_api_base = "https://xxxxx.openai.azure.com"
openai_api_sa_base = "https://xxxx.openai.azure.com"
```

***4*** Load tariff data

Run `ingest/download-tariffs.py`

Run `ingest/ingest_tariff_ada.py`

Run `ingest/ingest_tariff_bym.py`

Run `ingest/ingest_tariff_elser.py`



## App UI Launch
To launch the UI run
`streamlit run  Elastic_Tariff_demo.py`
