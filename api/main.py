import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pathlib import Path
import sys 
from fastapi import FastAPI
from api.routers import generate, settings 

app = FastAPI()

# include routers
app.include_router(settings.router)
app.include_router(generate.router)

@app.get("/health")
def health_check(): 
    return {"status": "ok"}