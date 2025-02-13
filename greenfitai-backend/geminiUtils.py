from urllib.request import urlopen
from PIL import Image
from statistics import mean
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from get_code_from_markdown import get_code_from_markdown
from typing import List, Dict
import json
from json import JSONDecodeError
from ragUtils import NeuralSearcher, qdrant_client, sparse_encoder, dense_encoder, synthetic_encoder

f = open("/run/secrets/gemini_key")
con = f.read()
gemini_api_key = con.replace("\n", "")
f.close()

def grade_to_markdown_color(grade: int):
    if grade < 3:
        evaluation = "bad"
    elif 3 <= grade < 7:
        evaluation = "medium"
    else:
        evaluation = "good"
    colors = {"bad": "ff0000", "medium": "ffcc00", "good": "33cc33"}
    mdcode = f"![#{colors[evaluation]}](https://placehold.co/15x15/{colors[evaluation]}/{colors[evaluation]}.png)"
    return mdcode

searcher = NeuralSearcher("sustainability_articles", qdrant_client, dense_encoder, sparse_encoder, synthetic_encoder, "synthetic_data")
genai.configure(api_key=gemini_api_key)

# Create the model
generation_config = {
  "temperature": 0,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_schema": content.Schema(
    type = content.Type.OBJECT,
    properties = {
      "materials": content.Schema(
        type = content.Type.ARRAY,
        items = content.Schema(
          type = content.Type.STRING,
        ),
      ),
      "product": content.Schema(
        type = content.Type.STRING,
      ),
    },
  ),
  "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config,
)

generation_config1 = {
  "temperature": 0,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model1 = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config1,
)

generation_config2 = {
  "temperature": 0,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_schema": content.Schema(
    type = content.Type.OBJECT,
    properties = {
      "vector_search_question": content.Schema(
        type = content.Type.STRING,
      ),
    },
  ),
  "response_mime_type": "application/json",
}

model2 = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config2,
)


