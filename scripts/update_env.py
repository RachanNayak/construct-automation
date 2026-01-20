#!/usr/bin/env python3
"""
Simple helper to update keys in a .env file.

Usage:
  python3 scripts/update_env.py --env .env --email you@example.com --password secret --company "My Co"

This will update (or add) TEST_EMAIL, TEST_PASSWORD and COMPANY_NAME in the given .env file.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys


def read_env(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def write_env(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def set_key(lines: list[str], key: str, value: str) -> list[str]:
    updated = []
    found = False
    for line in lines:
        if not line or line.strip().startswith("#"):
            updated.append(line)
            continue
        if "=" in line:
            k, _ = line.split("=", 1)
            if k.strip() == key:
                updated.append(f"{key}={value}")
                found = True
                continue
        updated.append(line)
    if not found:
        updated.append(f"{key}={value}")
    return updated


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Update .env values")
    p.add_argument("--env", default=".env", help="Path to .env file")
    p.add_argument("--email", help="TEST_EMAIL value")
    p.add_argument("--password", help="TEST_PASSWORD value")
    p.add_argument("--company", help="COMPANY_NAME value")
    p.add_argument("--website", help="WEBSITE_URL value")
    args = p.parse_args(argv)

    env_path = Path(args.env)
    lines = read_env(env_path)

    if args.email:
        lines = set_key(lines, "TEST_EMAIL", args.email)
    if args.password:
        lines = set_key(lines, "TEST_PASSWORD", args.password)
    if args.company:
        lines = set_key(lines, "COMPANY_NAME", args.company)
    if args.website:
        lines = set_key(lines, "WEBSITE_URL", args.website)

    write_env(env_path, lines)
    print(f"Updated {env_path} with:", end=" ")
    updates = []
    if args.email:
        updates.append("TEST_EMAIL")
    if args.password:
        updates.append("TEST_PASSWORD")
    if args.company:
        updates.append("COMPANY_NAME")
    if args.website:
        updates.append("WEBSITE_URL")
    print(", ".join(updates) if updates else "(no changes requested)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

d