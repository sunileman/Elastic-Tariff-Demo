import json

from utils.es_config import index_name, elser_index_name, elser_model, model, vector_embedding_field, \
    elser_embedding_field, ada002_index_name
from utils.openai_embedder import get_embedding

from utils.openai_helper import get_openai_guidance, get_openai_guidance_no_context, \
    get_openai_large_guidance
from variables import ner_model


def build_bm25_query(user_query, selected_authors=[], selected_states=[], selected_companies=[] ):
    # Base query
    base_query = {
        "match": {
            "text_field": {
                "query": user_query  # Use the passed in user query
            }
        }
    }

    filters = []

    # If authors are selected, we'll add a filter
    if selected_authors:
        filters.append({
            "terms": {
                "metadata.author.keyword": selected_authors
            }
        })

    # If companies are selected, we'll add a filter
    if selected_companies:
        filters.append({
            "terms": {
                "metadata.company.keyword": selected_companies
            }
        })

    # If states are selected, we'll add a filter
    if selected_states:
        filters.append({
            "terms": {
                "metadata.state.keyword": selected_states
            }
        })

    # Combining the base query and filters
    if filters:
        base_query = {
            "bool": {
                "must": base_query,
                "filter": filters
            }
        }

    full_query = {
        "query": base_query,
        "aggs": {
            "author_facet": {
                "terms": {
                    "field": "metadata.author.keyword",
                    "min_doc_count": 1
                }
            },
            "company_facet": {
                "terms": {
                    "field": "metadata.company.keyword",
                    "min_doc_count": 1
                }
            },
            "state_facet": {
                "terms": {
                    "field": "metadata.state.keyword",
                    "min_doc_count": 1
                }
            },
            "tarrif_category_facet": {
                "terms": {
                    "field": "metadata.tarrif_category.keyword",
                    "min_doc_count": 1
                }
            },
            "tarrif_type_facet": {
                "terms": {
                    "field": "metadata.tarrif_type.keyword",
                    "min_doc_count": 1
                }
            }
        }
    }

    # Dump the assembled query for debugging
    print(json.dumps(full_query, indent=4))

    return full_query


def build_hybrid_query(user_query, selected_authors, selected_states, selected_companies, BM25_Boost, KNN_Boost):
    """
    Builds a hybrid Elasticsearch query based on the provided parameters.

    Returns:
    - A dictionary representing the Elasticsearch query.
    """

    # Base structure for text match query
    text_query = {
        "query": "Does Demethanized contain isobutane in texas",
        "boost": BM25_Boost
    }

    # Base structure for knn
    knn_structure = {
        "field": vector_embedding_field,
        "k": 10,
        "num_candidates": 100,
        "query_vector_builder": {
            "text_embedding": {
                "model_id": model,
                "model_text": user_query
            }
        },
        "boost": KNN_Boost
    }

    main_filters = []
    if selected_authors:
        main_filters.append({
            "terms": {
                "metadata.author.keyword": selected_authors
            }
        })

    # If companies are selected, we'll add a filter
    if selected_companies:
        main_filters.append({
            "terms": {
                "metadata.company.keyword": selected_companies
            }
        })

    if selected_states:
        main_filters.append({
            "terms": {
                "metadata.state.keyword": selected_states
            }
        })

    # Copy the main_filters for the knn part
    knn_filters = list(main_filters)

    query = {
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "text": text_query
                    }
                },
                "filter": main_filters
            }
        },
        "knn": knn_structure,
        "aggs": {
            "author_facet": {
                "terms": {
                    "field": "metadata.author.keyword",
                    "min_doc_count": 1
                }
            },
            "company_facet": {
                "terms": {
                    "field": "metadata.company.keyword",
                    "min_doc_count": 1
                }
            },
            "state_facet": {
                "terms": {
                    "field": "metadata.state.keyword",
                    "min_doc_count": 1
                }
            },
            "tariff_category_facet": {
                "terms": {
                    "field": "metadata.tariff_category.keyword",
                    "min_doc_count": 1
                }
            },
            "tariff_type_facet": {
                "terms": {
                    "field": "metadata.tariff_type.keyword",
                    "min_doc_count": 1
                }
            }
        }
    }

    if knn_filters:
        query["knn"]["filter"] = knn_filters

    return query


