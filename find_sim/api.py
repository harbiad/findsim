import frappe
from frappe import _
from frappe.utils import now
from werkzeug import Response
from urllib.parse import urlparse

import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import torch
import re

@frappe.whitelist(allow_guest=True)
def search_description_old(query=None):
    """
    Return records from MyRecord Doctype matching the search query.
    """
    if not query:
        return ['empty query']

    # Example: Searching in name or description fields
    records = frappe.db.get_list(
        'Description',
        filters={
            # You can use partial matches with 'like' if desired
            'description': ['like', f'%{query}%']
        },
        fields=['name','description','sap_number'],
        limit=20
    )
    return records

@frappe.whitelist(allow_guest=True)
def search_description(query=None):
    """
    Return records from Description Doctype matching any of the substrings
    in the search query (split by spaces).
    """
    if not query:
        return ["empty query"]

    # Split query into separate tokens
    subqueries = query.split()

    # Build an OR filter for each token: ['description', 'like', '%token%']
    or_filters = []
    for token in subqueries:
        or_filters.append(["description", "like", f"%{token}%"])

    # Query the doctype with OR logic
    records = frappe.db.get_list(
        "Description",
        or_filters=or_filters,                 # Use OR filters
        fields=["name", "description", "sap_number"],
        limit=20
    )

    # Depending on how Frappe returns results, you might still need to remove duplicates
    # if a record matches more than one token. The code below ensures uniqueness by 'name'.
    
    # unique_records_map = {}
    # for rec in records:
    #     unique_records_map[rec["name"]] = rec

    # unique_records = list(unique_records_map.values())
    
    # for i, rec in enumerate(records):
    #     #records[i].description = f"<p>{rec.description}</p>"
    #     records[i].description = f"<p>{rec.description}</p>"

    return records


@frappe.whitelist(allow_guest=True)
def similar_description_old(query=None):
    
    if not query:
        return ["Please provide 'query'."]
    
    # Clean text function
    def clean_text(text):
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        text = re.sub(r'\s+', ' ', text)     # Normalize spaces
        text = text.strip()                  # Remove leading/trailing spaces
        return text
    
    # Check if GPU is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Initialize the model
    # model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"  # Use a SentenceTransformer model
    #model_name = "distiluse-base-multilingual-cased-v2"  # Use a SentenceTransformer model distiluse-base-multilingual-cased-v2
    model_path = '../apps/find_sim/paraphrase-multilingual-MiniLM-L12-v2'
    
    # Load the model from the local folder (no internet download required)
    model = SentenceTransformer('../apps/find_sim/paraphrase-multilingual-MiniLM-L12-v2')
    print(f"Model loaded from {model_path}")
    # model = SentenceTransformer(model_name, device=device)
    
    # Load your data (replace 'descriptions.csv' with your file)
    #df = pd.read_csv("Material Description-subset.csv")  # Assuming a column named 'description'
    df = pd.read_csv(        #'descriptions-original.csv', 
     '../apps/find_sim/MARA-check-duplicates.xls',

    sep=';',  # Use ; as a delimiter
    names=['Description','Original Row Nr', 'Old Material Nr', 'SAP Material Nr'],  
    skiprows = 1
    )
    
    df['processed'] = df['Description'].apply(clean_text)
    
     # 4. Create embeddings for all rows in the XLS
    embeddings = model.encode(
        df['processed'].tolist(), 
        normalize_embeddings=True, 
        show_progress_bar=False
    )
    print(f"Embeddings created for {len(df)} rows")
    # 5. Process and embed the `param`
    param_processed = clean_text(query)
    param_embedding = model.encode(
        [param_processed], 
        normalize_embeddings=True, 
        show_progress_bar=False
    )

    # 6. Compute similarity between param_embedding and each row’s embedding
    # shape of `similarities`: (1, number_of_rows)
    similarities = cosine_similarity(param_embedding, embeddings)[0]

    # 7. Attach similarity scores to the DataFrame
    df["similarity_score"] = similarities

    # (Optional) Sort by similarity descending
    df = df.sort_values(by="similarity_score", ascending=False)
     
    top_10 = df.head(10)
    
    
    

    # 1. Reset the index, adding it as a new column named "index"
    top_10.reset_index(inplace=True)
    # The new column will be named "index" by default
    
    # 2. Make "index" the first column in the DataFrame
    cols = ["index"] + [c for c in top_10.columns if c != "index"]
    top_10 = top_10[cols]
    
        # Convert to a list of dictionaries
    result_records = top_10.to_dict("records") 
    
    return result_records
    
