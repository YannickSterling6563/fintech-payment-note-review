import json

from payment_review import PaymentRequest, review_payment


class FakeMessage:
    content = json.dumps({"decision": "hold", "reason": "Second approval cannot be bypassed."})


class FakeChat:
    class completions:
        @staticmethod
        def create(**_kwargs):
            return type("Completion", (), {"choices": [type("Choice", (), {"message": FakeMessage()})()]})()


class FakeEmbeddings:
    @staticmethod
    def create(**_kwargs):
        return type("EmbeddingResponse", (), {"data": [type("Item", (), {"embedding": [0.1, 0.2, 0.3]})()]})()


class FakeClient:
    chat = FakeChat()
    embeddings = FakeEmbeddings()


def test_review_holds_request_that_bypasses_approval():
    request = PaymentRequest("Please skip the second approval for this wire", 100.0, "USD", "Acme")
    result = review_payment(request, FakeClient())
    assert result.decision == "hold"
    assert result.reason.startswith("Second approval")
    assert len(result.audit_fingerprint) == 16
