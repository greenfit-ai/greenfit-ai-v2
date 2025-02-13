from datasets import load_dataset
import json
try:
    from .cohereUtils import ChatModel
    from .ragUtils import co
    from .searchUtils import web_search
    from .geminiUtils import evaluate_products
except ImportError:
    from cohereUtils import ChatModel
    from ragUtils import co
    from searchUtils import web_search
    from geminiUtils import evaluate_products


llm = ChatModel(cohere_client=co)

dataset = load_dataset("greenfit-ai/claude-reviewed-sport-sustainability-papers", split="train")
contents = dataset["summary"]
urls = dataset["pdf_url"]
titles = dataset["title"]
document_type = dataset["document_type"]
urlsdict = {titles[i]: urls[i] for i in range(len(urls))}
urlsdict.update({"greenfit-ai/synthetic-sport-products-sustainability": "https://huggingface.co/datasets/greenfit-ai/synthetic-sport-products-sustainability"})

articles = {"articles": [{"title": titles[i], "summary": contents[i], "document_type": document_type[i]} for i in range(len(titles))]}
first_articles = {"articles": [{"title": titles[i], "document_type": document_type[i]} for i in range(10)]}
articles_json = [art["summary"] for art in articles["articles"]]

def match_evaluations(products, evaluations):
    products_string = ""
    for i in evaluations:
        for el in products["products"]:
            if el["title"] == i[0]:
                product_str = f"# {el['title']}\n\n![product_image]({el['image']})\n\n### [{el['price']}]({el['price_url']}) (convert [to EUR](https://www.oanda.com/currency-converter/en/?from=USD&to=EUR&amount={el['price'].replace('$','')}))\n\n## Description\n\n{el['description']}\n\n{i[1]}\n\n------------------------\n\n"
                products_string += product_str 
    return products_string

def reply(message: str):
    try:
        response = llm.optimize_search(message)
        loaded_res = json.loads(response)
        print("Produced keywords")
        if loaded_res["rejected"]:
            return json.dumps({"response": "I am sorry, but our internal evaluation of your product search deemed it not suitable for this application. Please, if you want to use GreenFit AI, use it to search sport products.", "data": [0,0,0]})
        else:
            keywords = loaded_res["keywords"]
            products = web_search(keywords)
            print("Obtained products")
            products_1 = [prod["title"] for prod in products["products"]]
            products_urls = [prod["image"] for prod in products["products"]]
            res1 = llm.choose_relevant_articles(products, articles_json)
            print("Chosen relevant documents")
            article_titles = list(set([art["title"] for art in articles["articles"] if art["summary"] in res1])) 
            evaluations, data = evaluate_products(products_1, products_urls, article_titles, urlsdict)
            print("Gotten evaluation")
            final_response = match_evaluations(products, evaluations)
            print("Everything ok, returning response!")
            json_resp = json.dumps({"response": final_response, "data": data})
            return json_resp
    except Exception as e:
        print(f"An excaption occurred: {e}")
        return json.dumps({"response": "I am sorry, an error occurred while generating the response", "data": [0,0,0]})