def build_elser_hybrid_query(user_query, selected_authors, selected_states, selected_companies,  bm25_boost, elser_boost):
    """
    Builds an Elasticsearch hybrid query combining BM25 and Elser.

    Returns:
    - A dictionary representing the Elasticsearch query.
    """

    # Base structure for text_expansion
    text_expansion_structure = {
        "text_expansion": {
            elser_embedding_field: {
                "model_text": user_query,
                "model_id": elser_model
            }
        }
    }

    text_expansion_structure["text_expansion"][elser_embedding_field]["boost"] = elser_boost

    # Base structure for query_string
    query_string_structure = {
        "query_string": {
            "default_field": "text",  # Assuming text is the main field you're querying
            "query": user_query
        }
    }

    query_string_structure["query_string"]["boost"] = bm25_boost

    query = {
        "query": {
            "bool": {
                "should": [
                    text_expansion_structure,
                    query_string_structure
                ],
                "filter": []
            }
        },
        "aggs": {
            "author_facet": {
                "terms": {
                    "field": "metadata.author.keyword",
                    "min_doc_count": 1
                }
            },
            "state_facet": {
                "terms": {
                    "field": "metadata.state.keyword",
                    "min_doc_count": 1
                }
            },
            "company_facet": {
                "terms": {
                    "field": "metadata.company.keyword",
                    "min_doc_count": 1
                }
            }
        }
    }

    filters = []
    if selected_authors:
        filters.append({
            "terms": {
                "metadata.author.keyword": selected_authors
            }
        })

    # If companies are selected, we'll add a filter
    if selected_companies:
        filters.append({
            "terms": {
                "metadata.company.keyword": selected_companies
            }
        })

    if selected_states:
        filters.append({
            "terms": {
                "metadata.state.keyword": selected_states
            }
        })

    if filters:
        query["query"]["bool"]["filter"] = filters

    return query


def build_knn_query(user_query, selected_authors=None, selected_states=None, selected_companies=None):
    """
    Builds an Elasticsearch KNN query based on the provided parameters.

    Parameters:
    - user_query: The query text input by the user.
    - selected_authors (optional): List of selected authors.
    - selected_states (optional): List of selected states.

    Returns:
    - A dictionary representing the Elasticsearch KNN query.
    """

    # Base KNN query structure
    knn_query = {
        "field": vector_embedding_field,  # Adjust according to your ES schema
        "k": 10,
        "num_candidates": 100,
        "query_vector_builder": {
            "text_embedding": {
                "model_id": model,
                "model_text": user_query
            }
        }
    }

    filters = []

    # If authors are selected, add the author filter
    if selected_authors:
        filters.append({
            "terms": {
                "metadata.author.keyword": selected_authors
            }
        })

    # If companies are selected, we'll add a filter
    if selected_companies:
        filters.append({
            "terms": {
                "metadata.company.keyword": selected_companies
            }
        })

    # If states are selected, add the state filter
    if selected_states:
        filters.append({
            "terms": {
                "metadata.state.keyword": selected_states
            }
        })

    # If there are any filters, add them to the KNN query
    if filters:
        knn_query["filter"] = {
            "bool": {
                "filter": filters
            }
        }

    # Final query structure including aggregations
    full_query = {
        "knn": knn_query,
        "aggs": {
            "author_facet": {
                "terms": {
                    "field": "metadata.author.keyword",
                    "min_doc_count": 1
                }
            },
            "company_facet": {
                "terms": {
                    "field": "metadata.company.keyword",
                    "min_doc_count": 1
                }
            },
            "state_facet": {
                "terms": {
                    "field": "metadata.state.keyword",
                    "min_doc_count": 1
                }
            },
            "tarrif_category_facet": {
                "terms": {
                    "field": "metadata.tarrif_category.keyword",
                    "min_doc_count": 1
                }
            },
            "tarrif_type_facet": {
                "terms": {
                    "field": "metadata.tarrif_type.keyword",
                    "min_doc_count": 1
                }
            }
        }
    }

    # Dump the assembled query for debugging
    print(json.dumps(full_query, indent=4))

    return full_query


