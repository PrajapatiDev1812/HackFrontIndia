import os
import json
import hashlib
# pyrefly: ignore[missing-import]
from dotenv import load_dotenv
# pyrefly: ignore[missing-import]
from pydantic import BaseModel, Field
from typing import List
# pyrefly: ignore[missing-import]
from langchain_google_genai import ChatGoogleGenerativeAI
# pyrefly: ignore[missing-import]
from langchain_core.prompts import ChatPromptTemplate
# pyrefly: ignore[missing-import]
from langchain_core.output_parsers import PydanticOutputParser

load_dotenv()

class Decision(BaseModel):
    summary: str = Field(description="One-sentence summary of the decision")
    decision_type: str = Field(description="api_design, performance, security, dependency, refactoring, architecture, testing, deprecation, other")
    rationale: str = Field(description="Why was this decision made?")
    confidence: int = Field(description="0-100 confidence score")

class ExtractionResult(BaseModel):
    decisions: List[Decision]
    has_architectural_significance: bool

def extract_decisions(pr: dict) -> dict:
    cache_key = hashlib.md5(f"{pr['number']}{pr['title']}".encode()).hexdigest()
    cache_file = f"cache/llm_{cache_key}.json"
    
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    model = os.getenv("LLM_PROVIDER", "gemini")
    if model == "gemini":
        gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        llm = ChatGoogleGenerativeAI(model=gemini_model, google_api_key=os.getenv("GOOGLE_API_KEY"))
    else:
        # pyrefly: ignore[missing-import]
        from langchain_groq import ChatGroq
        groq_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        llm = ChatGroq(model=groq_model, groq_api_key=os.getenv("GROQ_API_KEY"))

    parser = PydanticOutputParser(pydantic_object=ExtractionResult)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert software architect. Extract architectural decisions from PRs. {format_instructions}"),
        ("human", "PR Title: {title}\nPR Body: {body}\nFiles: {files}")
    ])
    
    chain = prompt | llm | parser
    
    try:
        result = chain.invoke({
            "title": pr['title'],
            "body": pr['body'][:1500],
            "files": str(pr['files'][:5]),
            "format_instructions": parser.get_format_instructions()
        })
        
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(result.model_dump(), f)
        return result.model_dump()
    except Exception as e:
        print(f"[ERROR] LLM Extraction failed for PR #{pr['number']}: {e}")
        return {"decisions": [], "has_architectural_significance": False}
