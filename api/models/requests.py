from pydantic import BaseModel


class ToneRequest(BaseModel): 
    tone: str 

class BlogGenerationRequest(BaseModel): 
    purpose: str
    language: str = "english"