from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.container import build_container
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.container = build_container(settings)
    app.include_router(api_router, prefix=settings.api_prefix)

    @app.get("/")
    def read_root() -> dict[str, str]:
        return {
            "name": settings.app_name,
            "docs": "/docs",
            "health": f"{settings.api_prefix}/health",
            "search": "/search",
        }

    @app.get("/search", response_class=HTMLResponse)
    def read_search_page() -> HTMLResponse:
        """Serve the 2000s-style search engine frontend"""
        search_html_path = Path(__file__).resolve().parent.parent.parent / "frontend" / "search.html"
        if search_html_path.exists():
            with open(search_html_path, 'r', encoding='utf-8') as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(
            status_code=404,
            content="<h1>404</h1><p>Search page not found.</p>"
        )

    @app.get("/main/{slug}", response_class=HTMLResponse)
    def read_generated_main_page(slug: str) -> HTMLResponse:
        page = app.state.container.mainpage_service.get_page_by_slug(slug=slug)
        if page is None:
            return HTMLResponse(status_code=404, content="<h1>404</h1><p>Page not found.</p>")
        return HTMLResponse(content=page.html_content)

    return app


app = create_app()
