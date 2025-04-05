from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import users, posts, ads, model, expanded

app = FastAPI(
    title="Social Media Analytics API",
    description="API for social media analytics and metrics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/metrics/users", tags=["users"])
app.include_router(posts.router, prefix="/metrics/posts", tags=["posts"])
app.include_router(ads.router, prefix="/metrics/ads", tags=["ads"])
app.include_router(model.router, prefix="/metrics/model", tags=["model"])
app.include_router(expanded.router, prefix="/metrics", tags=["expanded"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}