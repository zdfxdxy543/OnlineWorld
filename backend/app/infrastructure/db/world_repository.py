from __future__ import annotations

import json
import random
from itertools import count
from datetime import datetime, timezone

from app.domain.events import StoryEvent
from app.domain.models import AgentProfile, AgentSummary, WorldResource, WorldSnapshot
from app.infrastructure.db.session import DatabaseSessionManager
from app.repositories.world_repository import AbstractWorldRepository


class SQLiteWorldRepository(AbstractWorldRepository):
    def __init__(self, session_manager: DatabaseSessionManager) -> None:
        self.session_manager = session_manager
        self._resource_counter = count(1)
        self._agent_counter = count(1)
        self._legacy_agent_alias = {
            "agent-001": "aria",
            "agent-002": "milo",
            "agent-003": "eve",
        }

    def initialize(self) -> None:
        with self.session_manager.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS world_resources (
                    resource_id TEXT PRIMARY KEY,
                    resource_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    access_code TEXT NOT NULL,
                    owner_agent_id TEXT NOT NULL,
                    site_id TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    age_range TEXT NOT NULL,
                    occupation TEXT NOT NULL,
                    residence_city TEXT NOT NULL,
                    native_language TEXT NOT NULL,
                    bio TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS agent_site_accounts (
                    agent_id TEXT NOT NULL,
                    site_code TEXT NOT NULL,
                    site_user_id TEXT NOT NULL,
                    site_username TEXT NOT NULL,
                    account_status TEXT NOT NULL,
                    trust_level INTEGER NOT NULL,
                    metadata_json TEXT NOT NULL,
                    PRIMARY KEY (agent_id, site_code),
                    FOREIGN KEY(agent_id) REFERENCES agents(agent_id)
                );

                CREATE TABLE IF NOT EXISTS agent_profiles (
                    agent_id TEXT PRIMARY KEY,
                    personality_traits_json TEXT NOT NULL,
                    values_json TEXT NOT NULL,
                    hobbies_json TEXT NOT NULL,
                    work_schedule_json TEXT NOT NULL,
                    risk_preference TEXT NOT NULL,
                    trust_baseline INTEGER NOT NULL,
                    private_motives_json TEXT NOT NULL,
                    FOREIGN KEY(agent_id) REFERENCES agents(agent_id)
                );
                """
            )

            self._migrate_forum_users_to_agents(conn)
            self._seed_additional_agents(conn)

            row = conn.execute(
                "SELECT COALESCE(MAX(CAST(SUBSTR(resource_id, 7) AS INTEGER)), 0) AS max_id FROM world_resources"
            ).fetchone()
            next_id = int(row["max_id"]) + 1
            self._resource_counter = count(next_id)

            npc_row = conn.execute(
                "SELECT COALESCE(MAX(CAST(SUBSTR(agent_id, 5) AS INTEGER)), 0) AS max_id FROM agents WHERE agent_id LIKE 'npc-%'"
            ).fetchone()
            self._agent_counter = count(int(npc_row["max_id"]) + 1)
            conn.commit()

    def get_world_snapshot(self) -> WorldSnapshot:
        with self.session_manager.connect() as conn:
            thread_count = conn.execute("SELECT COUNT(1) AS count FROM threads").fetchone()["count"]
            post_count = conn.execute("SELECT COUNT(1) AS count FROM posts").fetchone()["count"]

        recent_events = [
            StoryEvent(
                name="WorldSnapshotBuilt",
                detail="世界快照已从 SQL 状态聚合。",
                metadata={"thread_count": str(thread_count), "post_count": str(post_count)},
            )
        ]
        return WorldSnapshot(
            current_tick=1,
            current_time_label="Day 1 / 08:00",
            active_sites=["forum.main", "market.square", "message.direct"],
            recent_events=recent_events,
        )

    def get_agent(self, agent_id: str) -> AgentProfile:
        resolved_id = self._legacy_agent_alias.get(agent_id, agent_id)

        with self.session_manager.connect() as conn:
            row = conn.execute(
                """
                SELECT agent_id, display_name, occupation, bio
                FROM agents
                WHERE agent_id = ?
                """,
                (resolved_id,),
            ).fetchone()

        if row is None:
            raise KeyError(f"Agent not found: {agent_id}")

        return AgentProfile(
            agent_id=row["agent_id"],
            display_name=row["display_name"],
            role=row["occupation"],
            goals=[row["bio"]],
        )

    def list_agents(self) -> list[AgentSummary]:
        with self.session_manager.connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    a.agent_id,
                    a.display_name,
                    a.status,
                    a.gender,
                    a.age_range,
                    a.occupation,
                    a.residence_city,
                    a.native_language,
                    p.personality_traits_json,
                    p.values_json,
                    p.hobbies_json
                FROM agents a
                LEFT JOIN agent_profiles p ON p.agent_id = a.agent_id
                ORDER BY a.agent_id ASC
                """
            ).fetchall()

        return [
            AgentSummary(
                agent_id=row["agent_id"],
                display_name=row["display_name"],
                status=row["status"],
                gender=row["gender"],
                age_range=row["age_range"],
                occupation=row["occupation"],
                residence_city=row["residence_city"],
                native_language=row["native_language"],
                personality_traits_json=row["personality_traits_json"] or "[]",
                values_json=row["values_json"] or "[]",
                hobbies_json=row["hobbies_json"] or "[]",
            )
            for row in rows
        ]

    def agent_exists(self, agent_id: str) -> bool:
        resolved_id = self._legacy_agent_alias.get(agent_id, agent_id)
        with self.session_manager.connect() as conn:
            row = conn.execute("SELECT 1 AS exists_flag FROM agents WHERE agent_id = ?", (resolved_id,)).fetchone()
        return row is not None

    def create_cloud_resource(self, *, owner_agent_id: str, site_id: str, title: str) -> WorldResource:
        index = next(self._resource_counter)
        resource_id = f"cloud-{index:04d}"
        access_code = f"K{index:03d}X"
        metadata = {
            "download_hint": f"https://files.local/{resource_id}",
            "visibility": "shared-with-link",
        }

        with self.session_manager.connect() as conn:
            conn.execute(
                """
                INSERT INTO world_resources (
                    resource_id,
                    resource_type,
                    title,
                    access_code,
                    owner_agent_id,
                    site_id,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    resource_id,
                    "cloud_file",
                    title,
                    access_code,
                    owner_agent_id,
                    site_id,
                    json.dumps(metadata, ensure_ascii=True),
                ),
            )
            conn.commit()

        return WorldResource(
            resource_id=resource_id,
            resource_type="cloud_file",
            title=title,
            access_code=access_code,
            owner_agent_id=owner_agent_id,
            site_id=site_id,
            metadata=metadata,
        )

    def create_random_agent(self) -> AgentSummary:
        adjectives = ["Silent", "Amber", "North", "Grey", "Neon", "Paper"]
        nouns = ["Courier", "Lantern", "Thread", "Switch", "Relay", "Watcher"]
        occupations = ["夜班保安", "网络维护员", "物流分拣员", "便利店店长", "旧货修复师", "出租车司机"]
        cities = ["Linhai", "Beicheng", "Yunzhou", "Haidong", "Nanshan"]
        age_ranges = ["18-24", "25-34", "35-44"]
        genders = ["female", "male", "non-binary"]

        agent_id = f"npc-{next(self._agent_counter):04d}"
        display_name = f"{random.choice(adjectives)}_{random.choice(nouns)}_{agent_id[-2:]}"
        status = random.choice(["Online", "Away", "Busy"])
        occupation = random.choice(occupations)
        residence_city = random.choice(cities)
        gender = random.choice(genders)
        age_range = random.choice(age_ranges)
        native_language = random.choice(["zh-CN", "en-US"])
        bio = f"{display_name} works as {occupation} in {residence_city} and often monitors rumor signals."
        now = datetime.now(timezone.utc).isoformat()

        personality_traits = random.sample(["curious", "cautious", "blunt", "empathetic", "meticulous"], k=2)
        values = random.sample(["safety", "truth", "privacy", "loyalty", "efficiency"], k=2)
        hobbies = random.sample(["night forums", "radio scanning", "street photography", "retro games"], k=2)

        with self.session_manager.connect() as conn:
            self._insert_agent_bundle(
                conn,
                agent_id=agent_id,
                display_name=display_name,
                status=status,
                gender=gender,
                age_range=age_range,
                occupation=occupation,
                residence_city=residence_city,
                native_language=native_language,
                bio=bio,
                personality_traits=personality_traits,
                values=values,
                hobbies=hobbies,
                now_iso=now,
                source="scheduler_random_spawn",
            )
            conn.commit()

        return AgentSummary(
            agent_id=agent_id,
            display_name=display_name,
            status=status,
            gender=gender,
            age_range=age_range,
            occupation=occupation,
            residence_city=residence_city,
            native_language=native_language,
            personality_traits_json=json.dumps(personality_traits, ensure_ascii=True),
            values_json=json.dumps(values, ensure_ascii=True),
            hobbies_json=json.dumps(hobbies, ensure_ascii=True),
        )

    def _migrate_forum_users_to_agents(self, conn) -> None:
        count_row = conn.execute("SELECT COUNT(1) AS count FROM agents").fetchone()
        if int(count_row["count"]) > 0:
            return

        users = conn.execute(
            """
            SELECT id, name, title, status, bio
            FROM users
            ORDER BY id ASC
            """
        ).fetchall()
        if not users:
            return

        now = datetime.now(timezone.utc).isoformat()
        for row in users:
            self._insert_agent_bundle(
                conn,
                agent_id=row["id"],
                display_name=row["name"],
                status=row["status"],
                gender="unknown",
                age_range="25-34",
                occupation=row["title"],
                residence_city="unknown",
                native_language="zh-CN",
                bio=row["bio"],
                personality_traits=["observant", "cautious"],
                values=["consistency", "credibility"],
                hobbies=["forum", "investigation"],
                now_iso=now,
                source="users_migration",
            )

    def _seed_additional_agents(self, conn) -> None:
        now = datetime.now(timezone.utc).isoformat()
        seeded_agents = [
            {
                "agent_id": "nora",
                "display_name": "Nora_Signal",
                "status": "Online",
                "gender": "female",
                "age_range": "25-34",
                "occupation": "Emergency Dispatcher",
                "residence_city": "Linhai",
                "native_language": "zh-CN",
                "bio": "Tracks late-night emergency chatter and timestamps unusual reports.",
                "personality_traits": ["calm", "methodical"],
                "values": ["duty", "accuracy"],
                "hobbies": ["ham radio", "crossword"],
            },
            {
                "agent_id": "kai",
                "display_name": "Kai_Backlane",
                "status": "Away",
                "gender": "male",
                "age_range": "18-24",
                "occupation": "Bike Courier",
                "residence_city": "Beicheng",
                "native_language": "zh-CN",
                "bio": "Knows alley shortcuts and picks up fragmented gossip across districts.",
                "personality_traits": ["bold", "street-smart"],
                "values": ["speed", "loyalty"],
                "hobbies": ["fixed-gear", "retro arcades"],
            },
            {
                "agent_id": "selene",
                "display_name": "Selene_Archive",
                "status": "Busy",
                "gender": "female",
                "age_range": "35-44",
                "occupation": "Museum Cataloger",
                "residence_city": "Yunzhou",
                "native_language": "en-US",
                "bio": "Cross-checks old catalog records with current urban legends.",
                "personality_traits": ["patient", "analytical"],
                "values": ["truth", "context"],
                "hobbies": ["film photography", "microfilm"],
            },
        ]

        for item in seeded_agents:
            self._insert_agent_bundle(
                conn,
                agent_id=item["agent_id"],
                display_name=item["display_name"],
                status=item["status"],
                gender=item["gender"],
                age_range=item["age_range"],
                occupation=item["occupation"],
                residence_city=item["residence_city"],
                native_language=item["native_language"],
                bio=item["bio"],
                personality_traits=item["personality_traits"],
                values=item["values"],
                hobbies=item["hobbies"],
                now_iso=now,
                source="starter_seed",
            )

    def _insert_agent_bundle(
        self,
        conn,
        *,
        agent_id: str,
        display_name: str,
        status: str,
        gender: str,
        age_range: str,
        occupation: str,
        residence_city: str,
        native_language: str,
        bio: str,
        personality_traits: list[str],
        values: list[str],
        hobbies: list[str],
        now_iso: str,
        source: str,
    ) -> None:
        conn.execute(
            """
            INSERT OR IGNORE INTO users (id, name, title, join_date, posts, reputation, status, signature, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                agent_id,
                display_name,
                occupation,
                now_iso[:10],
                0,
                100,
                status,
                "Signals over noise.",
                bio,
            ),
        )

        conn.execute(
            """
            INSERT OR IGNORE INTO agents (
                agent_id,
                display_name,
                status,
                gender,
                age_range,
                occupation,
                residence_city,
                native_language,
                bio,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                agent_id,
                display_name,
                status,
                gender,
                age_range,
                occupation,
                residence_city,
                native_language,
                bio,
                now_iso,
                now_iso,
            ),
        )

        conn.execute(
            """
            INSERT OR IGNORE INTO agent_site_accounts (
                agent_id,
                site_code,
                site_user_id,
                site_username,
                account_status,
                trust_level,
                metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                agent_id,
                "forum",
                agent_id,
                display_name,
                "active",
                50,
                json.dumps({"source": source}, ensure_ascii=True),
            ),
        )

        conn.execute(
            """
            INSERT OR IGNORE INTO agent_profiles (
                agent_id,
                personality_traits_json,
                values_json,
                hobbies_json,
                work_schedule_json,
                risk_preference,
                trust_baseline,
                private_motives_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                agent_id,
                json.dumps(personality_traits, ensure_ascii=True),
                json.dumps(values, ensure_ascii=True),
                json.dumps(hobbies, ensure_ascii=True),
                json.dumps({"active_hours": ["08:00-22:00"]}, ensure_ascii=True),
                "medium",
                50,
                json.dumps(["maintain_safety_margin"], ensure_ascii=True),
            ),
        )
