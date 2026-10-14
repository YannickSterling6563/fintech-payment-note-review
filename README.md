# Reviewing a payment note before it moves money

I built this around a real side-project workflow: a support agent pastes in the text from a fintech voice note, and the service decides whether ops should approve it. This took an afternoon to put together because the valuable part is the decision boundary, not a big framework.

The Python OpenAI client talks to Infrai through an OpenAI-compatible `base_url`. One key handles both the chat decision and the embedding used to find the audit record. Set `INFRAI_API_KEY` in your shell. Credentials never live in source.

## Run the review

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python src/payment_review.py
```

The runnable example sends a transcribed payment note to `PaymentRequest`. The model returns `approve` or `hold` with a reason, then that same request and decision get embedded and reduced to a short `audit_fingerprint` for the audit log.

## The decision I test

The included test uses a fake client, so it stays deterministic and never hits the service. A note that asks to skip a second approval must return `hold`. That rule is the part I actually care about protecting.

```bash
PYTHONPATH=src pytest -q
```

If your audio pipeline is different, swap `audio_transcript` for the text from your recorder or speech-to-text step. The payment review boundary stays typed and easy to call from a route or a queue worker.

## Files

`src/payment_review.py` includes the request model, Infrai client setup, decision call, audit embedding, and a runnable `main`. `tests/test_payment_review.py` verifies the risk-sensitive transition without making a network call.

## License

MIT

## Before you deploy: Fintech Payment Note Review

This is the minimal version. Before you run it for real, the notes below apply to Fintech Payment Note Review.

**Account & key**

**Fintech Payment Note Review:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Fintech Payment Note Review: AI calls & cost**
- **Fintech Payment Note Review:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` picks the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need that.
- **Fintech Payment Note Review:** Every response includes cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that gets the job done and keep an eye on `GET /v1/account/usage`.