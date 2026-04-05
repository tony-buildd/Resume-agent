from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any

from app.config import Settings, get_settings
from app.vault.contracts import VaultRoleRecord


@dataclass(frozen=True)
class VaultIndexDocument:
    id: str
    document: str
    metadata: dict[str, str | bool]


@dataclass(frozen=True)
class VaultSemanticMatch:
    id: str
    document: str
    metadata: dict[str, Any]
    distance: float | None = None


class VaultIndexer:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    @property
    def enabled(self) -> bool:
        return self.settings.chroma_enabled

    @cached_property
    def _client(self):
        import chromadb

        Path(self.settings.chroma_path).mkdir(parents=True, exist_ok=True)
        return chromadb.PersistentClient(path=self.settings.chroma_path)

    @cached_property
    def _collection(self):
        return self._client.get_or_create_collection(
            name=self.settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_role(self, *, user_id: str, role: VaultRoleRecord) -> int:
        if not self.enabled:
            return 0

        documents = build_role_index_documents(user_id=user_id, role=role)
        if not documents:
            return 0

        self._collection.upsert(
            ids=[item.id for item in documents],
            documents=[item.document for item in documents],
            metadatas=[item.metadata for item in documents],
        )
        return len(documents)

    def query(
        self,
        *,
        user_id: str,
        query_text: str,
        limit: int | None = None,
    ) -> list[VaultSemanticMatch]:
        if not self.enabled or not query_text.strip():
            return []

        result = self._collection.query(
            query_texts=[query_text],
            n_results=limit or self.settings.chroma_query_limit,
            where={"user_id": user_id},
        )

        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        matches: list[VaultSemanticMatch] = []
        for index, item_id in enumerate(ids):
            matches.append(
                VaultSemanticMatch(
                    id=item_id,
                    document=documents[index],
                    metadata=metadatas[index] or {},
                    distance=distances[index] if index < len(distances) else None,
                )
            )
        return matches


def build_role_index_documents(*, user_id: str, role: VaultRoleRecord) -> list[VaultIndexDocument]:
    documents: list[VaultIndexDocument] = []
    role_context = f"{role.company.name} {role.title}".strip()

    if role.summary:
        documents.append(
            VaultIndexDocument(
                id=f"role-summary:{role.id}",
                document=f"{role_context}\n{role.summary}",
                metadata={
                    "user_id": user_id,
                    "role_id": role.id,
                    "record_type": "role_summary",
                    "company_name": role.company.name,
                    "role_title": role.title,
                    "review_state": "approved",
                    "draft_eligible": "true",
                },
            )
        )

    for fact in role.role_facts:
        documents.append(
            VaultIndexDocument(
                id=f"fact:{fact.id}",
                document=build_fact_document(role_context=role_context, statement=fact.statement, evidence=fact.evidence),
                metadata={
                    "user_id": user_id,
                    "role_id": role.id,
                    "record_type": "fact",
                    "company_name": role.company.name,
                    "role_title": role.title,
                        "review_state": fact.review_state,
                        "draft_eligible": str(fact.draft_eligible).lower(),
                        "source_type": fact.source_type,
                    },
                )
            )

    for bullet in role.role_bullet_candidates:
        documents.append(
            VaultIndexDocument(
                id=f"bullet:{bullet.id}",
                document=build_bullet_document(
                    role_context=role_context,
                    text=bullet.text,
                    story_angle=bullet.story_angle,
                ),
                metadata={
                    "user_id": user_id,
                    "role_id": role.id,
                    "record_type": "bullet",
                    "company_name": role.company.name,
                    "role_title": role.title,
                    "review_state": bullet.review_state,
                    "draft_eligible": str(bullet.draft_eligible).lower(),
                    "source_type": bullet.source_type,
                },
            )
        )

    for story in role.project_stories:
        story_context = f"{role_context} {story.name}".strip()
        story_body = "\n".join(
            part
            for part in [story.summary, story.stack_summary, story.impact_summary]
            if part
        )
        if story_body:
            documents.append(
                VaultIndexDocument(
                    id=f"story:{story.id}",
                    document=f"{story_context}\n{story_body}",
                    metadata={
                        "user_id": user_id,
                        "role_id": role.id,
                        "project_story_id": story.id,
                        "record_type": "story",
                        "company_name": role.company.name,
                        "role_title": role.title,
                        "story_name": story.name,
                        "review_state": story.review_state,
                        "draft_eligible": str(story.draft_eligible).lower(),
                        "source_type": story.source_type,
                    },
                )
            )

        for fact in story.facts:
            documents.append(
                VaultIndexDocument(
                    id=f"fact:{fact.id}",
                    document=build_fact_document(
                        role_context=story_context,
                        statement=fact.statement,
                        evidence=fact.evidence,
                    ),
                    metadata={
                        "user_id": user_id,
                        "role_id": role.id,
                        "project_story_id": story.id,
                        "record_type": "fact",
                        "company_name": role.company.name,
                        "role_title": role.title,
                        "story_name": story.name,
                        "review_state": fact.review_state,
                        "draft_eligible": str(fact.draft_eligible).lower(),
                        "source_type": fact.source_type,
                    },
                )
            )

        for bullet in story.bullet_candidates:
            documents.append(
                VaultIndexDocument(
                    id=f"bullet:{bullet.id}",
                    document=build_bullet_document(
                        role_context=story_context,
                        text=bullet.text,
                        story_angle=bullet.story_angle,
                    ),
                    metadata={
                        "user_id": user_id,
                        "role_id": role.id,
                        "project_story_id": story.id,
                        "record_type": "bullet",
                        "company_name": role.company.name,
                        "role_title": role.title,
                        "story_name": story.name,
                        "review_state": bullet.review_state,
                        "draft_eligible": str(bullet.draft_eligible).lower(),
                        "source_type": bullet.source_type,
                    },
                )
            )

    return documents


def build_fact_document(*, role_context: str, statement: str, evidence: str | None) -> str:
    if evidence:
        return f"{role_context}\n{statement}\nEvidence: {evidence}"
    return f"{role_context}\n{statement}"


def build_bullet_document(*, role_context: str, text: str, story_angle: str | None) -> str:
    if story_angle:
        return f"{role_context}\nAngle: {story_angle}\n{text}"
    return f"{role_context}\n{text}"
