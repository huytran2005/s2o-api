from datetime import datetime
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException, Response, UploadFile

from controllers.menu_item_controller import (
    create_menu,
    create_menu_with_image,
    delete_menu,
    filter_menu_items_by_price,
    get_menu_detail,
    list_menus_guest,
    search_menu_items_by_name,
    update_menu_image,
)
from controllers.restaurant_controller import (
    create_restaurant,
    delete_restaurant,
    get_restaurant,
    list_restaurants,
    update_preview_image,
    update_restaurant,
)
from controllers.table_controller import (
    create_table,
    delete_table,
    get_all_tables,
    get_table_by_id,
    update_table,
)
from schemas.menu_schema import MenuCreate
from schemas.restaurant_schema import RestaurantCreate, RestaurantUpdate
from schemas.table_schema import TableCreate, TableUpdate


class QueryStub:
    def __init__(self, first_value=None, all_value=None):
        self.first_value = first_value
        self.all_value = list(all_value or [])
        self.deleted = False

    def filter(self, *args, **kwargs):
        return self

    def filter_by(self, *args, **kwargs):
        return self

    def outerjoin(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def subquery(self):
        return "subquery"

    def first(self):
        return self.first_value

    def all(self):
        return list(self.all_value)

    def delete(self, *args, **kwargs):
        self.deleted = True
        return 1


class DBSequence:
    def __init__(self, queries):
        self.queries = list(queries)
        self.added = []
        self.deleted = []
        self.committed = 0
        self.refreshed = []
        self.flush_called = False

    def query(self, *args, **kwargs):
        return self.queries.pop(0)

    def add(self, instance):
        if getattr(instance, "id", None) is None:
            instance.id = uuid4()
        if getattr(instance, "created_at", None) is None:
            instance.created_at = datetime(2026, 3, 27, 10, 0, 0)
        self.added.append(instance)

    def delete(self, instance):
        self.deleted.append(instance)

    def commit(self):
        self.committed += 1

    def refresh(self, instance):
        self.refreshed.append(instance)

    def flush(self):
        self.flush_called = True


class AsyncRedisStub:
    def __init__(self, get_value=None):
        self.get_value = get_value
        self.setex_calls = []

    async def get(self, key):
        import asyncio

        await asyncio.sleep(0)
        return self.get_value

    async def setex(self, key, ttl, value):
        import asyncio

        await asyncio.sleep(0)
        self.setex_calls.append((key, ttl, value))

    def delete(self, key):
        self.setex_calls.append(("delete", key))


class BrokenRedisGetStub:
    async def get(self, key):
        raise RuntimeError("redis down")

    async def setex(self, key, ttl, value):
        raise RuntimeError("unused")

    def delete(self, key):
        raise RuntimeError("unused")


class BrokenRedisDeleteStub:
    async def get(self, key):
        return None

    async def setex(self, key, ttl, value):
        return None

    def delete(self, key):
        raise RuntimeError("redis delete failed")


def owner_user():
    return SimpleNamespace(id=uuid4(), role="owner")


def staff_user():
    return SimpleNamespace(id=uuid4(), role="staff", restaurant_id=uuid4())


def test_restaurant_controller_crud(monkeypatch, tmp_path):
    user = owner_user()
    existing = SimpleNamespace(id=uuid4(), name="R1", description="Old", owner_id=user.id, image_preview=None)
    db = DBSequence([QueryStub(all_value=[existing])])
    assert list_restaurants(db=db, current_user=user) == [existing]

    db = DBSequence([])
    created = create_restaurant(
        RestaurantCreate(name="R1", description="Desc"),
        db=db,
        current_user=user,
    )
    assert created.name == "R1"
    assert db.committed == 1

    redis = AsyncRedisStub()
    restaurant = SimpleNamespace(
        id=uuid4(),
        name="R2",
        description="Desc",
        image_preview="/media/restaurants/preview.png",
    )
    db = DBSequence([QueryStub(first_value=restaurant)])
    response = Response()
    monkeypatch.setattr("controllers.restaurant_controller.redis_client", redis)
    import asyncio
    result = asyncio.run(get_restaurant(restaurant.id, response=response, db=db))
    assert result["name"] == "R2"
    assert response.headers["X-Cache"] == "MISS"

    with pytest.raises(HTTPException):
        asyncio.run(get_restaurant(uuid4(), response=Response(), db=DBSequence([QueryStub(first_value=None)])))

    db = DBSequence([QueryStub(first_value=existing)])
    updated = update_restaurant(
        existing.id,
        RestaurantUpdate(name="Renamed"),
        db=db,
        current_user=user,
    )
    assert updated.name == "Renamed"

    old_file = tmp_path / "old.png"
    old_file.write_bytes(b"old")
    restaurant.image_preview = str(old_file)
    db = DBSequence([QueryStub(first_value=restaurant)])
    monkeypatch.setattr("controllers.restaurant_controller.save_restaurant_image", lambda image: "/media/restaurants/new.png")
    upload = UploadFile(filename="preview.png", file=BytesIO(b"new"))
    result = update_preview_image(restaurant.id, image=upload, db=db, current_user=user)
    assert result == {"image_preview": "/media/restaurants/new.png"}

    old_file.write_bytes(b"old")
    restaurant.image_preview = str(old_file)
    monkeypatch.setattr("controllers.restaurant_controller.os.remove", lambda path: None)
    db = DBSequence([QueryStub(first_value=restaurant)])
    result = update_preview_image(restaurant.id, image=upload, db=db, current_user=user)
    assert result["image_preview"] == "/media/restaurants/new.png"

    old_file.write_bytes(b"old")
    restaurant.image_preview = str(old_file)
    monkeypatch.setattr(
        "controllers.restaurant_controller.os.remove",
        lambda path: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    db = DBSequence([QueryStub(first_value=restaurant)])
    result = update_preview_image(restaurant.id, image=upload, db=db, current_user=user)
    assert result["image_preview"] == "/media/restaurants/new.png"

    to_delete = SimpleNamespace(id=uuid4(), image_preview=str(tmp_path / "delete.png"))
    Path(to_delete.image_preview).write_bytes(b"x")
    admin = SimpleNamespace(id=uuid4(), role="admin")
    db = DBSequence([QueryStub(first_value=to_delete)])
    result = delete_restaurant(to_delete.id, db=db, current_user=admin)
    assert result == {"message": "Restaurant deleted"}
    assert db.deleted == [to_delete]

    delete_with_image = SimpleNamespace(id=uuid4(), image_preview=str(tmp_path / "delete-2.png"))
    Path(delete_with_image.image_preview).write_bytes(b"x")
    db = DBSequence([QueryStub(first_value=delete_with_image)])
    monkeypatch.setattr("controllers.restaurant_controller.os.remove", lambda path: (_ for _ in ()).throw(RuntimeError("boom")))
    result = delete_restaurant(delete_with_image.id, db=db, current_user=admin)
    assert result == {"message": "Restaurant deleted"}

    with pytest.raises(HTTPException):
        update_preview_image(uuid4(), image=upload, db=DBSequence([QueryStub(first_value=None)]), current_user=user)

    with pytest.raises(HTTPException):
        delete_restaurant(uuid4(), db=DBSequence([QueryStub(first_value=None)]), current_user=admin)

    with pytest.raises(HTTPException):
        create_restaurant(
            RestaurantCreate(name="Nope", description="Denied"),
            db=DBSequence([]),
            current_user=SimpleNamespace(id=uuid4(), role="customer"),
        )


def test_restaurant_get_uses_cache_when_available(monkeypatch):
    cached = AsyncRedisStub(get_value='{"id":"1","name":"Cached","description":null,"image_preview":null}')
    monkeypatch.setattr("controllers.restaurant_controller.redis_client", cached)
    response = Response()

    import asyncio

    result = asyncio.run(get_restaurant(uuid4(), response=response, db=DBSequence([])))

    assert result["name"] == "Cached"
    assert response.headers["X-Cache"] == "HIT"


def test_menu_controller_paths(monkeypatch, tmp_path):
    user = staff_user()
    restaurant_id = uuid4()
    category_id = uuid4()
    menu = SimpleNamespace(
        id=uuid4(),
        restaurant_id=restaurant_id,
        category_id=category_id,
        name="Pho",
        description="Hot",
        price=Decimal("12.5"),
        image_url="/media/menus/pho.png",
        is_available=True,
        category=SimpleNamespace(id=category_id, name="Main"),
    )

    assert search_menu_items_by_name("pho", db=DBSequence([QueryStub(all_value=[menu])])) == [menu]
    assert filter_menu_items_by_price(
        min_price=Decimal("1"),
        max_price=Decimal("20"),
        db=DBSequence([QueryStub(all_value=[menu])]),
    ) == [menu]
    assert filter_menu_items_by_price(min_price=Decimal("1"), db=DBSequence([QueryStub(all_value=[menu])])) == [menu]
    assert filter_menu_items_by_price(max_price=Decimal("20"), db=DBSequence([QueryStub(all_value=[menu])])) == [menu]
    assert filter_menu_items_by_price(db=DBSequence([QueryStub(all_value=[menu])])) == [menu]

    db = DBSequence([])
    created = create_menu(
        restaurant_id=restaurant_id,
        data=MenuCreate(name="Tea", price=Decimal("2.5"), category_id=category_id),
        db=db,
        current_user=user,
    )
    assert created.name == "Tea"

    with pytest.raises(HTTPException):
        create_menu(
            restaurant_id=restaurant_id,
            data=MenuCreate(name="Denied", price=Decimal("2.5"), category_id=category_id),
            db=DBSequence([]),
            current_user=SimpleNamespace(id=uuid4(), role="customer"),
        )

    redis = AsyncRedisStub()
    monkeypatch.setattr("controllers.menu_item_controller.redis_client", redis)
    response = Response()
    import asyncio
    result = asyncio.run(list_menus_guest(restaurant_id, response=response, db=DBSequence([QueryStub(all_value=[menu])])))
    assert result[0]["category_name"] == "Main"
    assert response.headers["X-Cache"] == "MISS"

    cached_redis = AsyncRedisStub(
        get_value='[{"id":"1","name":"Cached","price":"9.0","image_url":null,"is_available":true,"category_id":null,"category_name":null}]'
    )
    monkeypatch.setattr("controllers.menu_item_controller.redis_client", cached_redis)
    response = Response()
    result = asyncio.run(list_menus_guest(restaurant_id, response=response, db=DBSequence([])))
    assert result[0]["name"] == "Cached"
    assert response.headers["X-Cache"] == "HIT"

    monkeypatch.setattr("controllers.menu_item_controller.redis_client", BrokenRedisGetStub())
    response = Response()
    result = asyncio.run(list_menus_guest(restaurant_id, response=response, db=DBSequence([QueryStub(all_value=[menu])])))
    assert result[0]["name"] == "Pho"
    assert response.headers.get("X-Cache") is None

    monkeypatch.setattr("controllers.menu_item_controller.redis_client", BrokenRedisDeleteStub())
    response = Response()
    result = asyncio.run(list_menus_guest(restaurant_id, response=response, db=DBSequence([QueryStub(all_value=[menu])]), category_id=category_id))
    assert result[0]["category_id"] == category_id

    detail = get_menu_detail(menu.id, db=DBSequence([QueryStub(first_value=menu)]))
    assert detail.name == "Pho"

    with pytest.raises(HTTPException):
        get_menu_detail(uuid4(), db=DBSequence([QueryStub(first_value=None)]))

    monkeypatch.setattr("controllers.menu_item_controller.save_menu_image", lambda image: "/media/menus/new.png")
    upload = UploadFile(filename="menu.png", file=BytesIO(b"img"))
    db = DBSequence([])
    created_with_image = create_menu_with_image(
        restaurant_id=restaurant_id,
        name="Cake",
        category_id=category_id,
        price=Decimal("5.0"),
        description="Sweet",
        image=upload,
        db=db,
        current_user=user,
    )
    assert created_with_image.image_url == "/media/menus/new.png"

    old_image = tmp_path / "pho.png"
    old_image.write_bytes(b"old")
    menu.image_url = "/media/" + old_image.name
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("controllers.menu_item_controller.save_menu_image", lambda image: "/media/menus/updated.png")
    monkeypatch.setattr("controllers.menu_item_controller.redis_client", AsyncRedisStub())
    updated = update_menu_image(menu.id, image=upload, db=DBSequence([QueryStub(first_value=menu)]), current_user=user)
    assert updated.image_url == "/media/menus/updated.png"

    old_path = tmp_path / "old-menu.png"
    old_path.write_bytes(b"old")
    menu.image_url = "/media/" + old_path.name
    monkeypatch.setattr("controllers.menu_item_controller.os.remove", lambda path: None)
    updated = update_menu_image(menu.id, image=upload, db=DBSequence([QueryStub(first_value=menu)]), current_user=user)
    assert updated.image_url == "/media/menus/updated.png"

    monkeypatch.setattr("controllers.menu_item_controller.os.remove", lambda path: (_ for _ in ()).throw(RuntimeError("boom")))
    updated = update_menu_image(menu.id, image=upload, db=DBSequence([QueryStub(first_value=menu)]), current_user=user)
    assert updated.image_url == "/media/menus/updated.png"

    with pytest.raises(HTTPException):
        update_menu_image(uuid4(), image=upload, db=DBSequence([QueryStub(first_value=None)]), current_user=user)

    delete_target = SimpleNamespace(
        id=uuid4(),
        restaurant_id=restaurant_id,
        category_id=category_id,
        image_url="/media/to-delete.png",
    )
    delete_file = tmp_path / "media" / "to-delete.png"
    delete_file.parent.mkdir(parents=True, exist_ok=True)
    delete_file.write_bytes(b"x")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("controllers.menu_item_controller.redis_client", AsyncRedisStub())
    response = delete_menu(delete_target.id, db=DBSequence([QueryStub(first_value=delete_target)]), current_user=user)
    assert response.status_code == 204

    delete_target2 = SimpleNamespace(
        id=uuid4(),
        restaurant_id=restaurant_id,
        category_id=None,
        image_url="/media/to-delete-2.png",
    )
    (tmp_path / "media").mkdir(exist_ok=True)
    (tmp_path / "media" / "to-delete-2.png").write_bytes(b"x")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("controllers.menu_item_controller.os.remove", lambda path: None)
    monkeypatch.setattr("controllers.menu_item_controller.redis_client", BrokenRedisDeleteStub())
    response = delete_menu(delete_target2.id, db=DBSequence([QueryStub(first_value=delete_target2)]), current_user=user)
    assert response.status_code == 204

    delete_target3 = SimpleNamespace(
        id=uuid4(),
        restaurant_id=restaurant_id,
        category_id=category_id,
        image_url="/media/to-delete-3.png",
    )
    (tmp_path / "media" / "to-delete-3.png").write_bytes(b"x")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("controllers.menu_item_controller.os.remove", lambda path: (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setattr("controllers.menu_item_controller.redis_client", AsyncRedisStub())
    response = delete_menu(delete_target3.id, db=DBSequence([QueryStub(first_value=delete_target3)]), current_user=user)
    assert response.status_code == 204

    with pytest.raises(HTTPException):
        delete_menu(uuid4(), db=DBSequence([QueryStub(first_value=None)]), current_user=user)

    with pytest.raises(HTTPException):
        get_menu_detail(uuid4(), db=DBSequence([QueryStub(first_value=None)]))


def test_table_controller_paths(monkeypatch, tmp_path):
    table_id = uuid4()
    restaurant_id = uuid4()
    table = SimpleNamespace(
        id=table_id,
        restaurant_id=restaurant_id,
        name="A1",
        seats=4,
        status="active",
        created_at=datetime(2026, 3, 27, 9, 0, 0),
    )

    class QRImage:
        def save(self, path, scale, border):
            Path(path).write_bytes(b"png")

    monkeypatch.setattr("controllers.table_controller.segno.make", lambda url: QRImage())
    monkeypatch.setattr("controllers.table_controller.QR_DIR", tmp_path / "qrs")
    db = DBSequence([QueryStub(first_value=None)])
    created = create_table(TableCreate(restaurant_id=restaurant_id, name="A1", seats=4), db=db)
    assert created.name == "A1"
    assert db.committed >= 3

    with pytest.raises(HTTPException):
        create_table(TableCreate(restaurant_id=restaurant_id, name="A1", seats=4), db=DBSequence([QueryStub(first_value=table)]))

    assert get_table_by_id(table_id, db=DBSequence([QueryStub(first_value=table)])) is table
    assert get_all_tables(db=DBSequence([QueryStub(all_value=[table])])) == [table]

    with pytest.raises(HTTPException):
        get_table_by_id(uuid4(), db=DBSequence([QueryStub(first_value=None)]))

    db = DBSequence([QueryStub(first_value=table), QueryStub(first_value=None)])
    updated = update_table(table_id, TableUpdate(name="A2", seats=6), db=db)
    assert updated.name == "A2"
    assert updated.seats == 6

    same_name_table = SimpleNamespace(
        id=table_id,
        restaurant_id=restaurant_id,
        name="A1",
        seats=4,
        status="active",
        created_at=datetime(2026, 3, 27, 9, 0, 0),
    )
    db = DBSequence([QueryStub(first_value=same_name_table)])
    updated = update_table(table_id, TableUpdate(name="A1"), db=db)
    assert updated.name == "A1"

    db = DBSequence([QueryStub(first_value=table)])
    updated = update_table(table_id, TableUpdate(seats=8), db=db)
    assert updated.seats == 8

    duplicate_db = DBSequence([QueryStub(first_value=table), QueryStub(first_value=object())])
    with pytest.raises(HTTPException):
        update_table(table_id, TableUpdate(name="A3"), db=duplicate_db)

    with pytest.raises(HTTPException):
        update_table(uuid4(), TableUpdate(name="A3"), db=DBSequence([QueryStub(first_value=None)]))

    q1 = QueryStub(first_value=table)
    q2 = QueryStub()
    q3 = QueryStub()
    q4 = QueryStub()
    db = DBSequence([q1, q2, q3, q4])
    qr_file = tmp_path / "qrs" / f"table-{table_id}.png"
    qr_file.parent.mkdir(parents=True, exist_ok=True)
    qr_file.write_bytes(b"png")
    monkeypatch.chdir(tmp_path)

    class DummyColumn:
        def in_(self, value):
            return value

        def __eq__(self, other):
            return other

    monkeypatch.setattr(
        "controllers.table_controller.GuestSession",
        SimpleNamespace(qr_id=DummyColumn()),
    )
    monkeypatch.setattr(
        "controllers.table_controller.QRCode",
        SimpleNamespace(id=DummyColumn(), table_id=DummyColumn()),
    )
    delete_table(table_id, db=db, current_user=staff_user())
    assert db.deleted == [table]

    qr_on_disk = tmp_path / "media" / "qrs" / f"table-{table_id}.png"
    qr_on_disk.parent.mkdir(parents=True, exist_ok=True)
    qr_on_disk.write_bytes(b"png")
    monkeypatch.chdir(tmp_path)
    db = DBSequence([QueryStub(first_value=table), QueryStub(), QueryStub(), QueryStub()])
    delete_table(table_id, db=db, current_user=staff_user())
    assert db.deleted == [table]

    with pytest.raises(HTTPException):
        delete_table(uuid4(), db=DBSequence([QueryStub(first_value=None)]), current_user=staff_user())
