from __future__ import annotations

from abc import ABC, abstractmethod
import hashlib
import json
from urllib import error, request

from app.infrastructure.llm.json_content import parse_json_content
from app.simulation.protocol import ContentGenerationRequest, GeneratedContent


class AbstractStructuredContentGenerator(ABC):
    @abstractmethod
    def generate(self, generation_request: ContentGenerationRequest) -> GeneratedContent:
        raise NotImplementedError


class MockStructuredContentGenerator(AbstractStructuredContentGenerator):
    def generate(self, generation_request: ContentGenerationRequest) -> GeneratedContent:
        fact_context = generation_request.fact_context
        instruction = generation_request.instruction.strip() or "Summarize the currently verified facts"
        capability = generation_request.capability

        if capability == "netdisk.upload_file":
            title_seed = str(fact_context.get("title", "Evidence File")).strip() or "Evidence File"
            purpose_seed = str(fact_context.get("purpose", "General upload")).strip() or "General upload"
            file_name = str(fact_context.get("file_name", "report.txt")).strip() or "report.txt"
            document_type = str(
                fact_context.get(
                    "document_type",
                    generation_request.style_context.get("document_type", "incident_report"),
                )
            ).strip() or "incident_report"
            body = self._build_netdisk_document(
                document_type=document_type,
                title=title_seed,
                purpose=purpose_seed,
            )
            return GeneratedContent(
                fields={"file_content": body[:8000], "file_name": file_name[:120]},
                source="mock_local",
                raw_response=body,
                metadata={"generator": "MockStructuredContentGenerator", "document_type": document_type},
            )

        if capability == "forum.create_thread":
            title_seed = str(fact_context.get("requested_title", "Forum Update")).strip() or "Forum Update"
            content_seed = str(fact_context.get("requested_content", instruction)).strip() or instruction
            board_name = str(fact_context.get("board_name", fact_context.get("board_slug", "forum"))).strip()
            share_id = str(fact_context.get("netdisk_share_id", "")).strip()
            access_code = str(fact_context.get("netdisk_access_code", "")).strip()
            share_url = str(fact_context.get("netdisk_share_url", "")).strip()
            variant_seed = str(fact_context.get("draft_id", title_seed)).strip() or title_seed
            title_output = self._build_forum_thread_title(title_seed=title_seed, variant_seed=variant_seed)
            intro_options = [
                f"Posting this to {board_name} because the pattern is too specific to ignore.",
                f"I am adding this to {board_name} for anyone tracking the same anomaly.",
                f"Leaving a record in {board_name} before the details drift any further.",
            ]
            focus_options = [
                f"Current focus: {content_seed}",
                f"Working theory: {content_seed}",
                f"What stands out right now is simple: {content_seed}",
            ]
            closing_options = [
                "I will update this thread if the next checkpoint confirms the pattern.",
                "If anyone can cross-check timestamps, add it before the trail goes cold.",
                "Treat this as a live evidence thread until we can match it against other records.",
            ]
            choice_index = self._variant_index(variant_seed, len(intro_options))
            body = (
                f"{intro_options[choice_index]}\n\n"
                f"{focus_options[self._variant_index(variant_seed + '-focus', len(focus_options))]}\n\n"
                f"{closing_options[self._variant_index(variant_seed + '-close', len(closing_options))]}"
            )
            if share_id and access_code:
                body = (
                    f"{body}\n\n"
                    f"Attached netdisk share: {share_id}\n"
                    f"Access code: {access_code}\n"
                    f"Share URL: {share_url or '/api/v1/netdisk/shares/' + share_id}"
                )
            return GeneratedContent(
                fields={"title": title_output[:120], "content": body[:4000]},
                source="mock_local",
                raw_response=body,
                metadata={"generator": "MockStructuredContentGenerator"},
            )

        if capability == "forum.reply_thread":
            content_seed = str(fact_context.get("requested_content", instruction)).strip() or instruction
            thread_title = str(fact_context.get("thread_title", "Current Thread")).strip()
            body = (
                f"Adding verified details for \"{thread_title}\":\n\n"
                f"{content_seed}\n\n"
                "This reply is based only on currently verified facts."
            )
            return GeneratedContent(
                fields={"content": body[:4000]},
                source="mock_local",
                raw_response=body,
                metadata={"generator": "MockStructuredContentGenerator"},
            )

        return GeneratedContent(
            fields={field: str(fact_context.get(field, instruction)) for field in generation_request.desired_fields},
            source="mock_local",
            raw_response=instruction,
            metadata={"generator": "MockStructuredContentGenerator"},
        )

    @staticmethod
    def _variant_index(seed: str, size: int) -> int:
        if size <= 1:
            return 0
        digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()
        return int(digest[:8], 16) % size

    @staticmethod
    def _build_netdisk_document(*, document_type: str, title: str, purpose: str) -> str:
        if document_type == "timeline_note":
            return (
                f"Timeline Note: {title}\n"
                "Classification: Internal Archive\n\n"
                f"Objective: {purpose}\n\n"
                "Sequence:\n"
                "19:10 - Initial irregular movement recorded near the reported location.\n"
                "19:24 - A second pass confirmed repeated activity and inconsistent lighting.\n"
                "19:41 - Notes were consolidated for later cross-check with witness accounts.\n"
                "20:05 - Material archived for restricted review pending corroboration.\n\n"
                "Assessment: Activity pattern appears deliberate rather than incidental."
            )

        if document_type == "witness_memo":
            return (
                f"Witness Memorandum\nTitle: {title}\n\n"
                f"Reason for record: {purpose}\n\n"
                "Statement:\n"
                "I observed unusual behavior consistent with an attempted handoff or concealed transfer. "
                "The parties involved limited their movement once they noticed nearby foot traffic. "
                "No direct confrontation occurred, but the timing and repetition justified archival capture.\n\n"
                "Recommendation: Compare this memo with access logs and any available street-level reports."
            )

        return (
            f"Incident Report\nTitle: {title}\nStatus: Open for verification\n\n"
            f"Purpose: {purpose}\n\n"
            "Summary:\n"
            "A suspicious pattern was documented and stored for controlled review. "
            "Preliminary notes suggest coordination, repeated presence, or intentional concealment around the observed event.\n\n"
            "Key Points:\n"
            "- Multiple indicators justified evidence retention.\n"
            "- Observations remain preliminary and should be cross-checked.\n"
            "- Public release is not recommended until supporting records are matched.\n\n"
            "Filed for internal follow-up."
        )

    def _build_forum_thread_title(self, *, title_seed: str, variant_seed: str) -> str:
        normalized = title_seed.strip() or "Forum Update"
        lower_title = normalized.lower()

        if "warehouse" in lower_title:
            variants = [
                "[Evidence] Warehouse lights after curfew",
                "[Evidence] After-hours movement at the warehouse",
                "[Timeline] Repeated warehouse activity after closing",
            ]
            return variants[self._variant_index(variant_seed + '-title', len(variants))]

        if "dock" in lower_title:
            variants = [
                "[Evidence] Unscheduled dockside handoff",
                "[Timeline] Dock transfer outside normal hours",
                "[Evidence] Vehicle movement near the dock gate",
            ]
            return variants[self._variant_index(variant_seed + '-title', len(variants))]

        if "corridor" in lower_title or "witness" in lower_title:
            variants = [
                "[Witness Notes] Repeated corridor meetings",
                "[Memo] Short meeting pattern near the back corridor",
                "[Witness Notes] Same pair seen leaving by separate exits",
            ]
            return variants[self._variant_index(variant_seed + '-title', len(variants))]

        if "transit" in lower_title or "timeline" in lower_title:
            variants = [
                "[Timeline] Transit gap around reported sighting",
                "[Evidence] Timing mismatch near the station route",
                "[Timeline] Service gap overlapping the sighting window",
            ]
            return variants[self._variant_index(variant_seed + '-title', len(variants))]

        return normalized