def build_rrf_query(user_query, selected_authors, selected_states, selected_companies, rrf_rank_constant, rrf_window_size):
    """
    Builds an Elasticsearch query with rank (rrf) for tariffs based on the provided parameters.

    Returns:
    - A dictionary representing the Elasticsearch query.
    """

    query = {
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "text": user_query  # Assuming "text" is the field containing the main tariff content
                    }
                },
                "filter": []
            }
        },
        "knn": {
            "field": vector_embedding_field,  # Ensure this field aligns with your indexed data
            "query_vector_builder": {
                "text_embedding": {
                    "model_id": model,
                    "model_text": user_query
                }
            },
            "k": 10,
            "num_candidates": 100,
            "filter": []  # Ensure the filter section is present under knn
        },
        "rank": {
            "rrf": {
                "window_size": rrf_window_size,
                "rank_constant": rrf_rank_constant
            }
        },
        "aggs": {
            "author_facet": {
                "terms": {
                    "field": "metadata.author.keyword",
                    "min_doc_count": 1
                }
            },
            "state_facet": {
                "terms": {
                    "field": "metadata.state.keyword",
                    "min_doc_count": 1
                }
            },
            "company_facet": {
                "terms": {
                    "field": "metadata.company.keyword",
                    "min_doc_count": 1
                }
            }
        }
    }

    filters = []
    if selected_authors:
        filters.append({
            "terms": {
                "metadata.author.keyword": selected_authors
            }
        })

    # If companies are selected, we'll add a filter
    if selected_companies:
        filters.append({
            "terms": {
                "metadata.company.keyword": selected_companies
            }
        })

    if selected_states:
        filters.append({
            "terms": {
                "metadata.state.keyword": selected_states
            }
        })

    if filters:
        query["query"]["bool"]["filter"] = filters
        query["knn"]["filter"] = filters

    return query


def build_elser_query(user_query, selected_authors, selected_states, selected_companies):
    # Base query
    base_query = {
        "text_expansion": {
            elser_embedding_field: {
                "model_id": ".elser_model_1",
                "model_text": user_query
            }
        }
    }

    filters = []

    # If authors are selected, we'll add a filter
    if selected_authors:
        filters.append({
            "terms": {
                "metadata.author.keyword": selected_authors
            }
        })

    # If companies are selected, we'll add a filter
    if selected_companies:
        filters.append({
            "terms": {
                "metadata.company.keyword": selected_companies
            }
        })

    # If states are selected, we'll add a filter
    if selected_states:
        filters.append({
            "terms": {
                "metadata.state.keyword": selected_states
            }
        })

    if filters:
        base_query = {
            "bool": {
                "must": base_query,
                "filter": filters
            }
        }

    query = {
        "size": 5,
        "query": base_query,
        "aggs": {
            "author_facet": {
                "terms": {
                    "field": "metadata.author.keyword",
                    "min_doc_count": 1
                }
            },
            "company_facet": {
                "terms": {
                    "field": "metadata.company.keyword",
                    "min_doc_count": 1
                }
            },
            "state_facet": {
                "terms": {
                    "field": "metadata.state.keyword",
                    "min_doc_count": 1
                }
            },
            "tarrif_category_facet": {
                "terms": {
                    "field": "metadata.tarrif_category.keyword",
                    "min_doc_count": 1
                }
            },
            "tarrif_type_facet": {
                "terms": {
                    "field": "metadata.tarrif_type.keyword",
                    "min_doc_count": 1
                }
            }
        }
    }

    print(json.dumps(query, indent=4))
    return query




import json

def build_openai_query(embeddings, selected_states=[], selected_companies=[], optional_state=None):
    """
    Builds an Elasticsearch KNN query using OpenAI embeddings and includes aggregations.

    Parameters:
    - embeddings: The vector embeddings.
    - selected_states (optional): List of selected states.
    - selected_companies (optional): List of selected companies.
    - optional_state (optional): State value for the should clause.

    Returns:
    - A dictionary representing the Elasticsearch KNN query.
    """

    # Base KNN query structure
    knn_query = {
        "field": "vector_query_field.predicted_value",  # Field containing the OpenAI embeddings
        "k": 10,
        "num_candidates": 100,
        "query_vector": embeddings
    }

    filters = []
    bool_query = {}

    # If states are selected, add the state filter
    if selected_states:
        filters.append({
            "terms": {
                "metadata.state.keyword": selected_states
            }
        })

    # If companies are selected, we'll add a filter
    if selected_companies:
        filters.append({
            "terms": {
                "metadata.company.keyword": selected_companies
            }
        })

    # If there's an optional_state, add the should clause
    if optional_state:
        bool_query["should"] = {
            "term": {
                "metadata.state.keyword": optional_state
            }
        }

    # If there are any filters, add them to the bool query
    if filters:
        bool_query["filter"] = filters

    # If the bool_query is not empty, add it to the knn_query
    if bool_query:
        knn_query["filter"] = {
            "bool": bool_query
        }

    # Final query structure including aggregations
    full_query = {
        "knn": knn_query,
        "aggs": {
            "company_facet": {
                "terms": {
                    "field": "metadata.company.keyword",
                    "min_doc_count": 1
                }
            },
            "state_facet": {
                "terms": {
                    "field": "metadata.state.keyword",
                    "min_doc_count": 1
                }
            },
            "tariff_category_facet": {
                "terms": {
                    "field": "metadata.tariff_type.keyword",
                    "min_doc_count": 1
                }
            },
            "tariff_type_facet": {
                "terms": {
                    "field": "metadata.tariff_type.keyword",
                    "min_doc_count": 1
                }
            }
        }
    }

    # Dump the assembled query for debugging
    print(json.dumps(full_query, indent=4))

    return full_query


