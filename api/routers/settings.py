from fastapi import APIRouter, HTTPException
from api.models.requests import ToneRequest
from api.dependencies import blog_service

router = APIRouter(prefix="/settings", tags=["settings"])

@router.post("/tone", response_model=None)
def set_tone(request: ToneRequest): 
    return blog_service.set_tone(request.tone)