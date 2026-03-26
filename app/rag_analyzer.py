import os
import numpy as np
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
import requests
import faiss
from newspaper import Article

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")


class RAGAnalyzer:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.news_store = []  # {"title", "url", "content"}
        self.index = None
        self.embeddings = []

    def _embed(self, texts: list) -> np.ndarray:
        # 간단한 TF 기반 임베딩 (faiss용)
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(max_features=256)
        vecs = vectorizer.fit_transform(texts).toarray().astype("float32")
        # L2 정규화
        norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9
        return vecs / norms

    def _fetch_article(self, url: str) -> str:
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article.text[:500] if article.text else ""
        except Exception:
            return ""

    def ingest(self, news: list):
        self.news_store = []
        for n in news[:5]:
            content = self._fetch_article(n.get("url", ""))
            self.news_store.append({
                "title": n["title"],
                "url": n.get("url", ""),
                "content": content if content else n["title"],
            })

        if not self.news_store:
            return

        texts = [f"{n['title']} {n['content']}" for n in self.news_store]
        vecs = self._embed(texts)
        self.embeddings = vecs

        # FAISS 인덱스 생성
        dim = vecs.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # Inner Product (코사인 유사도)
        self.index.add(vecs)

    def search(self, query: str, k: int = 3) -> list:
        if self.index is None or len(self.news_store) == 0:
            return self.news_store

        texts = [f"{n['title']} {n['content']}" for n in self.news_store]
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(max_features=256)
        all_texts = texts + [query]
        vecs = vectorizer.fit_transform(all_texts).toarray().astype("float32")
        norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9
        vecs = vecs / norms

        doc_vecs = vecs[:-1]
        query_vec = vecs[-1:].astype("float32")

        index = faiss.IndexFlatIP(doc_vecs.shape[1])
        index.add(doc_vecs)
        _, indices = index.search(query_vec, min(k, len(self.news_store)))

        return [self.news_store[i] for i in indices[0] if i < len(self.news_store)]

    def analyze(self, ticker: str, signals: dict,
                fundamentals: dict, news: list) -> str:

        # 뉴스 수집 및 인덱싱
        self.ingest(news)

        # 관련 뉴스 검색
        query = f"{ticker} stock price prediction market analysis"
        relevant = self.search(query, k=3)

        # Citation 형식으로 뉴스 컨텍스트 구성
        news_context = ""
        for i, n in enumerate(relevant, 1):
            news_context += f"[{i}] {n['title']}\n"
            if n["content"] and n["content"] != n["title"]:
                news_context += f"    {n['content'][:200]}...\n"
            news_context += f"    Source: {n['url']}\n\n"

        prompt = f"""You are a professional quantitative analyst.
Analyze the following stock data and provide investment insights WITH citations.

Ticker: {ticker}

Technical Signals:
- RSI: {signals.get('rsi')}
- MACD Histogram: {signals.get('macd_hist')}
- Bollinger Band %: {signals.get('bb_pct')}
- Composite Signal: {signals.get('composite')}
- ML Prediction: {signals.get('signal')} (prob_up: {signals.get('prob_up')})
- Model Accuracy: {signals.get('accuracy')} | Walk-Forward AUC: {signals.get('walkforward_auc')}
- Top Predictive Features: {signals.get('top_features')}

Fundamentals:
- 52W High: {fundamentals.get('52w_high')}
- 52W Low: {fundamentals.get('52w_low')}
- Market Cap: {fundamentals.get('market_cap')}

Relevant News (use [1], [2], [3] citations):
{news_context}

Please provide:
1. Current market situation summary (cite news with [1][2][3])
2. Key risk factors (2-3 bullet points with citations)
3. ML model insight (what top features are driving the prediction)
4. Short-term outlook (1-2 sentences)
5. Overall assessment: Bullish / Neutral / Bearish

Important: Use [1], [2], [3] citations when referencing news."""

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
        )

        result = response.choices[0].message.content

        # Citation 링크 추가
        citations = "\n\n**Sources:**\n"
        for i, n in enumerate(relevant, 1):
            citations += f"[{i}] [{n['title']}]({n['url']})\n"

        return result + citations