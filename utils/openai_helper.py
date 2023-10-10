import openai
import time

from variables import openai_completion_deployment_name, openai_completion_large_deployment_name, openai_api_sa_base
from variables import openai_api_type, openai_api_base, openai_api_version

import streamlit as st



def get_openai_guidance(user_query, results, num_results, searchtype):
    openai.api_type = openai_api_type
    openai.api_base = openai_api_base
    openai.api_version = openai_api_version

    # Set the GPT-3 API key
    openai.api_key = st.secrets['pass']

    processed_results = []
    retry_attempts = 3  # Number of retries before failing

    for idx in range(num_results):
        if searchtype == "Elser" or searchtype == "Elser Hybrid":
            text = results['hits']['hits'][idx]["_source"]["text"]
        elif searchtype == "Vector OpenAI":
            text = results['hits']['hits'][idx]["_source"]["content"]
        else:
            text = results['hits']['hits'][idx]["_source"]["text_field"]
        # text = results['hits']['hits'][idx]["_source"]["text"]
        if searchtype != "Vector OpenAI":
            author = results['hits']['hits'][idx]["_source"]["metadata"]["author"]
        else:
            author = ""
        company = results['hits']['hits'][idx]["_source"]["metadata"]["company"]
        state = results['hits']['hits'][idx]["_source"]["metadata"]["state"]
        doc_url = results['hits']['hits'][idx]["_source"]["metadata"]["url"]
        tariff_title = results['hits']['hits'][idx]["_source"]["metadata"]["tarrif_title"]
        score = results['hits']['hits'][idx]["_score"]

        for _ in range(retry_attempts):
            try:
                response = openai.ChatCompletion.create(
                    engine=openai_completion_deployment_name,
                    messages=[
                        {"role": "system",
                         "content": "You are an AI assistant. Your answers should stay short and concise. explain your answer. no formalities."},
                        {"role": "user",
                         "content": f"Answer this question {user_query} based on the following text {text}"}
                    ],
                    temperature=0.7,
                    max_tokens=800,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None)

                # print(response['choices'][0]['message']['content'])
                completion_output = response['choices'][0]['message']['content'].strip()
                processed_results.append((text, completion_output, score, author, state, doc_url, tariff_title, company))
                break  # If successful, break out of the retry loop

            except openai.error.RateLimitError as e:
                # Handle rate limit error
                if _ < retry_attempts - 1:  # If it's not the last attempt
                    print(f"Rate Limit Error: {e}. Retrying in 1 second...")
                    time.sleep(1)  # Wait for 1 second before retrying
                else:
                    print(f"Rate Limit Error: {e}. No more retries.")

            except openai.error.APIError as e:
                print(f"OpenAI API returned an API Error: {e}")
                break

            except openai.error.AuthenticationError as e:
                print(f"OpenAI API returned an Authentication Error: {e}")
                break

            except openai.error.APIConnectionError as e:
                print(f"Failed to connect to OpenAI API: {e}")
                break

            except openai.error.InvalidRequestError as e:
                print(f"Invalid Request Error: {e}")
                break

            except openai.error.ServiceUnavailableError as e:
                print(f"Service Unavailable: {e}")
                break

            except openai.error.Timeout as e:
                print(f"Request timed out: {e}")
                break

            except:
                # Handles all other exceptions
                print("An unexpected exception has occurred.")
                break

            time.sleep(4)

    return processed_results, results


