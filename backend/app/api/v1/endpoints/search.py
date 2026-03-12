from __future__ import annotations

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, Field

router = APIRouter()


class SearchResultItem(BaseModel):
    result_id: str = Field(..., description="Unique result identifier")
    title: str = Field(..., description="Result title")
    description: str = Field(..., description="Result description/preview")
    content_type: str = Field(..., description="Type of content (forum_thread, product, news, page, etc)")
    url: str = Field(..., description="URL to view the full content")
    created_at: str = Field(..., description="Creation timestamp")
    relevance_score: float = Field(..., description="Relevance score 0-1")
    metadata: dict | None = Field(None, description="Additional metadata")


class SearchResponse(BaseModel):
    query: str = Field(..., description="The search query")
    total_results: int = Field(..., description="Total number of results found")
    results: list[SearchResultItem] = Field(..., description="Search results")


@router.get("/search", response_model=SearchResponse)
async def search(
    request: Request,
    q: str = Query(..., description="Search query", min_length=1),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
) -> SearchResponse:
    """
    Search across all content modules (forums, products, news, pages, files).
    Returns unified results ranked by relevance.
    """
    search_service = request.app.state.container.search_service
    results = search_service.search(query=q, limit=limit)

    return SearchResponse(
        query=q,
        total_results=len(results),
        results=[
            SearchResultItem(
                result_id=r.result_id,
                title=r.title,
                description=r.description,
                content_type=r.content_type,
                url=r.url,
                created_at=r.created_at,
                relevance_score=r.relevance_score,
                metadata=r.metadata,
            )
            for r in results
        ],
    )
