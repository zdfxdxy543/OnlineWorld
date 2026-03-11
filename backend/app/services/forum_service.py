from __future__ import annotations

from app.repositories.forum_repository import (
    AbstractForumRepository,
    BoardSummary,
    ForumStats,
    ThreadDetail,
    ThreadSummary,
    UserProfile,
)


class ForumService:
    def __init__(self, forum_repository: AbstractForumRepository) -> None:
        self.forum_repository = forum_repository

    def get_stats(self) -> ForumStats:
        return self.forum_repository.get_stats()

    def list_boards(self) -> list[BoardSummary]:
        return self.forum_repository.list_boards()

    def list_board_threads(self, board_slug: str) -> tuple[BoardSummary | None, list[ThreadSummary]]:
        return self.forum_repository.list_threads(board_slug)

    def get_thread(self, thread_id: str) -> ThreadDetail | None:
        return self.forum_repository.get_thread(thread_id)

    def get_user_profile(self, user_id: str) -> UserProfile | None:
        return self.forum_repository.get_user_profile(user_id)

    def get_user_recent_threads(self, user_id: str, limit: int = 5) -> list[ThreadSummary]:
        return self.forum_repository.get_recent_threads_by_author(user_id, limit)

    def get_hot_threads(self, limit: int = 5) -> list[ThreadSummary]:
        return self.forum_repository.get_hot_threads(limit)
