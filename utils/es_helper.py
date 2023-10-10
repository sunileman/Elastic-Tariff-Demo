from elasticsearch import Elasticsearch


def create_es_client(username, password, cloudid):
    es = Elasticsearch(
        cloud_id=cloudid,
        basic_auth=(username, password)
    )
    return es



def manage_index(es: Elasticsearch, index_name: str, settings: dict, mappings: dict, deleteIndex: bool):
    if es.indices.exists(index=index_name):
        if deleteIndex:
            print(f"Index {index_name} exists. Deleting it...")
            es.indices.delete(index=index_name)
            print(f"Index {index_name} deleted!")
            es.indices.create(index=index_name, settings=settings, mappings=mappings)
            print(f"Index {index_name} created successfully!")
        else:
            print(f"Index {index_name} exists and deleteIndex is False. Doing nothing...")
            return
    else:
        # Create new index with the specified mappings
        es.indices.create(index=index_name, settings=settings, mappings=mappings)
        print(f"Index {index_name} created successfully!")
