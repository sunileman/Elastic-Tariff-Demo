# Import the required libraries
import sys
from utils.es_helper import create_es_client
import streamlit as st
from utils.query_helper import search_tariffs


# Initialize these variables with default values at the start of the script
BM25_Boost = 0
KNN_Boost = 0
rrf_rank_constant = 0
rrf_window_size = 0

# Connect to Elasticsearch
try:
    username = st.secrets['es_username']
    password = st.secrets['es_password']
    cloudid = st.secrets['es_cloudid']
    es = create_es_client(username, password, cloudid)
except Exception as e:
    print("Connection failed", str(e))
    st.error("Error connecting to Elasticsearch. Fix connection and restart app")
    sys.exit(1)

# Layout columns
col1, col2 = st.columns([1, 3])  # col1 is 1/4 of the width, and col2 is 3/4

# Initialize 'author_checks', 'state_checks' and their associated names if they don't exist
if 'author_checks' not in st.session_state:
    st.session_state.author_checks = {}

if 'company_checks' not in st.session_state:
    st.session_state.company_checks = {}

if 'state_checks' not in st.session_state:
    st.session_state.state_checks = {}

if 'author_names' not in st.session_state:
    st.session_state.author_names = []

if 'company_names' not in st.session_state:
    st.session_state.company_names = []

if 'state_names' not in st.session_state:
    st.session_state.state_names = []

# Initialize the search clicked state
if 'search_clicked' not in st.session_state:
    st.session_state.search_clicked = False