def get_loc_entity(result):
    for doc in result.get('inference_results', []):
        entities = doc.get('entities', [])
        for entity in entities:
            if entity['class_name'] == "LOC":
                return entity['entity']
    return None  # Return None if no LOC entity is found




def run_ner_inference(es, input_text):
    docs = [{"text_field": input_text}]

    # Use the infer_trained_model method
    response = es.ml.infer_trained_model(model_id=ner_model, docs=docs)

    return get_loc_entity(response)





def search_tariffs(es, user_query, searchtype, BM25_Boost, KNN_Boost, rrf_rank_constant, rrf_window_size,
                   selected_authors, selected_states, selected_companies):
    # Select the appropriate query building function based on searchtype
    if searchtype == "Vector Hybrid":
        query = build_hybrid_query(user_query, selected_authors, selected_states, selected_companies, BM25_Boost, KNN_Boost)
    elif searchtype == "Vector":
        query = build_knn_query(user_query, selected_authors, selected_states, selected_companies)
    elif searchtype == "BM25":
        query = build_bm25_query(user_query, selected_authors, selected_states, selected_companies)
    elif searchtype == "Reciprocal Rank Fusion":
        query = build_rrf_query(user_query, selected_authors, selected_states, selected_companies, rrf_rank_constant, rrf_window_size)
    elif searchtype == "Elser":
        query = build_elser_query(user_query, selected_authors, selected_states, selected_companies)
    elif searchtype == "Elser Hybrid":
        query = build_elser_hybrid_query(user_query, selected_authors, selected_states, selected_companies, BM25_Boost, KNN_Boost)
    elif searchtype == "Vector OpenAI":
        query = build_openai_query(get_embedding(user_query), selected_states, selected_companies, run_ner_inference(es, user_query))
    elif searchtype == "GenAI":
        print("GenAI Search Only")
    else:
        raise ValueError(f"Invalid searchtype: {searchtype}")

    if searchtype == "Vector OpenAI":
        results = es.search(index=ada002_index_name, body=query, _source=True)
    elif searchtype == "Elser" or searchtype == "Elser Hybrid":
        results = es.search(index=elser_index_name, body=query, _source=True)
    elif searchtype != "GenAI":
        results = es.search(index=index_name, body=query, _source=True)
    else:
        results=[]
        print("GenAI Search Only")

    # Set a default value for num_results
    num_results = 0
    authors = ""
    # Check if there are any hits
    if results and results.get('hits') and results['hits'].get('hits'):
        # Limit the number of results displayed

        num_results = min(5, len(results['hits']['hits']))

        for i in range(num_results):
            hit = results['hits']['hits'][i]
            # Retrieve the game title and platform from _source or fields, depending on the structure of your results
            if searchtype == "Vector OpenAI":
                authors = []
            else:
                authors = [bucket['key'] for bucket in results['aggregations']['author_facet']['buckets']]
            if searchtype == "Elser" or searchtype == "Elser Hybrid":
                text_list = [hit['_source']['text'] for hit in results['hits']['hits'] if 'text' in hit['_source']]
            else:
                text_list = [hit['_source']['text_field'] for hit in results['hits']['hits'] if
                             'text_field' in hit['_source']]

            # Print the results
            print("Authors:")
            for author in authors:
                print(author)

            print("\nTexts:")
            for text in text_list:
                print(text)
                print("-------------------------------")

    else:
        print("No results found.")

    if searchtype == "Vector OpenAI":
        return get_openai_large_guidance(user_query, results, num_results, searchtype)
    elif searchtype == "GenAI":
        return get_openai_guidance_no_context(user_query)
    else:
        return get_openai_guidance(user_query, results, num_results, searchtype)
