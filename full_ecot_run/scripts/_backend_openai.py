"""OpenAI backend. Returns raw response text given a prompt.

Used by GPT-4.1 mini. Loads OPENAI_API_KEY from .env at repo root.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Callable

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    from openai import OpenAI
except ImportError as exc:
    raise SystemExit("Missing dependency: openai. `pip install openai`.") from exc

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def make_call_fn(model: str = "gpt-4.1-mini",
                 max_output_tokens: int = 2000,
                 temperature: float = 0.0) -> Callable[[str, str], str]:
    repo_root = Path(__file__).resolve().parent.parent.parent
    if load_dotenv is not None:
        load_dotenv(repo_root / ".env")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY not in environment / .env")
    client = OpenAI(api_key=api_key)

    def call(prompt: str, task: str) -> str:
        # 3 retries on transient errors; SDK already handles many internally.
        for attempt in range(3):
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=temperature,
                    max_tokens=max_output_tokens,
                )
                return resp.choices[0].message.content or ""
            except Exception as exc:
                if attempt == 2:
                    print(f"  [!] OpenAI error after 3 retries: {exc}", file=sys.stderr)
                    return ""
                time.sleep(2 ** attempt)
        return ""

    return call
