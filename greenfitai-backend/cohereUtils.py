import cohere

class ChatModel:
    def __init__(self, cohere_client: cohere.ClientV2):
        self.co = cohere_client
    def optimize_search(self, prompt: str):
        res = self.co.chat(
            model = "command-r-plus-08-2024",
            messages = [
                {"role": "system", "content": "You are a browser search optimization assistant for sports products: starting from the natural language prompt of the user, you should produce a JSON string containing the following field: 'keywords' (List[str]), which will be a list of the keywords to use in the search, and 'rejected' (bool), which states if the products that the user is searching are sports products or not. If the user is NOT searching sport products, please set the 'rejected' field to True, else set it to False."},
                {"role": "user", "content": prompt},
            ],
            response_format= {
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "rejected": {
                            "type": "boolean",
                        }
                    },
                    "required": ["keywords", "rejected"],
                },
            }
        )
        return res.message.content[0].text
    def choose_relevant_articles(self, products: list, articles: list):
        # model="rerank-v3.5", query=text, documents=search_result, top_n = 5
        res = self.co.rerank(
            model = "rerank-v3.5",
            query = f"I am writing a sustainability evaluation report of sports products based on their overall sustainability, carbon footprint, energy usage and water waste. The products that I am trying to evaluate are: {', '.join(products)}",
            documents=articles,
            top_n = 5
        )
        ranked_results = [articles[res.results[i].index] for i in range(5)]
        return ranked_results