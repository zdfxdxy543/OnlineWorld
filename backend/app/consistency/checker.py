from __future__ import annotations

from app.domain.models import DraftPostPlan


class ConsistencyChecker:
    def validate_post_content(self, plan: DraftPostPlan, content: str) -> list[str]:
        violations: list[str] = []

        if plan.referenced_resource is not None:
            if plan.referenced_resource.resource_id not in content:
                violations.append("missing-resource-id")
            if plan.referenced_resource.access_code not in content:
                violations.append("missing-access-code")

        for fact in plan.facts:
            if fact not in content:
                violations.append(f"missing-fact:{fact}")

        return violations
