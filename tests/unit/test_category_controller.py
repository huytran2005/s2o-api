import uuid
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from controllers.category_controller import create_category, list_categories
from models.category import Category
from schemas.category_schema import CategoryCreate


class QueryStub:
    def __init__(self, first_value=None, all_value=None):
        self._first_value = first_value
        self._all_value = all_value or []

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return self._first_value

    def all(self):
        return self._all_value


class DBStub:
    def __init__(self, existing=None, listed=None):
        self.existing = existing
        self.listed = listed or []
        self.added = []
        self.committed = False
        self.refreshed = []

    def query(self, model):
        if model is Category and self.existing is not None:
            return QueryStub(first_value=self.existing)
        return QueryStub(all_value=self.listed)

    def add(self, instance):
        if getattr(instance, "id", None) is None:
            instance.id = uuid.uuid4()
        self.added.append(instance)

    def commit(self):
        self.committed = True

    def refresh(self, instance):
        self.refreshed.append(instance)


def test_create_category_trims_name_and_persists():
    db = DBStub(existing=None)
    user = SimpleNamespace(role="owner")

    result = create_category(
        restaurant_id=uuid.uuid4(),
        data=CategoryCreate(name="  Drinks  ", icon="cup"),
        db=db,
        current_user=user,
    )

    assert result.name == "Drinks"
    assert db.committed is True
    assert db.added


def test_create_category_rejects_duplicate_name():
    db = DBStub(existing=SimpleNamespace(id=uuid.uuid4()))
    user = SimpleNamespace(role="owner")

    with pytest.raises(HTTPException) as exc_info:
        create_category(
            restaurant_id=uuid.uuid4(),
            data=CategoryCreate(name="Drinks"),
            db=db,
            current_user=user,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Category already exists"


def test_list_categories_returns_ordered_collection():
    categories = [SimpleNamespace(name="Drinks"), SimpleNamespace(name="Food")]
    db = DBStub(listed=categories)

    result = list_categories(restaurant_id=uuid.uuid4(), db=db)

    assert result == categories
