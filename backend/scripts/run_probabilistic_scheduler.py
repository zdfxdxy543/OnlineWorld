from __future__ import annotations

import argparse
import json
import os
import random
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient


@dataclass(slots=True)
class DispatchProbabilities:
    new_story: float
    new_long_arc: float
    continue_long_arc: float

    def normalize(self) -> "DispatchProbabilities":
        total = self.new_story + self.new_long_arc + self.continue_long_arc
        if total <= 0:
            return DispatchProbabilities(0.5, 0.3, 0.2)
        return DispatchProbabilities(
            self.new_story / total,
            self.new_long_arc / total,
            self.continue_long_arc / total,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Dispatch scheduler runs with probabilities across: new story line, "
            "new long arc, continue long arc."
        )
    )
    parser.add_argument("--actors", default="", help="Comma-separated actor ids, e.g. aria,milo")
    parser.add_argument("--cycles", type=int, default=1, help="How many dispatch cycles to run")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed for reproducible dispatch")
    parser.add_argument("--new-story-prob", type=float, default=0.55, help="Probability of starting a new short story")
    parser.add_argument("--new-long-arc-prob", type=float, default=0.25, help="Probability of starting a new long arc")
    parser.add_argument(
        "--continue-long-arc-prob",
        type=float,
        default=0.20,
        help="Probability of continuing an existing long arc",
    )
    parser.add_argument(
        "--spawn-probability",
        type=float,
        default=None,
        help="Optional override for SCHEDULER_NEW_ACTOR_PROBABILITY (0.0 to 1.0).",
    )
    return parser.parse_args()


def _format_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def _build_short_story_goal(rng: random.Random) -> str:
    samples = [
        "A normal day in town with small interpersonal misunderstandings and resolution.",
        "A busy market morning where neighbors share practical tips and updates.",
        "A community notice about transport timing changes and daily life adjustments.",
        "An evening neighborhood discussion about shared resources and routines.",
    ]
    return rng.choice(samples)


def _build_new_arc_goal(rng: random.Random) -> str:
    samples = [
        "Ongoing issue: repeated inventory mismatch in the canteen supply room",
        "Ongoing issue: unexplained schedule drift in the neighborhood shuttle",
        "Ongoing issue: recurring noise pattern near the community center",
        "Ongoing issue: missing maintenance logs in the transit depot",
    ]
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{rng.choice(samples)} [{suffix}]"


def _pick_dispatch_action(
    *,
    rng: random.Random,
    probs: DispatchProbabilities,
    has_open_arcs: bool,
) -> str:
    normalized = probs.normalize()
    thresholds = [
        ("new_story", normalized.new_story),
        ("new_long_arc", normalized.new_long_arc),
        ("continue_long_arc", normalized.continue_long_arc),
    ]
    roll = rng.random()
    cursor = 0.0
    selected = "new_story"
    for name, weight in thresholds:
        cursor += weight
        if roll <= cursor:
            selected = name
            break

    # If asked to continue but no open arcs exist, fallback to creating a new long arc.
    if selected == "continue_long_arc" and not has_open_arcs:
        return "new_long_arc"
    return selected


def _run_scheduler(client: TestClient, *, endpoint: str, goal: str, actors: list[str]) -> dict:
    payload = {"goal": goal, "actors": actors}
    response = client.post(endpoint, json=payload)
    if response.status_code >= 400:
        raise RuntimeError(f"Scheduler call failed: HTTP {response.status_code} {response.text}")
    return response.json()


def main() -> None:
    args = parse_args()

    if args.spawn_probability is not None:
        clamped = max(0.0, min(1.0, args.spawn_probability))
        os.environ["SCHEDULER_NEW_ACTOR_PROBABILITY"] = str(clamped)

    rng = random.Random(args.seed)
    from app.main import create_app

    app = create_app()
    client = TestClient(app)
    story_arc_service = app.state.container.story_arc_service

    actors = [item.strip() for item in args.actors.split(",") if item.strip()]
    probs = DispatchProbabilities(
        new_story=max(0.0, args.new_story_prob),
        new_long_arc=max(0.0, args.new_long_arc_prob),
        continue_long_arc=max(0.0, args.continue_long_arc_prob),
    )

    cycles = max(1, args.cycles)
    action_counts: dict[str, int] = {
        "new_story": 0,
        "new_long_arc": 0,
        "continue_long_arc": 0,
    }
    success_cycles = 0
    failed_cycles = 0
    capability_counts: dict[str, int] = {}
    start_open_arc_count = len(story_arc_service.list_open_arcs(limit=1000))

    print("Probabilistic scheduler dispatcher started.")
    print(f"cycles={cycles}")
    print(
        "probabilities(normalized)="
        f"{_format_json(asdict(probs.normalize()))}"
    )

    for cycle in range(1, cycles + 1):
        open_arcs = story_arc_service.list_open_arcs(limit=100)
        action = _pick_dispatch_action(
            rng=rng,
            probs=probs,
            has_open_arcs=bool(open_arcs),
        )

        if action == "new_story":
            endpoint = "/api/v1/ai/scheduler/run-life"
            goal = _build_short_story_goal(rng)
            selected_arc_id = ""
        elif action == "new_long_arc":
            endpoint = "/api/v1/ai/scheduler/run-life-arc"
            goal = _build_new_arc_goal(rng)
            selected_arc_id = ""
        else:
            endpoint = "/api/v1/ai/scheduler/run-life-arc"
            arc = rng.choice(open_arcs)
            goal = arc.goal_key
            selected_arc_id = arc.arc_id

        print("\n----------------------------------------")
        print(f"cycle={cycle}")
        print(f"dispatch_action={action}")
        print(f"endpoint={endpoint}")
        print(f"selected_arc_id={selected_arc_id}")
        print(f"goal={goal}")
        action_counts[action] = action_counts.get(action, 0) + 1

        try:
            report = _run_scheduler(client, endpoint=endpoint, goal=goal, actors=actors)
        except Exception as exc:
            print(f"cycle_result=failed error={exc}")
            failed_cycles += 1
            continue

        success_cycles += 1
        executed_caps = [item.get("capability", "") for item in report.get("results", [])]
        for cap in executed_caps:
            if not cap:
                continue
            capability_counts[cap] = capability_counts.get(cap, 0) + 1

        print(f"story_id={report.get('story_id')}")
        print(f"status={report.get('status')}")
        print(f"planner={report.get('planner_name')}")
        print(f"steps_executed={len(executed_caps)}")
        print(f"capabilities={executed_caps}")

    end_open_arc_count = len(story_arc_service.list_open_arcs(limit=1000))
    sorted_caps = sorted(capability_counts.items(), key=lambda item: (-item[1], item[0]))

    print("\n========================================")
    print("dispatch_summary")
    print(f"cycles_total={cycles}")
    print(f"cycles_success={success_cycles}")
    print(f"cycles_failed={failed_cycles}")
    print("action_counts=")
    print(_format_json(action_counts))
    print(f"open_arcs_start={start_open_arc_count}")
    print(f"open_arcs_end={end_open_arc_count}")
    print(f"open_arcs_delta={end_open_arc_count - start_open_arc_count}")
    print("capability_execution_counts=")
    print(_format_json({key: value for key, value in sorted_caps}))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.extend(["--cycles", "3", "--actors", "aria"])
    main()
