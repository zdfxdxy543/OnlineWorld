from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from app.schemas.paper import (
    CategoryListResponse,
    CategoryResponse,
    CreatePaperRequest,
    CreatePaperResponse,
    HotPapersResponse,
    PaperDetailResponse,
    PaperStatsResponse,
    PaperSummaryResponse,
    PapersResponse,
    SearchPapersRequest,
    SearchPapersResponse,
)

router = APIRouter(prefix="/api/v1/academic", tags=["academic"])


def _get_paper_service(request: Request):
    return request.app.state.container.paper_service


@router.get("/stats", response_model=PaperStatsResponse)
def get_stats(request: Request):
    service = _get_paper_service(request)
    stats = service.get_stats()
    return PaperStatsResponse(
        total_papers=stats.total_papers,
        total_journals=stats.total_journals,
    )


@router.get("/categories", response_model=CategoryListResponse)
def list_categories(request: Request):
    service = _get_paper_service(request)
    categories = service.list_categories()
    return CategoryListResponse(
        categories=[
            CategoryResponse(
                id=cat.id,
                name=cat.name,
                paper_count=cat.paper_count,
            )
            for cat in categories
        ]
    )


@router.get("/papers", response_model=PapersResponse)
def list_papers(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
):
    service = _get_paper_service(request)
    papers = service.list_papers(limit=limit)
    return PapersResponse(
        papers=[
            PaperSummaryResponse(
                paper_id=p.paper_id,
                title=p.title,
                authors=p.authors,
                institution=p.institution,
                journal=p.journal,
                publish_date=p.publish_date,
                keywords=p.keywords,
                downloads=p.downloads,
                pages=p.pages,
                file_size=p.file_size,
                file_name=p.file_name,
            )
            for p in papers
        ],
        total=len(papers),
    )


@router.get("/papers/hot", response_model=HotPapersResponse)
def get_hot_papers(
    request: Request,
    limit: int = Query(default=5, ge=1, le=20),
):
    service = _get_paper_service(request)
    papers = service.get_hot_papers(limit=limit)
    return HotPapersResponse(
        papers=[
            PaperSummaryResponse(
                paper_id=p.paper_id,
                title=p.title,
                authors=p.authors,
                institution=p.institution,
                journal=p.journal,
                publish_date=p.publish_date,
                keywords=p.keywords,
                downloads=p.downloads,
                pages=p.pages,
                file_size=p.file_size,
                file_name=p.file_name,
            )
            for p in papers
        ]
    )


@router.get("/papers/search", response_model=SearchPapersResponse)
def search_papers(
    request: Request,
    q: str | None = Query(default=None),
    field: str | None = Query(default=None),
    category: str | None = Query(default=None),
    year_start: int | None = Query(default=None),
    year_end: int | None = Query(default=None),
):
    service = _get_paper_service(request)
    papers = service.search_papers(
        query=q,
        field=field,
        category=category,
        year_start=year_start,
        year_end=year_end,
    )
    return SearchPapersResponse(
        papers=[
            PaperSummaryResponse(
                paper_id=p.paper_id,
                title=p.title,
                authors=p.authors,
                institution=p.institution,
                journal=p.journal,
                publish_date=p.publish_date,
                keywords=p.keywords,
                downloads=p.downloads,
                pages=p.pages,
                file_size=p.file_size,
                file_name=p.file_name,
            )
            for p in papers
        ],
        total=len(papers),
        query=q,
    )


@router.get("/paper/{paper_id}", response_model=PaperDetailResponse)
def get_paper(paper_id: str, request: Request):
    service = _get_paper_service(request)
    paper = service.get_paper(paper_id)
    if paper is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")
    return PaperDetailResponse(
        paper_id=paper.paper_id,
        title=paper.title,
        authors=paper.authors,
        institution=paper.institution,
        journal=paper.journal,
        publish_date=paper.publish_date,
        keywords=paper.keywords,
        downloads=paper.downloads,
        pages=paper.pages,
        file_size=paper.file_size,
        file_name=paper.file_name,
        abstract=paper.abstract,
    )


@router.post("/papers", response_model=CreatePaperResponse, status_code=status.HTTP_201_CREATED)
def create_paper(request: Request, paper_data: CreatePaperRequest):
    service = _get_paper_service(request)
    paper = service.create_paper(
        title=paper_data.title,
        authors=paper_data.authors,
        institution=paper_data.institution,
        journal=paper_data.journal,
        publish_date=paper_data.publish_date,
        keywords=paper_data.keywords,
        abstract=paper_data.abstract,
        pages=paper_data.pages,
        file_name=paper_data.file_name,
        file_size=paper_data.file_size,
    )
    return CreatePaperResponse(
        paper=PaperDetailResponse(
            paper_id=paper.paper_id,
            title=paper.title,
            authors=paper.authors,
            institution=paper.institution,
            journal=paper.journal,
            publish_date=paper.publish_date,
            keywords=paper.keywords,
            downloads=paper.downloads,
            pages=paper.pages,
            file_size=paper.file_size,
            file_name=paper.file_name,
            abstract=paper.abstract,
        )
    )


@router.post("/paper/{paper_id}/download")
def download_paper(paper_id: str, request: Request):
    service = _get_paper_service(request)
    paper = service.get_paper(paper_id)
    if paper is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")

    service.increment_downloads(paper_id)

    return JSONResponse(
        {
            "paper_id": paper_id,
            "file_name": paper.file_name,
            "download_url": f"/api/v1/academic/files/{paper_id}/{paper.file_name}",
        }
    )
