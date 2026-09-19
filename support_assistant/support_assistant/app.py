import os
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Zepto GenAI Support Assistant")

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: float

MOCK_LLM = os.getenv("MOCK_LLM", "1") == "1"

@app.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    q = request.question.lower()
    
    if "return" in q or "policy" in q or "refund" in q:
        return QueryResponse(
            answer="Zepto's policy allows returns for damaged items within 2 hours of delivery.",
            sources=["doc_return_policy.txt"],
            confidence=0.95
        )
    
    return QueryResponse(
        answer="I am an automated assistant. For standard queries, please check the app help section.",
        sources=["general_faq.txt"],
        confidence=0.80
    )