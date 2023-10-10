import pandas as pd
from utils.openai_embedder import get_embedding


def prepare_data(file_path: str, platform_choice: str):
    df = pd.read_csv(file_path)

    # Mapping the platform_choice string to its corresponding platform value
    platform_mapping = {
        "xbox": "XBOX",
        "ps": "PS",
        "nintendo": "NINTENDO"
    }

    # Update platform column based on user's choice
    df['platform'] = platform_mapping.get(platform_choice, "UNKNOWN")

    df['name'] = df['name'].str.replace(r'[^a-zA-Z0-9\s]', '', regex=True).str.replace(r'\s+', ' ',
                                                                                       regex=True).str.strip()

    # Rename 'name' column to 'game_title'
    df = df.rename(columns={'name': 'game_title'})

    # Select required columns
    df = df[['game_title', 'platform']]

    df.fillna("UNKNOWN", inplace=True)

    # Create a new column 'openai_vector' and set its value based on the embedding of the 'name' column
    #df['openai_vector'] = df['game_title'].apply(get_embedding)

    records = df.to_dict(orient='records')
    print("number of records")
    print(len(records))

    return records