class SiliconFlowStructuredContentGenerator(AbstractStructuredContentGenerator):
    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        base_url: str,
        max_attempts: int = 3,
    ) -> None:
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.max_attempts = max(1, max_attempts)

    def generate(self, generation_request: ContentGenerationRequest) -> GeneratedContent:
        payload = self._build_payload(generation_request)
        last_error = "unknown error"
        for _attempt in range(1, self.max_attempts + 1):
            generated, error_reason = self._call_model(payload)
            if generated is not None:
                generated.source = f"remote_llm:{self.model_name}"
                return generated
            last_error = error_reason or "invalid or empty generation response"

        raise RuntimeError(
            f"SiliconFlow content generation failed after {self.max_attempts} attempts: {last_error}"
        )

    # ------------------------------------------------------------------ #
    #  Capability-specific prompt builders                               #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _prompt_netdisk_upload(generation_request: ContentGenerationRequest) -> tuple[str, str]:
        ctx = generation_request.fact_context
        style = generation_request.style_context
        title = ctx.get("title", "Evidence File")
        purpose = ctx.get("purpose", "General upload")
        file_name = ctx.get("file_name", "report.txt")
        document_type = ctx.get("document_type", style.get("document_type", "incident_report"))

        system = (
            "You are a document archivist in an in-world investigation simulation set in the early 2000s. "
            "Your job is to write plain-text archive documents. "
            "Write only the document body — no meta commentary, no JSON keys as prose, no chain-of-thought. "
            'Return a JSON object with exactly two keys: "file_content" and "file_name". '
            '"file_content" must be the full plain-text document body (multi-line, realistic, at least 80 words). '
            '"file_name" must be a short snake_case filename ending in .txt.'
        )
        user = (
            f"Write a {document_type.replace('_', ' ')} document.\n"
            f"Title: {title}\n"
            f"Purpose: {purpose}\n"
            f"Suggested filename: {file_name}\n\n"
            "Requirements:\n"
            "- Write in English.\n"
            "- The document should read like a real internal archive record.\n"
            "- Include timestamps, observations, and a short assessment section.\n"
            "- Do NOT repeat these instructions inside the document.\n"
            '- Return JSON: {"file_content": "<full document text>", "file_name": "<filename.txt>"}'
        )
        return system, user

    @staticmethod
    def _prompt_forum_create_thread(generation_request: ContentGenerationRequest) -> tuple[str, str]:
        ctx = generation_request.fact_context
        title_seed = ctx.get("requested_title", "Forum Update")
        content_seed = ctx.get("requested_content", "")
        board_name = ctx.get("board_name", ctx.get("board_slug", "forum"))
        share_id = ctx.get("netdisk_share_id", "")
        access_code = ctx.get("netdisk_access_code", "")
        share_url = ctx.get("netdisk_share_url", "")

        share_block = ""
        if share_id and access_code:
            share_block = (
                f"\nAlso append these lines at the end of the content:\n"
                f"Attached netdisk share: {share_id}\n"
                f"Access code: {access_code}\n"
                f"Share URL: {share_url or '/api/v1/netdisk/shares/' + share_id}"
            )

        system = (
            "You are writing forum posts for an in-world online community in a simulation. "
            "Write in English. Posts should feel like real community messages — personal, specific, not generic. "
            "Do not add meta commentary or repeat instructions. "
            'Return a JSON object with exactly two keys: "title" and "content".'
        )
        user = (
            f"Write a forum thread for the board: {board_name}\n"
            f"Suggested title theme: {title_seed}\n"
            f"Core topic: {content_seed}\n\n"
            "Requirements:\n"
            "- Title: short, intriguing, under 80 characters, no raw goal text.\n"
            "- Content: 3-5 sentences, first-person, specific observations, not generic filler.\n"
            f"- Do NOT use the title theme as a literal title.{share_block}\n"
            '- Return JSON: {"title": "<thread title>", "content": "<post body>"}'
        )
        return system, user

    @staticmethod
    def _prompt_news_publish_article(generation_request: ContentGenerationRequest) -> tuple[str, str]:
        ctx = generation_request.fact_context
        category = str(ctx.get("category", "community"))
        title_seed = str(ctx.get("requested_title", ""))
        content_seed = str(ctx.get("requested_content", ""))
        related_thread_ids = ctx.get("requested_related_thread_ids", [])
        related_share_ids = ctx.get("requested_related_share_ids", [])

        if not isinstance(related_thread_ids, list):
            related_thread_ids = []
        if not isinstance(related_share_ids, list):
            related_share_ids = []

        thread_block = ""
        share_block = ""
        if related_thread_ids:
            thread_block = (
                "\nYou MUST include each thread id verbatim in the article body: "
                + ", ".join(str(item) for item in related_thread_ids if str(item).strip())
            )
        if related_share_ids:
            share_block = (
                "\nYou MUST include each share id verbatim in the article body: "
                + ", ".join(str(item) for item in related_share_ids if str(item).strip())
            )

        system = (
            "You are writing a publish-ready news article for an in-world online news site. "
            "Write in English with a neutral journalistic tone. "
            "Do not include meta commentary or prompt instructions. "
            'Return a JSON object with exactly two keys: "title" and "content".'
        )
        user = (
            f"Category: {category}\n"
            f"Requested title hint: {title_seed}\n"
            f"Core facts to report: {content_seed}\n"
            f"{thread_block}"
            f"{share_block}\n\n"
            "Requirements:\n"
            "- title: concise newsroom headline, under 100 chars\n"
            "- content: 2-4 paragraphs, concrete and factual\n"
            "- if related ids are given above, include them exactly as written\n"
            '- Return JSON: {"title":"<headline>","content":"<article body>"}'
        )
        return system, user

    @staticmethod
    def _prompt_generic(generation_request: ContentGenerationRequest) -> tuple[str, str]:
        desired = ", ".join(f'"{f}"' for f in generation_request.desired_fields)
        ctx_summary = json.dumps(generation_request.fact_context, ensure_ascii=False)

        system = (
            "You are a content generator for an in-world AI society simulation. "
            "Write publishable in-world content only — no meta text, no chain-of-thought. "
            f"Return a JSON object with exactly these keys: {desired}."
        )
        user = (
            f"Task: {generation_request.instruction}\n"
            f"Context: {ctx_summary}\n\n"
            f"Return JSON with keys: {desired}"
        )
        return system, user

    def _build_payload(self, generation_request: ContentGenerationRequest) -> dict:
        capability = generation_request.capability
        if capability == "netdisk.upload_file":
            system_prompt, user_prompt_text = self._prompt_netdisk_upload(generation_request)
        elif capability == "forum.create_thread":
            system_prompt, user_prompt_text = self._prompt_forum_create_thread(generation_request)
        elif capability == "news.publish_article":
            system_prompt, user_prompt_text = self._prompt_news_publish_article(generation_request)
        else:
            system_prompt, user_prompt_text = self._prompt_generic(generation_request)

        return {
            "model": self.model_name,
            "temperature": 0.7,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_text},
            ],
            "response_format": {"type": "json_object"},
        }

    def _call_model(self, payload: dict) -> tuple[GeneratedContent | None, str | None]:
        endpoint = f"{self.base_url}/chat/completions"
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(http_request, timeout=45) as response:
                response_text = response.read().decode("utf-8")
        except TimeoutError:
            return None, "timeout"
        except error.HTTPError as exc:
            try:
                body_preview = exc.read().decode("utf-8", errors="replace")[:400]
            except Exception:
                body_preview = "<unavailable>"
            return None, f"http {exc.code}: {body_preview}"
        except error.URLError as exc:
            return None, f"url_error: {exc.reason}"

        try:
            data = json.loads(response_text)
            content = data["choices"][0]["message"]["content"]
            fields = parse_json_content(content)
            if fields is None:
                return None, "content_json_parse_failed"

            raw_response = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)

            return (
                GeneratedContent(
                    fields=fields,
                    source=f"remote_llm:{self.model_name}",
                    raw_response=raw_response,
                    metadata={"generator": "SiliconFlowStructuredContentGenerator"},
                ),
                None,
            )
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, f"response_parse_error: {exc}"
