from __future__ import annotations

from typing import Any
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class SearchResult:
    """Unified search result across all content types"""
    result_id: str
    title: str
    description: str
    content_type: str  # "forum_thread", "forum_post", "product", "order", "news", "page"
    url: str
    created_at: str
    relevance_score: float = 1.0
    metadata: dict[str, Any] | None = None


class SearchService:
    """Cross-module search service for forums, products, news, pages, etc."""

    def __init__(
        self,
        forum_service: Any,
        p2pstore_service: Any,
        news_service: Any,
        mainpage_service: Any,
        netdisk_service: Any,
    ) -> None:
        self.forum_service = forum_service
        self.p2pstore_service = p2pstore_service
        self.news_service = news_service
        self.mainpage_service = mainpage_service
        self.netdisk_service = netdisk_service

    def search(self, query: str, limit: int = 50) -> list[SearchResult]:
        """
        Search across all content modules.
        Returns combined results sorted by relevance.
        """
        if not query or len(query.strip()) == 0:
            return []

        query_lower = query.lower().strip()
        results: list[SearchResult] = []

        # Search forums
        results.extend(self._search_forums(query_lower))

        # Search products
        results.extend(self._search_products(query_lower))

        # Search news
        results.extend(self._search_news(query_lower))

        # Search main pages
        results.extend(self._search_mainpages(query_lower))

        # Search netdisk
        results.extend(self._search_netdisk(query_lower))

        # Sort by relevance score (descending) and then by creation time (descending)
        results.sort(key=lambda r: (r.relevance_score, r.created_at), reverse=True)

        return results[:limit]

    def _calculate_relevance(self, query: str, text: str) -> float:
        """Calculate relevance score based on query matching"""
        if not text or not query:
            return 0.0

        text_lower = text.lower()
        query_tokens = [token for token in re.split(r"\s+", query.strip()) if token]
        if not query_tokens:
            return 0.0

        # Hard filter: if no token appears at all, this is not a match.
        if not any(token in text_lower for token in query_tokens):
            return 0.0

        if query == text_lower:
            return 1.0
        if text_lower.startswith(query):
            return 0.9
        if query in text_lower:
            return 0.8

        matched_tokens = sum(1 for token in query_tokens if token in text_lower)
        token_ratio = matched_tokens / len(query_tokens)

        if token_ratio >= 1.0:
            return 0.7
        if token_ratio >= 0.5:
            return 0.5
        return 0.3

    def _search_forums(self, query: str) -> list[SearchResult]:
        """Search forum threads and posts"""
        results = []

        try:
            # Try to get all boards
            boards = getattr(self.forum_service, "list_boards", lambda: [])()
            for board in boards:
                board_slug = getattr(board, 'slug', str(board))

                # Search threads in board
                try:
                    _, threads = self.forum_service.list_board_threads(board_slug=board_slug)

                    for thread in threads:
                        title = getattr(thread, 'title', str(thread))
                        tags = getattr(thread, 'tags', [])
                        content = " ".join(tags) if isinstance(tags, list) else str(tags)
                        thread_id = getattr(thread, 'id', '')

                        title_relevance = self._calculate_relevance(query, title)
                        content_relevance = self._calculate_relevance(query, content)
                        max_relevance = max(title_relevance, content_relevance)

                        if max_relevance > 0:
                            results.append(
                                SearchResult(
                                    result_id=f"thread-{thread_id}",
                                    title=title,
                                    description=content[:200] if content else "No description",
                                    content_type="forum_thread",
                                    url=f"/forum/thread/{thread_id}",
                                    created_at=getattr(thread, 'created_at', datetime.now().isoformat()),
                                    relevance_score=max_relevance,
                                    metadata={'board': board_slug},
                                )
                            )
                except Exception:
                    pass

        except Exception:
            pass

        return results

    def _search_products(self, query: str) -> list[SearchResult]:
        """Search p2p store products"""
        results = []

        try:
            products = self.p2pstore_service.list_products(limit=100)
            for product in products:
                name = getattr(product, 'name', str(product))
                description = getattr(product, 'description', '')
                product_id = getattr(product, 'product_id', '')
                category = getattr(product, 'category', '')
                price = getattr(product, 'price', 0)

                name_relevance = self._calculate_relevance(query, name)
                desc_relevance = self._calculate_relevance(query, description)
                cat_relevance = self._calculate_relevance(query, category)
                max_relevance = max(name_relevance, desc_relevance, cat_relevance)

                if max_relevance > 0:
                    results.append(
                        SearchResult(
                            result_id=f"product-{product_id}",
                            title=f"{name} (${price})",
                            description=description[:200] if description else "No description",
                            content_type="product",
                            url=f"/p2pstore/product/{product_id}",
                            created_at=getattr(product, 'created_at', datetime.now().isoformat()),
                            relevance_score=max_relevance,
                            metadata={'price': str(price), 'category': category},
                        )
                    )
        except Exception:
            pass

        return results

    def _search_news(self, query: str) -> list[SearchResult]:
        """Search news articles"""
        results = []

        try:
            articles = self.news_service.list_articles(limit=100)
            if isinstance(articles, dict):
                articles = articles.get('articles', [])

            for article in articles:
                title = getattr(article, 'title', str(article))
                content = getattr(article, 'content', '')
                article_id = getattr(article, 'article_id', '')
                category = getattr(article, 'category', '')

                title_relevance = self._calculate_relevance(query, title)
                content_relevance = self._calculate_relevance(query, content)
                cat_relevance = self._calculate_relevance(query, category)
                max_relevance = max(title_relevance, content_relevance, cat_relevance)

                if max_relevance > 0:
                    results.append(
                        SearchResult(
                            result_id=f"article-{article_id}",
                            title=title,
                            description=content[:200] if content else "No description",
                            content_type="news",
                            url=f"/news/article/{article_id}",
                            created_at=getattr(article, 'created_at', datetime.now().isoformat()),
                            relevance_score=max_relevance,
                            metadata={'category': category},
                        )
                    )
        except Exception:
            pass

        return results

    def _search_mainpages(self, query: str) -> list[SearchResult]:
        """Search main pages"""
        results = []

        try:
            pages = self.mainpage_service.list_pages(limit=100)
            for page in pages:
                title = getattr(page, 'title', str(page))
                content = getattr(page, 'html_content', '')
                slug = getattr(page, 'slug', '')
                page_id = getattr(page, 'page_id', '')

                title_relevance = self._calculate_relevance(query, title)
                content_relevance = self._calculate_relevance(query, content)
                max_relevance = max(title_relevance, content_relevance)

                if max_relevance > 0:
                    # Strip HTML for description
                    clean_content = re.sub(r'<[^>]+>', '', content)
                    results.append(
                        SearchResult(
                            result_id=f"page-{page_id}",
                            title=title,
                            description=clean_content[:200] if clean_content else "No description",
                            content_type="page",
                            url=f"/main/{slug}",
                            created_at=getattr(page, 'published_at', datetime.now().isoformat()),
                            relevance_score=max_relevance,
                        )
                    )
        except Exception:
            pass

        return results

    def _search_netdisk(self, query: str) -> list[SearchResult]:
        """Search netdisk files"""
        results = []

        try:
            files = getattr(self.netdisk_service, "list_files", lambda: [])()
            for file in files:
                name = getattr(file, 'file_name', str(file))
                title = getattr(file, 'title', '')
                purpose = getattr(file, 'purpose', '')
                description = f"{title} {purpose}".strip()
                resource_id = getattr(file, 'resource_id', '')

                name_relevance = self._calculate_relevance(query, name)
                desc_relevance = self._calculate_relevance(query, description)
                max_relevance = max(name_relevance, desc_relevance)

                if max_relevance > 0:
                    results.append(
                        SearchResult(
                            result_id=f"file-{resource_id}",
                            title=title or name,
                            description=description[:200] if description else "No description",
                            content_type="netdisk_file",
                            url="/netdisk",
                            created_at=getattr(file, 'created_at', datetime.now().isoformat()),
                            relevance_score=max_relevance,
                        )
                    )
        except Exception:
            pass

        return results
