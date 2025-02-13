from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer 
import torch
from fastembed import SparseTextEmbedding
import cohere

g = open("/run/secrets/qdrant_key")
con = g.read()
qdrant_api_key = con.replace("\n", "")
g.close()
g = open("/run/secrets/qdrant_db")
con = g.read()
qdrant_url = con.replace("\n", "")
g.close()
g = open("/run/secrets/cohere_key")
con = g.read()
cohere_api_key = con.replace("\n", "")
g.close()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
dense_encoder = SentenceTransformer("nomic-ai/modernbert-embed-base").to(device)
qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
sparse_encoder = SparseTextEmbedding(model_name="Qdrant/bm25")
synthetic_encoder = SentenceTransformer("Alibaba-NLP/gte-modernbert-base").to(device)
co = cohere.ClientV2(api_key=cohere_api_key, log_warning_experimental_features=False)

def get_query_sparse_embedding(text: str, model: SparseTextEmbedding):
    embeddings = list(model.embed(text))
    query_vector = models.NamedSparseVector(
        name="sparse-text",
        vector=models.SparseVector(
            indices=embeddings[0].indices,
            values=embeddings[0].values,
        ),
    )
    return query_vector

class NeuralSearcher:
    def __init__(self, text_collection_name: str, client: QdrantClient, text_encoder: SentenceTransformer , sparse_encoder: SparseTextEmbedding, synthetic_encoder: SentenceTransformer, synthetic_collection_name: str):
        self.text_collection_name = text_collection_name
        self.text_encoder = text_encoder
        self.qdrant_client = client
        self.sparse_encoder = sparse_encoder
        self.synthetic_encoder = synthetic_encoder
        self.synthetic_collection_name = synthetic_collection_name
    def search_text(self, text: str, titles_filter: list, limit: int = 10):
        vector = self.text_encoder.encode(text).tolist()

        search_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="source",
                    match=models.MatchAny(any=titles_filter)
                )
            ]
        )
        
        search_result_dense = self.qdrant_client.search(
            collection_name=self.text_collection_name,
            query_vector=models.NamedVector(name="dense-text", vector=vector),
            query_filter=search_filter,
            limit=limit,
        )

        search_result_sparse = self.qdrant_client.search(
            collection_name=self.text_collection_name,
            query_vector=get_query_sparse_embedding(text, self.sparse_encoder),
            query_filter=search_filter,
            limit=limit,
        )
        payloads = [hit.payload["text"] for hit in search_result_dense]
        sources = [hit.payload["source"] for hit in search_result_dense]
        payloads += [hit.payload["text"] for hit in search_result_sparse]
        sources += [hit.payload["source"] for hit in search_result_sparse]
        text2source = {payloads[i]: sources[i] for i in range(len(payloads))}
        return payloads, text2source
    def search_synthetic(self, text: str, limit: int = 10):
        vector = self.synthetic_encoder.encode(text).tolist()
        
        search_result_dense = self.qdrant_client.search(
            collection_name=self.synthetic_collection_name,
            query_vector=models.NamedVector(name="dense-text", vector=vector),
            query_filter=None,
            limit=limit,
        )

        search_result_sparse = self.qdrant_client.search(
            collection_name=self.synthetic_collection_name,
            query_vector=get_query_sparse_embedding(text, self.sparse_encoder),
            query_filter=None,
            limit=limit,
        )
        contexts = [hit.payload["context"] for hit in search_result_dense]
        responses = [hit.payload["response"] for hit in search_result_dense]
        contexts += [hit.payload["context"] for hit in search_result_sparse]
        responses += [hit.payload["response"] for hit in search_result_sparse]
        return contexts, responses
    def reranking(self, text: str, search_result: list):
        results = co.rerank(model="rerank-v3.5", query=text, documents=search_result, top_n = 5)
        ranked_results = [search_result[results.results[i].index] for i in range(5)]
        return ranked_results
    def reranking_synthetic(self, text: str, contexts: str, responses: str):
        results_contexts = co.rerank(model="rerank-v3.5", query=text, documents=contexts, top_n = 5)
        ranked_contexts = [contexts[results_contexts.results[i].index] for i in range(5)]
        results_responses = co.rerank(model="rerank-v3.5", query=text, documents=responses, top_n = 5)
        ranked_responses = [responses[results_responses.results[i].index] for i in range(5)]
        documents = ranked_contexts+ranked_responses
        final_reranked = co.rerank(model="rerank-v3.5", query=text, documents=documents, top_n = 5)
        final_results = [documents[final_reranked.results[i].index] for i in range(5)]
        return final_results

