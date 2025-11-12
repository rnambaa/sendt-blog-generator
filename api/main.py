import sys
from pathlib import Path
# add root dir TODO: figure this out later 
root = str(Path(__file__).parent.parent)
print(root)
sys.path.insert(0, root)

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