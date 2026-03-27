from controllers import health_controller


def test_health_success(monkeypatch):
    class DummyConnection:
        def close(self):
            return None

    class DummySession:
        def execute(self, statement):
            return 1

        def close(self):
            return None

    monkeypatch.setattr(health_controller, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(health_controller.pika, "URLParameters", lambda url: url)
    monkeypatch.setattr(
        health_controller.pika,
        "BlockingConnection",
        lambda params: DummyConnection(),
    )

    response = health_controller.health_check()

    assert response == {"status": "ok", "db": "ok", "rabbitmq": "ok"}


def test_health_marks_failed_dependencies(monkeypatch):
    class BrokenSession:
        def execute(self, statement):
            raise RuntimeError("db down")

        def close(self):
            return None

    monkeypatch.setattr(health_controller, "SessionLocal", lambda: BrokenSession())
    monkeypatch.setattr(health_controller.pika, "URLParameters", lambda url: url)

    def raise_rabbit(*args, **kwargs):
        raise RuntimeError("rabbit down")

    monkeypatch.setattr(health_controller.pika, "BlockingConnection", raise_rabbit)

    response = health_controller.health_check()

    assert response == {"status": "error", "db": "error", "rabbitmq": "error"}
