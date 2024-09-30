from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import positions, teams, players

"""
Tags used for OpenAPI documentation
"""
tags_metadata = [
    {
        "name": "positions",
        "description": "NFL Player Positions",
    }
]

"""
Creates a Fast API object.
Add high level API documentation for OpenAPI
"""
app = FastAPI(
    title="NFL Statistics Collection API",
    summary="A REST API for collection of NFL statistics from ESPN",
    version="1.0.0",
    openapi_tags=tags_metadata
)

"""
Load user endpoints to the NFL stats collection backend router.
https://fastapi.tiangolo.com/tutorial/bigger-applications/
"""
app.include_router(positions.router)
app.include_router(teams.router)
app.include_router(players.router)


"""
CORS Configuration
https://fastapi.tiangolo.com/tutorial/cors/
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL (e.g., http://localhost:3000) in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)