def get_openai_large_guidance(user_query, results, num_results, searchtype):
    openai.api_type = openai_api_type
    openai.api_base = openai_api_sa_base
    openai.api_version = openai_api_version

    # Set the GPT-3 API key
    openai.api_key = st.secrets['sa_pass']

    processed_results = []
    retry_attempts = 3  # Number of retries before failing

    for idx in range(num_results):
        if searchtype == "Elser" or searchtype == "Elser Hybrid":
            text = results['hits']['hits'][idx]["_source"]["text"]
        elif searchtype == "Vector OpenAI":
            text = results['hits']['hits'][idx]["_source"]["content"]
        else:
            text = results['hits']['hits'][idx]["_source"]["text_field"]
        # text = results['hits']['hits'][idx]["_source"]["text"]
        if searchtype != "Vector OpenAI":
            author = results['hits']['hits'][idx]["_source"]["metadata"]["author"]
        else:
            author = ""
        company = results['hits']['hits'][idx]["_source"]["metadata"]["company"]
        state = results['hits']['hits'][idx]["_source"]["metadata"]["state"]
        doc_url = results['hits']['hits'][idx]["_source"]["metadata"]["url"]
        tariff_title = results['hits']['hits'][idx]["_source"]["metadata"]["tarrif_title"]
        score = results['hits']['hits'][idx]["_score"]

        for _ in range(retry_attempts):
            try:
                response = openai.ChatCompletion.create(
                    engine=openai_completion_large_deployment_name ,
                    messages=[
                        {"role": "system",
                         "content": "You are an AI assistant. Your answers should stay short and concise. explain your answer. no formalities."},
                        {"role": "user",
                         "content": f"Answer this question {user_query} based on the following text {text}"}
                    ],
                    temperature=0.7,
                    max_tokens=800,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None)

                # print(response['choices'][0]['message']['content'])
                completion_output = response['choices'][0]['message']['content'].strip()
                processed_results.append((text, completion_output, score, author, state, doc_url, tariff_title, company))
                break  # If successful, break out of the retry loop

            except openai.error.RateLimitError as e:
                # Handle rate limit error
                if _ < retry_attempts - 1:  # If it's not the last attempt
                    print(f"Rate Limit Error: {e}. Retrying in 1 second...")
                    time.sleep(1)  # Wait for 1 second before retrying
                else:
                    print(f"Rate Limit Error: {e}. No more retries.")

            except openai.error.APIError as e:
                print(f"OpenAI API returned an API Error: {e}")
                break

            except openai.error.AuthenticationError as e:
                print(f"OpenAI API returned an Authentication Error: {e}")
                break

            except openai.error.APIConnectionError as e:
                print(f"Failed to connect to OpenAI API: {e}")
                break

            except openai.error.InvalidRequestError as e:
                print(f"Invalid Request Error: {e}")
                break

            except openai.error.ServiceUnavailableError as e:
                print(f"Service Unavailable: {e}")
                break

            except openai.error.Timeout as e:
                print(f"Request timed out: {e}")
                break

            except:
                # Handles all other exceptions
                print("An unexpected exception has occurred.")
                break

            time.sleep(4)

    return processed_results, results



def get_openai_guidance_no_context(user_query):
    openai.api_type = openai_api_type
    openai.api_base = openai_api_base
    openai.api_version = openai_api_version

    # Set the GPT-3 API key
    openai.api_key = st.secrets['pass']

    processed_results = []
    results = []
    retry_attempts = 3  # Number of retries before failing

    # Note: The openai-python library support for Azure OpenAI is in preview.

    for _ in range(retry_attempts):
        try:
            response = openai.ChatCompletion.create(
                engine=openai_completion_deployment_name,
                messages=[
                    {"role": "system",
                     "content": "You are an AI assistant. Your answers should stay short and concise. explain your answer. no formalities."},
                    {"role": "user", "content": f"Answer this question {user_query}"}
                ],
                temperature=0.7,
                max_tokens=800,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None)

            # print(response['choices'][0]['message']['content'])
            completion_output = response['choices'][0]['message']['content'].strip()
            processed_results.append(completion_output)
            break  # If successful, break out of the retry loop

        except openai.error.RateLimitError as e:
            # Handle rate limit error
            if _ < retry_attempts - 1:  # If it's not the last attempt
                print(f"Rate Limit Error: {e}. Retrying in 1 second...")
                time.sleep(1)  # Wait for 1 second before retrying
            else:
                print(f"Rate Limit Error: {e}. No more retries.")

        except openai.error.APIError as e:
            print(f"OpenAI API returned an API Error: {e}")
            break

        except openai.error.AuthenticationError as e:
            print(f"OpenAI API returned an Authentication Error: {e}")
            break

        except openai.error.APIConnectionError as e:
            print(f"Failed to connect to OpenAI API: {e}")
            break

        except openai.error.InvalidRequestError as e:
            print(f"Invalid Request Error: {e}")
            break

        except openai.error.ServiceUnavailableError as e:
            print(f"Service Unavailable: {e}")
            break

        except openai.error.Timeout as e:
            print(f"Request timed out: {e}")
            break

        except:
            # Handles all other exceptions
            print("An unexpected exception has occurred.")
            break

        time.sleep(4)

    return processed_results, results
