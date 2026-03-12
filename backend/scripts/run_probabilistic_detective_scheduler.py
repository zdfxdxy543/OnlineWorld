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
class DetectiveDispatchProbabilities:
    detective_story: float
    new_detective_long_arc: float
    continue_detective_long_arc: float

    def normalize(self) -> "DetectiveDispatchProbabilities":
        total = self.detective_story + self.new_detective_long_arc + self.continue_detective_long_arc
        if total <= 0:
            return DetectiveDispatchProbabilities(0.45, 0.30, 0.25)
        return DetectiveDispatchProbabilities(
            self.detective_story / total,
            self.new_detective_long_arc / total,
            self.continue_detective_long_arc / total,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Dispatch mystery scheduler runs with probabilities across: "
            "regular detective story, new long detective arc, continue long detective arc."
        )
    )
    parser.add_argument("--actors", default="", help="Comma-separated actor ids, e.g. aria,milo")
    parser.add_argument("--cycles", type=int, default=1, help="How many dispatch cycles to run")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed for reproducible dispatch")
    parser.add_argument("--detective-story-prob", type=float, default=0.45)
    parser.add_argument("--new-detective-long-arc-prob", type=float, default=0.30)
    parser.add_argument("--continue-detective-long-arc-prob", type=float, default=0.25)
    parser.add_argument(
        "--spawn-probability",
        type=float,
        default=None,
        help="Optional override for SCHEDULER_NEW_ACTOR_PROBABILITY (0.0 to 1.0).",
    )
    return parser.parse_args()


def _format_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def _build_detective_goal(rng: random.Random) -> str:
    samples = [
        "Investigate a suspicious movement pattern around the old warehouse.",
        "Investigate mismatched dockside transfer records from last night.",
        "Investigate why witness statements conflict about corridor meetings.",
        "Investigate timeline gaps in transit logs near the reported sighting.",
    ]
    return rng.choice(samples)


def _build_new_detective_arc_goal(rng: random.Random) -> str:
    samples = [
        "Long-case: recurring warehouse lights after curfew",
        "Long-case: repeated unsigned transfer entries at the docks",
        "Long-case: missing surveillance intervals around station exits",
        "Long-case: witness accounts diverge on corridor rendezvous",
    ]
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"detective: {rng.choice(samples)} [{suffix}]"


def _pick_action(
    *,
    rng: random.Random,
    probs: DetectiveDispatchProbabilities,
    has_open_detective_arcs: bool,
) -> str:
    normalized = probs.normalize()
    thresholds = [
        ("detective_story", normalized.detective_story),
        ("new_detective_long_arc", normalized.new_detective_long_arc),
        ("continue_detective_long_arc", normalized.continue_detective_long_arc),
    ]
    roll = rng.random()
    cursor = 0.0
    selected = "detective_story"
    for name, weight in thresholds:
        cursor += weight
        if roll <= cursor:
            selected = name
            break

    if selected == "continue_detective_long_arc" and not has_open_detective_arcs:
        return "new_detective_long_arc"
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
    probs = DetectiveDispatchProbabilities(
        detective_story=max(0.0, args.detective_story_prob),
        new_detective_long_arc=max(0.0, args.new_detective_long_arc_prob),
        continue_detective_long_arc=max(0.0, args.continue_detective_long_arc_prob),
    )

    cycles = max(1, args.cycles)
    action_counts: dict[str, int] = {
        "detective_story": 0,
        "new_detective_long_arc": 0,
        "continue_detective_long_arc": 0,
    }
    success_cycles = 0
    failed_cycles = 0
    capability_counts: dict[str, int] = {}

    initial_open_detective_arcs = [arc for arc in story_arc_service.list_open_arcs(limit=1000) if arc.goal_key.startswith("detective:")]

    print("Probabilistic detective dispatcher started.")
    print(f"cycles={cycles}")
    print("probabilities(normalized)=")
    print(_format_json(asdict(probs.normalize())))

    for cycle in range(1, cycles + 1):
        open_detective_arcs = [
            arc for arc in story_arc_service.list_open_arcs(limit=1000) if arc.goal_key.startswith("detective:")
        ]
        action = _pick_action(
            rng=rng,
            probs=probs,
            has_open_detective_arcs=bool(open_detective_arcs),
        )
        action_counts[action] = action_counts.get(action, 0) + 1

        if action == "detective_story":
            endpoint = "/api/v1/ai/scheduler/run"
            goal = _build_detective_goal(rng)
            selected_arc_id = ""
        elif action == "new_detective_long_arc":
            endpoint = "/api/v1/ai/scheduler/run-detective-arc"
            goal = _build_new_detective_arc_goal(rng)
            selected_arc_id = ""
        else:
            endpoint = "/api/v1/ai/scheduler/run-detective-arc"
            arc = rng.choice(open_detective_arcs)
            goal = arc.goal_key
            selected_arc_id = arc.arc_id

        print("\n----------------------------------------")
        print(f"cycle={cycle}")
        print(f"dispatch_action={action}")
        print(f"endpoint={endpoint}")
        print(f"selected_arc_id={selected_arc_id}")
        print(f"goal={goal}")

        try:
            report = _run_scheduler(client, endpoint=endpoint, goal=goal, actors=actors)
        except Exception as exc:
            failed_cycles += 1
            print(f"cycle_result=failed error={exc}")
            continue

        success_cycles += 1
        executed_caps = [item.get("capability", "") for item in report.get("results", [])]
        for cap in executed_caps:
            if cap:
                capability_counts[cap] = capability_counts.get(cap, 0) + 1

        print(f"story_id={report.get('story_id')}")
        print(f"status={report.get('status')}")
        print(f"planner={report.get('planner_name')}")
        print(f"steps_executed={len(executed_caps)}")
        print(f"capabilities={executed_caps}")

    final_open_detective_arcs = [arc for arc in story_arc_service.list_open_arcs(limit=1000) if arc.goal_key.startswith("detective:")]
    sorted_caps = sorted(capability_counts.items(), key=lambda item: (-item[1], item[0]))

    print("\n========================================")
    print("detective_dispatch_summary")
    print(f"cycles_total={cycles}")
    print(f"cycles_success={success_cycles}")
    print(f"cycles_failed={failed_cycles}")
    print("action_counts=")
    print(_format_json(action_counts))
    print(f"open_detective_arcs_start={len(initial_open_detective_arcs)}")
    print(f"open_detective_arcs_end={len(final_open_detective_arcs)}")
    print(f"open_detective_arcs_delta={len(final_open_detective_arcs) - len(initial_open_detective_arcs)}")
    print("capability_execution_counts=")
    print(_format_json({key: value for key, value in sorted_caps}))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.extend(["--cycles", "3", "--actors", "aria"])
    main()