#import os
import numpy as np
#import pandas as pd
#from sentence_transformers import SentenceTransformer
#from sklearn.metrics.pairwise import cosine_similarity

def clean_text(text):
    if not text:
        return ""
    # Example cleaning
    return " ".join(text.split()).lower()

def generate_and_store_embeddings(csv_path, embeddings_file):
    """
    Reads from your CSV or XLS file, cleans text, encodes with SentenceTransformer,
    and saves the resulting embeddings in embeddings_file (.npy).
    """

    df = pd.read_csv(
        csv_path,
        sep=';',  
        names=['Description','Original Row Nr', 'Old Material Nr', 'SAP Material Nr'], 
        skiprows=1
    )

    # Preprocess text
    df['processed'] = df['Description'].apply(clean_text)

    # Load the model (local path or huggingface name)
    model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

    # Encode all rows
    embeddings = model.encode(
        df['processed'].tolist(),
        normalize_embeddings=True,
        show_progress_bar=False
    )

    # Save embeddings to a .npy file
    np.save(embeddings_file, embeddings)

    # Optionally return df in case you want to store indices, etc.
    return df
@frappe.whitelist(allow_guest=True)
def mara_embeddings():
    """
    Generate and store embeddings for the MARA-check-duplicates.xls file.
    """
    df = generate_and_store_embeddings(
        csv_path="../apps/find_sim/MARA-check-duplicates.xls",
        embeddings_file="../apps/find_sim/my_embeddings.npy"
    )
    print(f"Embeddings saved to my_embeddings.npy")
    return df

@frappe.whitelist(allow_guest=True)
def compute_similarities_with_query(query, embeddings_file, csv_path):
        
    """
    Loads precomputed embeddings from .npy,
    encodes the user query, and computes similarity scores.
    Returns the similarity array.
    """
    # Load the DataFrame to keep track of row info, if needed
    df = pd.read_csv(
        csv_path,
        sep=';',  
        names=['Description','Original Row Nr', 'Old Material Nr', 'SAP Material Nr'], 
        skiprows=1
     )
    # Load embeddings from file
    embeddings = np.load(embeddings_file)

    # Load the same model
    model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

    # Clean and embed the user query
    param_processed = clean_text(query)
    param_embedding = model.encode(
        [param_processed],
        normalize_embeddings=True,
        show_progress_bar=False
    )

    # Compute cosine similarity
    # shape = (1, number_of_rows)
    similarities = cosine_similarity(param_embedding, embeddings)[0]

    # Combine the similarity scores into df for convenience
    df["similarity_score"] = similarities

    # Sort descending by similarity
    df.sort_values(by="similarity_score", ascending=False, inplace=True)

    # Return the sorted DataFrame (or just the similarity array)
    return df
@frappe.whitelist(allow_guest=True)
def similar_description(query=None):
    
    if not query:
        return ["Please provide 'query'."]
    
        
    result_df = compute_similarities_with_query(query, 
            embeddings_file="../apps/find_sim/my_embeddings.npy", 
            csv_path="../apps/find_sim/MARA-check-duplicates.xls",
            )
 
    top_10 = result_df.head(10)
    

    # 1. Reset the index, adding it as a new column named "index"
    top_10.reset_index(inplace=True)
    # The new column will be named "index" by default
    
    # 2. Make "index" the first column in the DataFrame
    cols = ["index"] + [c for c in top_10.columns if c != "index"]
    top_10 = top_10[cols]
    
    # Convert to a list of dictionaries
    result_records = top_10.to_dict("records") 
    # Now you have a DataFrame with "similarity_score" column
    #print(result_df.head(10))
    return result_records

