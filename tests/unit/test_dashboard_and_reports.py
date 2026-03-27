from datetime import datetime
from types import SimpleNamespace

from controllers.customer_dashboard_controller import list_customers
from controllers.menu_analytics_controller import menu_revenue, menu_trends, top_menu_items
from controllers.point_dashboard_controller import (
    point_summary,
    point_transactions,
    top_customers_by_points,
)
from controllers.report_controller import build_overview, cached_overview, overview_report
from controllers.review_dashboard_controller import list_reviews, review_summary, reviews_by_menu


class QueryStub:
    def __init__(
        self,
        all_value=None,
        scalar_value=None,
        one_value=None,
        count_value=None,
    ):
        self._all_value = list(all_value or [])
        self._scalar_value = scalar_value
        self._one_value = one_value
        self._count_value = count_value
        self.filters = []
        self.limit_value = None

    def join(self, *args, **kwargs):
        return self

    def outerjoin(self, *args, **kwargs):
        return self

    def filter(self, *conditions):
        self.filters.extend(conditions)
        return self

    def group_by(self, *args, **kwargs):
        return self

    def having(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def distinct(self):
        return self

    def count(self):
        return self._count_value

    def scalar(self):
        return self._scalar_value

    def one(self):
        return self._one_value

    def all(self):
        return list(self._all_value)


class DBSequence:
    def __init__(self, queries):
        self.queries = list(queries)

    def query(self, *args, **kwargs):
        return self.queries.pop(0)

    def close(self):
        pass


def owner_user():
    return SimpleNamespace(role="owner", restaurant_id=123)


def test_list_customers_supports_search_and_formats_rows():
    rows = [
        SimpleNamespace(
            user_id="u-1",
            display_name="Alice",
            email="alice@example.com",
            phone="0909",
            total_orders=3,
            total_spent=150.5,
            total_points=1200,
            last_visit=datetime(2026, 3, 27, 10, 15, 0),
        )
    ]
    db = DBSequence([QueryStub(all_value=rows)])

    result = list_customers(search="alice", db=db, current_user=owner_user())

    assert result == [
        {
            "user_id": "u-1",
            "name": "Alice",
            "email": "alice@example.com",
            "phone": "0909",
            "total_orders": 3,
            "total_spent": 150.5,
            "total_points": 1200,
            "last_visit": "2026-03-27T10:15:00",
        }
    ]


def test_list_customers_handles_filters_and_email_fallback():
    rows = [
        SimpleNamespace(
            user_id="u-2",
            display_name=None,
            email="returning@example.com",
            phone=None,
            total_orders=2,
            total_spent=80,
            total_points=30,
            last_visit=None,
        )
    ]
    db = DBSequence([QueryStub(all_value=rows)])

    result = list_customers(filter="returning", db=db, current_user=owner_user())

    assert result[0]["name"] == "returning@example.com"
    assert result[0]["last_visit"] is None


def test_point_dashboard_endpoints_transform_rows():
    summary_db = DBSequence(
        [
            QueryStub(scalar_value=500),
            QueryStub(scalar_value=7),
        ]
    )
    top_db = DBSequence(
        [
            QueryStub(
                all_value=[
                    SimpleNamespace(
                        id="user-1",
                        display_name="Top User",
                        email="top@example.com",
                        total_points=900,
                    )
                ]
            )
        ]
    )
    tx_db = DBSequence(
        [
            QueryStub(
                all_value=[
                    SimpleNamespace(
                        id="tx-1",
                        order_id="order-1",
                        display_name=None,
                        email="guest@example.com",
                        points=20,
                        created_at=datetime(2026, 3, 27, 9, 0, 0),
                    )
                ]
            )
        ]
    )

    assert point_summary(db=summary_db, current_user=owner_user()) == {
        "total_points_issued": 500,
        "total_customers_with_points": 7,
    }
    assert top_customers_by_points(db=top_db, current_user=owner_user()) == [
        {"user_id": "user-1", "name": "Top User", "total_points": 900}
    ]
    assert point_transactions(db=tx_db, current_user=owner_user()) == [
        {
            "transaction_id": "tx-1",
            "order_id": "order-1",
            "customer": "guest@example.com",
            "points": 20,
            "created_at": "2026-03-27T09:00:00",
        }
    ]


def test_review_dashboard_endpoints_transform_rows():
    summary_db = DBSequence(
        [
            QueryStub(count_value=12),
            QueryStub(scalar_value=4.126),
            QueryStub(scalar_value=2),
        ]
    )
    list_db = DBSequence(
        [
            QueryStub(
                all_value=[
                    SimpleNamespace(
                        id="review-1",
                        menu_name="Pho",
                        rating=5,
                        comment="great",
                        created_at=datetime(2026, 3, 27, 8, 30, 0),
                    )
                ]
            )
        ]
    )
    by_menu_db = DBSequence(
        [
            QueryStub(
                all_value=[
                    SimpleNamespace(
                        menu_item_id="menu-1",
                        name="Pho",
                        total_reviews=4,
                        avg_rating=4.75,
                    )
                ]
            )
        ]
    )

    assert review_summary(db=summary_db, current_user=owner_user()) == {
        "total_reviews": 12,
        "avg_rating": 4.13,
        "bad_reviews": 2,
    }
    assert list_reviews(
        rating=5,
        menu_item_id="menu-1",
        from_date="2026-03-01",
        to_date="2026-03-31",
        db=list_db,
        current_user=owner_user(),
    ) == [
        {
            "review_id": "review-1",
            "menu_item": "Pho",
            "rating": 5,
            "comment": "great",
            "created_at": "2026-03-27T08:30:00",
        }
    ]
    assert reviews_by_menu(db=by_menu_db, current_user=owner_user()) == [
        {
            "menu_item_id": "menu-1",
            "menu_item": "Pho",
            "total_reviews": 4,
            "avg_rating": 4.75,
        }
    ]


def test_menu_analytics_endpoints_transform_rows():
    top_db = DBSequence(
        [
            QueryStub(
                all_value=[
                    SimpleNamespace(
                        menu_item_id="menu-1",
                        menu_name="Pho",
                        total_qty=8,
                        revenue=120.0,
                    )
                ]
            )
        ]
    )
    revenue_db = DBSequence(
        [
            QueryStub(all_value=[SimpleNamespace(menu_name="Tea", revenue=22.5)])
        ]
    )
    trend_db = DBSequence(
        [
            QueryStub(
                all_value=[
                    SimpleNamespace(day=datetime(2026, 3, 27, 0, 0, 0), sold_qty=6)
                ]
            )
        ]
    )

    assert top_menu_items(db=top_db, current_user=owner_user()) == [
        {
            "menu_item_id": "menu-1",
            "name": "Pho",
            "sold_qty": 8,
            "revenue": 120.0,
        }
    ]
    assert menu_revenue(db=revenue_db, current_user=owner_user()) == [
        {"name": "Tea", "revenue": 22.5}
    ]
    assert menu_trends(
        menu_item_id="menu-1",
        db=trend_db,
        current_user=owner_user(),
    ) == [{"date": "2026-03-27", "sold_qty": 6}]


def test_build_overview_returns_chart_and_summary():
    db = DBSequence(
        [
            QueryStub(
                all_value=[
                    SimpleNamespace(
                        time=datetime(2026, 3, 27, 9, 0, 0),
                        total_revenue=350.0,
                        total_orders=3,
                    )
                ]
            ),
            QueryStub(one_value=(500.0, 4)),
            QueryStub(count_value=2),
            QueryStub(scalar_value=40),
        ]
    )

    result = build_overview(db, restaurant_id=123)

    assert result["chart"] == [
        {
            "time": "2026-03-27T09:00:00",
            "total_revenue": 350.0,
            "total_orders": 3,
        }
    ]
    assert result["summary"] == {
        "total_revenue": 500.0,
        "total_orders": 4,
        "returning_customers": 2,
        "total_points_issued": 40,
    }


def test_cached_overview_uses_sessionlocal_and_closes(monkeypatch):
    calls = []
    closed = []

    class SessionFactory:
        def __call__(self):
            return SimpleNamespace(close=lambda: closed.append(True))

    def fake_build_overview(db, restaurant_id):
        calls.append((db, restaurant_id))
        return {"restaurant_id": restaurant_id}

    monkeypatch.setattr("controllers.report_controller.build_overview", fake_build_overview)
    monkeypatch.setattr("db.database.SessionLocal", SessionFactory())
    cached_overview.cache_clear()

    result = cached_overview(99, 1)

    assert result == {"restaurant_id": 99}
    assert calls and calls[0][1] == 99
    assert closed == [True]


def test_overview_report_handles_options_and_cached_path(monkeypatch):
    user = owner_user()
    monkeypatch.setattr("controllers.report_controller.cached_overview", lambda *args: {"ok": True})

    assert overview_report(SimpleNamespace(method="OPTIONS"), current_user=user) == {}
    assert overview_report(SimpleNamespace(method="GET"), current_user=user) == {"ok": True}