with col2:
    st.subheader('AI-Powered Tariff Search')

    # Sub-columns within col2
    col2a, col2b = st.columns([3, 1])

    with col2a:
        # Search type radio
        searchtype = col2a.radio(
            "Search Method:",
            ("GenAI", "BM25", "Vector", "Vector OpenAI", "Elser", "Vector Hybrid", "Elser Hybrid",
             "Reciprocal Rank Fusion"),
            index=1  # Default to "BM25"
        )

        user_query = col2a.text_area("Tariff Search")

        # ... [rest of your code for searching, displaying results, etc.]

    with col2b:
        # Conditionally display sliders based on `searchtype` value
        BM25_Boost = 0
        KNN_Boost = 0

        if searchtype == "Vector Hybrid" or searchtype == "Elser Hybrid":
            BM25_Boost = col2b.slider(
                "BM25 Score Boost:",
                min_value=0.0,
                max_value=5.0,
                value=0.00,
                step=0.01,
                help="Adjust the BM25 score boost value. Higher values give more weight to BM25 scores."
            )

            KNN_Boost = col2b.slider(
                "KNN Score Boost:",
                min_value=0.0,
                max_value=5.0,
                value=0.00,
                step=0.01,
                help="Adjust the KNN score boost value. Higher values give more weight to KNN scores."
            )

        if searchtype == "Reciprocal Rank Fusion":
            rrf_rank_constant = col2b.slider(
                "Rank Constant:",
                min_value=1,
                max_value=60,
                value=1,
                step=1,
                help="Influences the impact of lower-ranked documents. Higher values give them more influence."
            )

            rrf_window_size = col2b.slider(
                "Window Size",
                min_value=10,
                max_value=200,
                value=10,
                step=1,
                help="Determines size of individual result sets per query. Higher values improve relevance but may reduce performance."
            )

    # Check if searchtype has changed
    if searchtype != st.session_state.get('previous_searchtype', None):
        st.session_state.search_clicked = False
        for author in st.session_state.get('author_names', []):
            st.session_state.author_checks[author] = False
        for state in st.session_state.get('state_names', []):
            st.session_state.state_checks[state] = False
        for company in st.session_state.get('company_names', []):
            st.session_state.company_checks[company] = False
        st.session_state.previous_searchtype = searchtype

    # user_query = st.text_area("Tariff Search")

    if st.button("Search"):
        if user_query:
            # Gather the authors selected by the user from the checkboxes
            if 'author_checks' in st.session_state:
                selected_authors = [author for author, selected in st.session_state.author_checks.items() if selected]
            else:
                selected_authors = []

            # Gather the states selected by the user from the checkboxes
            if 'state_checks' in st.session_state:
                selected_states = [state for state, selected in st.session_state.state_checks.items() if selected]
            else:
                selected_states = []

            # Gather the states selected by the user from the checkboxes
            if 'company_checks' in st.session_state:
                selected_companies = [company for company, selected in st.session_state.company_checks.items() if
                                      selected]
            else:
                selected_companies = []

            # Convert "Not Available" back to ""
            selected_authors = ["" if author == "Not Available" else author for author in selected_authors]
            selected_states = ["" if state == "Not Available" else state for state in selected_states]
            selected_companies = ["" if company == "Not Available" else company for company in selected_companies]

            processed_results, original_results = search_tariffs(es, user_query, searchtype, BM25_Boost, KNN_Boost,
                                                                 rrf_rank_constant, rrf_window_size, selected_authors,
                                                                 selected_states, selected_companies)

            # Retrieve the author buckets from original_results
            if searchtype != "GenAI":
                author_buckets = original_results.get('aggregations', {}).get('author_facet', {}).get('buckets', [])
                author_names = [bucket['key'] if bucket['key'] != "" else "Not Available" for bucket in author_buckets]

                state_buckets = original_results.get('aggregations', {}).get('state_facet', {}).get('buckets', [])
                state_names = [bucket['key'] if bucket['key'] != "" else "Not Available" for bucket in state_buckets]

                # company_buckets = original_results.get('aggregations', {}).get('company_facet', {}).get('buckets', [])
                # company_names = [bucket['key'] if bucket['key'] != "" else "Not Available" for bucket in company_buckets]

                ##new code
                # Extract companies from the original_results aggregations
                company_buckets = original_results.get('aggregations', {}).get('company_facet', {}).get('buckets', [])
                existing_companies = [bucket['key'] for bucket in company_buckets]

                # Extract companies from processed_results
                companies_from_results = [company for _, _, _, _, _, _, _, company in processed_results]

                # Merge the two lists and remove duplicates
                all_companies = list(set(existing_companies + companies_from_results))

                # Convert "Not Available" if needed
                all_companies = ["Not Available" if company == "" else company for company in all_companies]

                # If you still want this in the original bucket format (assuming other fields like 'doc_count' are important):
                company_buckets = [{'key': company, 'doc_count': existing_companies.count(company)} for company in
                                   all_companies]

                # Update the author and state names in the session state
                st.session_state.author_names = author_names
                st.session_state.state_names = state_names
                # st.session_state.company_names = company_names
                st.session_state.company_names = all_companies

                # Set search_clicked to True once the search button has been clicked
                st.session_state.search_clicked = True

                st.markdown('<hr style="border-top: 3px solid white">', unsafe_allow_html=True)

            if searchtype != "GenAI":
                result_counter = 1  # Initialize the counter
                for idx, (text, completion_output, score, author, state, doc_url, tariff_title, company) in enumerate(
                        processed_results):
                    badge_style = "background-color: red; color: white; border-radius: 50%; padding: 5px 10px;"
                    st.markdown(
                        f'<span style="{badge_style}">{result_counter}</span> AI Insight/Summary: {completion_output}',
                        unsafe_allow_html=True)
                    displayed_state = state if state else "Not Available"
                    displayed_author = author if state else "Not Available"
                    score_str = f"{score:.2f}" if score else "Not Applicable"
                    st.markdown(
                        f"**Author**: {displayed_author}&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;**State**: {displayed_state}&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;**Document Score:** {score_str}")
                    st.markdown(f'**Company:** {company}')
                    st.markdown(f'[**{tariff_title}**]({doc_url})', unsafe_allow_html=True)
                    st.markdown(f"**Supporting Document Excerpt:**")
                    # st.text_area(f"Document Text", text, height=100, key=f"Document_Text_{idx}")
                    st.markdown(
                        f'<div style="height:100px;overflow-y:scroll;padding:10px;border:1px solid gray;">{text}</div>',
                        unsafe_allow_html=True)
                    st.markdown('<hr style="border-top: 3px solid white">', unsafe_allow_html=True)
                    # st.markdown("\n\n---\n")
                    result_counter += 1  # Increment the counter for the next result
            else:
                for idx, (completion_output) in enumerate(
                        processed_results):
                    st.markdown(f"**AI Insight/Summary:** {completion_output}")

        else:
            st.error("Please enter a question before searching.")

##Uncomment if you want facets to be displayed
_ = '''
# Only display the authors and states sections if the Search button has been clicked
if st.session_state.search_clicked:
    with col1:
        if searchtype != "Vector OpenAI":
            st.markdown("### Authors")
            if 'author_names' in st.session_state:
                for author in st.session_state.author_names:
                    if author not in st.session_state.author_checks:
                        st.session_state.author_checks[author] = False
                    st.session_state.author_checks[author] = st.checkbox(author, value=st.session_state.author_checks[author], key=author)

        st.markdown("### Companies")
        if 'company_names' in st.session_state:
            for company in st.session_state.company_names:
                if company not in st.session_state.company_checks:
                    st.session_state.company_checks[company] = False
                st.session_state.company_checks[company] = st.checkbox(company, value=st.session_state.company_checks[company], key=f"company_{company}")

        st.markdown("### States")
        if 'state_names' in st.session_state:
            for state in st.session_state.state_names:
                if state not in st.session_state.state_checks:
                    st.session_state.state_checks[state] = False
                st.session_state.state_checks[state] = st.checkbox(state, value=st.session_state.state_checks[state], key=f"state_{state}") 
'''
