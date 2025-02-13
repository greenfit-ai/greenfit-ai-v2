import requests
import os

g = open("/run/secrets/rapid_key")
con = g.read()
rapid_api_key = con.replace("\n","")

def web_search(keywords: str, limit: int = 10):
    query = " ".join(keywords)
    url = "https://real-time-product-search.p.rapidapi.com/search-v2"
    querystring = {"q": query,"country":"us","language":"en","page":"1","limit":limit,"sort_by":"BEST_MATCH","product_condition":"ANY"}
    headers = {
        "x-rapidapi-key": rapid_api_key,
        "x-rapidapi-host": "real-time-product-search.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    resdict = response.json()
    data = resdict["data"]["products"]
    # product_title, product_description, product_photos[0], product_page_url 
    products_dict = {"products": [{"title": d["product_title"], "description": d["product_description"], "image": d["product_photos"][0], "page_url": d["product_page_url"], "price": d["offer"]["price"], "price_url": d["offer"]["offer_page_url"]} for d in data]}
    return products_dict