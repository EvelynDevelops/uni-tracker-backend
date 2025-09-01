from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.universities.route import router as universities_router

app = FastAPI(
    title="Uni Tracker Backend",
    description="Unified Tracker Backend API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(universities_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Uni Tracker Backend API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 