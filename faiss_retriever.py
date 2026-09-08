import numpy as np
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer

FAQ_DOCS = {
    "Billing": "If a customer is charged twice for the same order, refund the "
               "duplicate charge within 3-5 business days. No approval needed "
               "for duplicate-charge refunds under $100.",
    "Refund": "Refunds are accepted within 30 days of delivery for damaged or "
              "incorrect items. Refunds must be approved by a senior agent if "
              "the order is outside the 30-day window.",
    "Shipping": "If tracking shows 'delivered' but the customer says they did "
                "not receive the package, file a carrier claim and offer a "
                "replacement or refund after 48 hours if the carrier does not "
                "resolve it.",
}


class FaissRetriever:
    def __init__(self, docs: dict[str, str] = None):
        self.docs = docs or FAQ_DOCS
        self.categories = list(self.docs.keys())
        self.texts = list(self.docs.values())

        self.vectorizer = TfidfVectorizer()
        vectors = self.vectorizer.fit_transform(self.texts).toarray().astype("float32")

        self.dim = vectors.shape[1]
        self.index = faiss.IndexFlatL2(self.dim)
        self.index.add(vectors)

    def retrieve(self, category: str) -> str | None:
        if category not in self.categories:
            return None
        query_vec = self.vectorizer.transform([self.docs[category]]).toarray().astype("float32")
        distances, indices = self.index.search(query_vec, k=1)
        best_idx = indices[0][0]
        return self.texts[best_idx]

    def retrieve_by_text(self, query_text: str, k: int = 1) -> list[tuple[str, str, float]]:
        query_vec = self.vectorizer.transform([query_text]).toarray().astype("float32")
        distances, indices = self.index.search(query_vec, k=k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            results.append((self.categories[idx], self.texts[idx], float(dist)))
        return results