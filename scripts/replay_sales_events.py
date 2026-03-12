#!/usr/bin/env python3
"""Replay SaleEvent JSONL payloads into the FastAPI /api/sales endpoint."""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Any

import requests


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send sale events from a JSONL file to FastAPI /api/sales",
    )
    parser.add_argument(
        "--file",
        default="data/inventory_events.jsonl",
        help="Path to JSONL file where each line is a SaleEvent JSON object.",
    )
    parser.add_argument(
        "--endpoint",
        default="http://localhost:8000/api/sales",
        help="FastAPI sales endpoint URL.",
    )
    parser.add_argument(
        "--delay-ms",
        type=int,
        default=0,
        help="Optional delay in milliseconds between requests (default: 0).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Request timeout in seconds (default: 5.0).",
    )
    return parser.parse_args()


def setup_logger() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    return logging.getLogger("sales_replay")


def iter_jsonl(path: Path, logger: logging.Logger):
    with path.open("r", encoding="utf-8") as fh:
        for line_number, raw_line in enumerate(fh, start=1):
            line = raw_line.strip()
            if not line:
                continue

            try:
                payload: dict[str, Any] = json.loads(line)
            except json.JSONDecodeError as exc:
                logger.error(
                    "Invalid JSON at line %s: %s",
                    line_number,
                    exc,
                )
                yield line_number, None
                continue

            yield line_number, payload


def send_event(
    session: requests.Session,
    endpoint: str,
    payload: dict[str, Any],
    timeout: float,
) -> requests.Response:
    return session.post(endpoint, json=payload, timeout=timeout)


def main() -> int:
    args = parse_args()
    logger = setup_logger()

    source_file = Path(args.file)
    if not source_file.exists():
        logger.error("Input file does not exist: %s", source_file)
        return 1

    success_count = 0
    failure_count = 0
    sent_count = 0

    logger.info(
        "Starting replay from %s to %s (delay=%sms, timeout=%ss)",
        source_file,
        args.endpoint,
        args.delay_ms,
        args.timeout,
    )

    with requests.Session() as session:
        for line_number, payload in iter_jsonl(source_file, logger):
            if payload is None:
                failure_count += 1
                continue

            sent_count += 1
            event_id = payload.get("event_id", "unknown")

            try:
                response = send_event(
                    session=session,
                    endpoint=args.endpoint,
                    payload=payload,
                    timeout=args.timeout,
                )

                if 200 <= response.status_code < 300:
                    success_count += 1
                else:
                    failure_count += 1
                    logger.warning(
                        "HTTP %s for line=%s event_id=%s body=%s",
                        response.status_code,
                        line_number,
                        event_id,
                        response.text[:500],
                    )

            except requests.RequestException as exc:
                failure_count += 1
                logger.error(
                    "Request failed for line=%s event_id=%s: %s",
                    line_number,
                    event_id,
                    exc,
                )

            if args.delay_ms > 0:
                time.sleep(args.delay_ms / 1000)

    logger.info(
        "Replay finished. attempted=%s succeeded=%s failed=%s",
        sent_count,
        success_count,
        failure_count,
    )

    return 0 if failure_count == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())