from __future__ import annotations

from app.repositories.forum_repository import (
    AbstractForumRepository,
    BoardSummary,
    ForumStats,
    ThreadDetail,
    ThreadPost,
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

    def user_exists(self, user_id: str) -> bool:
        return self.forum_repository.user_exists(user_id)

    def list_user_ids(self) -> list[str]:
        return self.forum_repository.list_user_ids()

    def get_user_recent_threads(self, user_id: str, limit: int = 5) -> list[ThreadSummary]:
        return self.forum_repository.get_recent_threads_by_author(user_id, limit)

    def get_hot_threads(self, limit: int = 5) -> list[ThreadSummary]:
        return self.forum_repository.get_hot_threads(limit)

    def create_thread(
        self,
        *,
        board_slug: str,
        author_id: str,
        title: str,
        content: str,
        tags: list[str],
    ) -> ThreadDetail:
        return self.forum_repository.create_thread(
            board_slug=board_slug,
            author_id=author_id,
            title=title,
            content=content,
            tags=tags,
        )

    def reply_thread(self, *, thread_id: str, author_id: str, content: str) -> ThreadPost | None:
        return self.forum_repository.reply_thread(thread_id=thread_id, author_id=author_id, content=content)