def evaluate_products(products_list: List[str], products_urls: List[str], articles_titles: List[str], urlsdict: Dict[str, str]) -> List[str]:
    chat_session = model.start_chat(history=[])
    evaluations = {}
    carbongrades = []
    watergrades = []
    energygrades = []
    titles = '\n- '.join(articles_titles)
    for i in range(len(products_urls)):
        products_mat = []
        img = Image.open(urlopen(products_urls[i]))
        product_name = products_list[i]
        response = chat_session.send_message([f"Based on the provided image of {product_name}, can you recognize the the materials which make up the product displayed in the image?", img])
        response_body = response.text
        products_mat.append({"role": "user", "parts": [f"Based on the provided image of {product_name}, can you recognize the the materials which make up the product displayed in the image?"]})
        products_mat.append({"role": "model", "parts": [response_body]})
        chat_session2 = model2.start_chat(history=products_mat)
        response2 = chat_session2.send_message(f"Based on the product you just recognized and whose materials you identified, can you generate a question that will be used to search within a vector database and retrieve relevant information from these articles: {titles}?")
        response2_body = response2.text
        json_response2 = json.loads(response2_body)["vector_search_question"]
        hits, hit2sources = searcher.search_text(json_response2, articles_titles)
        reranked_hits = searcher.reranking(json_response2, hits)
        contexts, responses = searcher.search_synthetic(json_response2)
        reranked_hits_synth = searcher.reranking_synthetic(json_response2, contexts, responses)
        reranked_hits_json = {"documents": [{"id": i, "content": reranked_hits[i], "title": hit2sources[reranked_hits[i]]} for i in range(len(reranked_hits))]}
        d = 0
        for synth_hit in reranked_hits_synth:
            reranked_hits_json["documents"].append({"id": len(reranked_hits)+d, "content": synth_hit, "title": "greenfit-ai/synthetic-sport-products-sustainability"})
            d+=1
        chat_session1 = model1.start_chat(history=products_mat)
        response1 = chat_session1.send_message(f"This is your contextual information that you should use to evaluate the sustainability of the product you just described:\n\n{reranked_hits_json}\n\nCan you please reason about it, producing a summary and adding relevant information coming from your knowledge? You should especially focus on understanding more about carbon emissions, water consumption and energy usage that are associated with the product's life cycle (production, usage and disposal).")
        response1a = chat_session1.send_message("""Based on the contextual information you've been provided with, on your reasoning about that contextual information and on the product itself, can you now produce an actual sustainability evaluation for the product? The evaluation should follow this JSON format: {"carbon_emissions": {"grade": "", "positive": "", "negative": ""}, "water_consumption": {"grade": "", "positive": "", "negative": ""}, "energy_usage": {"grade": "", "positive": "", "negative": ""}, "overall_summary": "", "sources": ["",""...]}. Grades should be given out of 10, whereas positive and negative denote the positive points and the negative points related to the reason why you gave that specific grade to the product. For the sources, please use the titles of the documents, and not the chunks of text themselves. Please, produce only JSON code.""")
        response1a_body = response1a.text
        try: 
            json_response1a = json.loads(response1a_body)
        except JSONDecodeError:
            json_code1a = get_code_from_markdown(response1a_body, language="json")
            json_response1a = json.loads(json_code1a[0])
        tcgrade = type(json_response1a["carbon_emissions"]["grade"])
        twgrade = type(json_response1a["water_consumption"]["positive"])
        tegrade = type(json_response1a["energy_usage"]["grade"])
        if tcgrade == str:
            if "/10" in json_response1a["carbon_emissions"]["grade"]:
                carbon_grade = int(json_response1a["carbon_emissions"]["grade"].replace("/10",""))
            else:
                carbon_grade = int(json_response1a["carbon_emissions"]["grade"])
        if twgrade == str:
            if "/10" in json_response1a["water_consumption"]["grade"]:
                water_grade = int(json_response1a["water_consumption"]["grade"].replace("/10",""))
            else:
                water_grade = int(json_response1a["water_consumption"]["grade"])
        if tegrade == str:
            if "/10" in json_response1a["energy_usage"]["grade"]:
                energy_grade = int(json_response1a["energy_usage"]["grade"].replace("/10",""))
            else:
                energy_grade = int(json_response1a["energy_usage"]["grade"])
        carbongrades.append(carbon_grade)
        carbon_positive = json_response1a["carbon_emissions"]["positive"]
        carbon_negative = json_response1a["carbon_emissions"]["negative"]
        watergrades.append(water_grade)
        water_positive = json_response1a["water_consumption"]["positive"]
        water_negative = json_response1a["water_consumption"]["negative"]
        energygrades.append(energy_grade)
        energy_positive = json_response1a["energy_usage"]["positive"]
        energy_negative = json_response1a["energy_usage"]["negative"]
        overall_summary = json_response1a["overall_summary"]
        sources = json_response1a["sources"]
        
        evaluation = f"## Sustainability Evaluation\n\n"
        evaluation += f"### {grade_to_markdown_color(carbon_grade)} Carbon emissions: {carbon_grade}/10\n\n**Positive aspects**:\n{carbon_positive}\n\n**Negative aspects**:\n{carbon_negative}\n\n"
        evaluation += f"### {grade_to_markdown_color(water_grade)} Water consumption: {water_grade}/10\n\n**Positive aspects**:\n{water_positive}\n\n**Negative aspects**:\n{water_negative}\n\n"
        evaluation += f"### {grade_to_markdown_color(energy_grade)} Energy usage: {energy_grade}/10\n\n**Positive aspects**:\n{energy_positive}\n\n**Negative aspects**:\n{energy_negative}\n\n"
        evaluation += f"### Overall Summary\n\n{overall_summary}\n\n"
        setsources = list(set(sources))
        sources_w_url = [f"[{source}]({urlsdict[source]})" for source in setsources if source in list(urlsdict.keys())]
        evaluation += f"### Sources\n\n- " + "\n- ".join(sources_w_url)
        evaluations.update({len(energygrades)-1: [evaluation, sum([carbongrades[len(energygrades) -1], energygrades[len(energygrades)-1], watergrades[len(energygrades)-1]]), products_list[i]]})
    ordered_dict = dict(sorted(evaluations.items(), key=lambda x: x[1][1], reverse=True))
    evs = [(ordered_dict[k][2], ordered_dict[k][0]) for k in ordered_dict]
    return evs, [mean(carbongrades), mean(watergrades), mean(energygrades)]


        
    
