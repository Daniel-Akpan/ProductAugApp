import openai
import json
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def promptResponse(json_string):
    # Parse JSON if necessary
    products = json.loads(json_string) if isinstance(json_string, str) else json_string
    
    # Process each product to add augmented data
    for product in products:
        # Fetch limited real-time augmented data
        internet_data = fetch_internet_data(product)
        
        # Enhance with OpenAI API for concise augmented data
        augmented_data = fetch_augmented_data(product, internet_data)
        
        # Add augmented data field to the product
        product['augmented_data'] = augmented_data
    # Return pretty-printed JSON for readability
    return json.dumps(products, indent=4)

def fetch_internet_data(product):
    """Scrapes a limited amount of internet data"""
    query = f"{product.get('description', '')} {product.get('product_details', '')} {product.get('taxonomy', '')}"
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    

def fetch_augmented_data(product, internet_data):
    """Fetches concise augmented data using OpenAI LLM API."""
    description = product.get("description", "")
    details = product.get("product_details", "")
    taxonomy = product.get("taxonomy", "")
    prompt = (
        f"Summarize detailed information for a product described as '{description}', "
        f"with details '{details}' under taxonomy '{taxonomy}'. Include any useful insights "
        f"from additional information: '{internet_data}'. Make it concise and informative."
    )

    # OpenAI API call
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100  
    )
    return response.choices[0].message['content'].strip()

