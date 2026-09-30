from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
import pandas as pd
from pydantic import BaseModel

from app.database.session import get_db
from app.models.database import Dataset, User
from app.core import dependencies
from app.services import ai_analyst

router = APIRouter(prefix="/ai", tags=["AI Analyst"])

class ChatRequest(BaseModel):
    dataset_id: int
    query: str

@router.post("/chat")
def chat_with_analyst(
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user)
):
    """Process natural language question about a dataset via Python analytical routing & Groq LLM."""
    current_dataset = dependencies.get_user_dataset(req.dataset_id, db, current_user)
    
    # We validate ownership inside dependency or manually
    if current_dataset.status != "mapped":
        raise HTTPException(status_code=400, detail="Dataset must be mapped first.")
        
    try:
        explanation = ai_analyst.analyze_user_query(current_dataset.file_path, req.query)
        return {
            "query": req.query,
            "response": explanation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

@router.get("/{dataset_id}/insights")
def get_automated_insights_route(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_dataset: Dataset = Depends(dependencies.get_user_dataset)
):
    """Retrieve instant automated business insight bullet points for dashboard headers."""
    if current_dataset.status != "mapped":
        raise HTTPException(status_code=400, detail="Dataset must be mapped first.")
        
    try:
        df = pd.read_csv(current_dataset.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read dataset file: {str(e)}")
        
    insights = ai_analyst.generate_automated_insights(df)
    return {"insights": insights}
