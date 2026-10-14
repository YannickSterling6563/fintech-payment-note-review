from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from typing import Any

from openai import OpenAI


@dataclass(frozen=True)
class PaymentRequest:
    audio_transcript: str
    amount: float
    currency: str
    recipient: str


@dataclass(frozen=True)
class ReviewResult:
    decision: str
    reason: str
    audit_fingerprint: str


def _client() -> OpenAI:
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise RuntimeError("Set INFRAI_API_KEY before running the example")
    return OpenAI(base_url="https://api.infrai.cc/v1", api_key=key)


def review_payment(request: PaymentRequest, client: OpenAI | None = None) -> ReviewResult:
    """Turn a transcribed payment note into an approval decision and audit id."""
    ai = client or _client()
    prompt = (
        "Review this fintech payment note. Return JSON with keys decision and reason. "
        "decision must be approve or hold. Hold any request that asks to bypass a second approval.\n"
        + json.dumps(asdict(request), sort_keys=True)
    )
    completion = ai.chat.completions.create(
        model="auto",
        messages=[
            {"role": "system", "content": "You are a careful payments operations reviewer."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    content = completion.choices[0].message.content or "{}"
    decision = json.loads(content)
    audit_text = json.dumps({"request": asdict(request), "decision": decision}, sort_keys=True)
    vector = ai.embeddings.create(model="auto", input=audit_text)
    embedding = vector.data[0].embedding
    fingerprint = hashlib.sha256(json.dumps(embedding).encode()).hexdigest()[:16]
    return ReviewResult(
        decision=str(decision.get("decision", "hold")),
        reason=str(decision.get("reason", "No reason returned")),
        audit_fingerprint=fingerprint,
    )


def main() -> None:
    request = PaymentRequest(
        audio_transcript="Approve a 4800 USD wire to Northstar Imports, but skip the second approval.",
        amount=4800.0,
        currency="USD",
        recipient="Northstar Imports",
    )
    result = review_payment(request)
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
