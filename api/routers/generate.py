from fastapi import APIRouter, HTTPException
from api.models.requests import BlogGenerationRequest
from api.dependencies import blog_service

router = APIRouter()

@router.post("/generate", response_model=None)
def generate_blog_post(request: BlogGenerationRequest): 
    return blog_service.generate_blog(request.purpose, request.language)
    

