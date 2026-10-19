#!/usr/bin/env python3
"""Validate optional scene policy, not geometry, permissions or engine readiness."""
import argparse
import json
from pathlib import Path


DEFAULTS = {
    "intent": "original_game",
    "blockout": "auto",
    "master_variants": "auto",
    "human_edit_preservation": "auto",
    "weathering": "off",
    "human_review_stages": ["final"],
    "repair_attempts_per_issue": 2,
}


def normalize(options):
    if not isinstance(options, dict):
        raise ValueError("scene_options must be an object")
    unknown = options.keys() - DEFAULTS.keys()
    if unknown:
        raise ValueError("Unknown scene options: " + ", ".join(sorted(unknown)))
    result = {**DEFAULTS, **options}
    for key in ("blockout", "master_variants", "human_edit_preservation", "weathering"):
        if result[key] not in ("auto", "on", "off"):
            raise ValueError(key + " must be auto, on or off")
    if result["intent"] not in ("original_game", "reference_guided", "strict_reconstruction"):
        raise ValueError("Unknown scene intent")
    stages = result["human_review_stages"]
    if not isinstance(stages, list) or any(
        not isinstance(s, str) or s not in ("blockout", "complex_assets", "final")
        for s in stages
    ):
        raise ValueError("Invalid human_review_stages")
    if len(stages) != len(set(stages)):
        raise ValueError("Duplicate human review stage")
    if result["blockout"] == "off" and "blockout" in stages:
        raise ValueError("Blockout review conflicts with blockout=off")
    attempts = result["repair_attempts_per_issue"]
    if type(attempts) is not int or attempts < 0:
        raise ValueError("repair_attempts_per_issue must be a nonnegative integer")
    result["human_review_stages"] = list(stages)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    args = parser.parse_args()
    try:
        contract = json.loads(args.contract.read_text(encoding="utf-8-sig"))
        if not isinstance(contract, dict):
            raise ValueError("Contract must be an object")
        result = normalize(contract.get("scene_options", {}))
    except (ValueError, OSError) as exc:
        print(json.dumps({"status": "fail", "reason": str(exc)}))
        return 2
    print(json.dumps({"status": "pass", "scope": "scene_policy_only", "scene_options": result}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
