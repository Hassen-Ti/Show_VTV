"""CLI headless du show à personas.

Exemple :
    python -m show.runner --topic "Faut-il ralentir l'IA ?" \
        --guest-a "provocateur:physicien:physique quantique:+0.8" \
        --guest-b "diplomate:philosophe:éthique des techniques:-0.6" \
        --rounds 3 --out result.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
from openai import OpenAI

from show.graph.show_graph import run_show
from show.personas.registry import make_guest
from show.personas.vector import PersonaVector

RESET = "\033[0m"
COLORS = {"moderator": "\033[93m", "guest_a": "\033[96m", "guest_b": "\033[95m"}
DIM = "\033[2m"


def parse_guest_spec(spec: str, agent_id: str) -> PersonaVector:
    """``personnalité:domaine:spécialisation:stance`` → PersonaVector."""
    # split limité + rpartition : la spécialisation peut contenir des ":"
    head = spec.split(":", 2)
    rest = head[2] if len(head) == 3 else ""
    specialization_raw, _, stance_part = rest.rpartition(":")
    if len(head) != 3 or not specialization_raw:
        raise SystemExit(
            f"Spec invité invalide: {spec!r} "
            "(attendu personnalité:domaine:spécialisation:stance, ex provocateur:physicien:quantique:+0.8)"
        )
    personality, domain, specialization, stance_raw = (
        p.strip() for p in (head[0], head[1], specialization_raw, stance_part)
    )
    try:
        stance = float(stance_raw)
    except ValueError:
        raise SystemExit(f"Stance invalide: {stance_raw!r} (attendu un nombre dans [-1, 1])")
    return make_guest(personality, domain, specialization, stance, agent_id=agent_id)


def make_console_emitter(guest_ids: dict[str, str]):
    def emit(event: dict[str, Any]) -> None:
        kind = event["type"]
        if kind == "moderator":
            print(f"\n{COLORS['moderator']}🎙️  ANIMATEUR — {event['text']}{RESET}")
        elif kind == "turn":
            color = COLORS.get(guest_ids.get(event["agent"], ""), "")
            evidence = " [preuve web]" if event.get("evidence_used") else ""
            print(
                f"\n{color}🗣️  {event['name']} (round {event['round']}, "
                f"tactique {event['tactic']}{evidence}) —{RESET}\n{color}{event['text']}{RESET}"
            )
        elif kind == "inner_monologue":
            print(f"{DIM}   💭 ({event['agent']}) {event['text']}{RESET}")
        elif kind == "stance_update":
            stances = ", ".join(f"{aid}: {v:+.2f}" for aid, v in event["stances"].items())
            print(f"{DIM}   📊 tension {event['tension']:.2f} | stances {stances}{RESET}")
        elif kind == "step":
            print(f"{DIM}   … {event['agent']} {event['label']}{RESET}")

    return emit


def print_final_report(result: dict[str, Any], guests: list[PersonaVector]) -> None:
    print("\n" + "=" * 60)
    print("ÉVOLUTION DES POSITIONS")
    print("=" * 60)
    for guest in guests:
        history = result["stance_history"][guest.agent_id]
        trajectory = " → ".join(f"{v:+.2f}" for v in history)
        mind = result["minds"][guest.agent_id]
        print(f"\n{guest.name} ({guest.personality} × {guest.domain})")
        print(f"  stance     : {trajectory}")
        print(f"  conviction : {mind['conviction']:.2f} | humeur finale "
              f"(valence {mind['valence']:+.2f}, arousal {mind['arousal']:.2f})")
        if mind["inner_monologue"]:
            print(f"  dernière pensée : {mind['inner_monologue']}")
    print(f"\nTension finale du plateau : {result['tension']:.2f}")


def export_json(result: dict[str, Any], path: str) -> None:
    payload = {
        "topic": result["topic"],
        "rounds": result["round"],
        "tension": result["tension"],
        "transcript": result["transcript"],
        "stance_history": result["stance_history"],
        "minds": result["minds"],
        "moderator_notes": result.get("moderator_notes", []),
    }
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nÉtat final exporté : {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Show TV à personas agentiques (headless)")
    parser.add_argument("--topic", required=True, help="Question du débat")
    parser.add_argument(
        "--guest-a",
        default="provocateur:physicien:intelligence artificielle:+0.8",
        help="personnalité:domaine:spécialisation:stance",
    )
    parser.add_argument(
        "--guest-b",
        default="diplomate:philosophe:éthique des techniques:-0.6",
        help="personnalité:domaine:spécialisation:stance",
    )
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--out", default="", help="Chemin d'export JSON du ShowState final")
    parser.add_argument("--no-web-search", action="store_true")
    args = parser.parse_args()
    if args.rounds < 1:
        raise SystemExit("--rounds doit être >= 1")

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY manquant dans l'environnement")

    guest_a = parse_guest_spec(args.guest_a, "guest_a")
    guest_b = parse_guest_spec(args.guest_b, "guest_b")
    print(f"Sujet : {args.topic}")
    print(f"Invité A : {guest_a.name} — {guest_a.specialization} (stance {guest_a.initial_stance:+.2f})")
    print(f"Invité B : {guest_b.name} — {guest_b.specialization} (stance {guest_b.initial_stance:+.2f})")

    result = run_show(
        args.topic,
        guest_a,
        guest_b,
        max_rounds=args.rounds,
        client=OpenAI(api_key=api_key),
        enable_web_search=not args.no_web_search,
        emit=make_console_emitter({g.agent_id: g.agent_id for g in (guest_a, guest_b)}),
    )

    print_final_report(result, [guest_a, guest_b])
    if args.out:
        export_json(result, args.out)


if __name__ == "__main__":
    main()
