import pytest
from http import HTTPStatus
from datetime import datetime


@pytest.mark.parametrize("query_data, expected", [
    ({"page_number": 1, "page_size": 10}, {"status": HTTPStatus.OK, "length": 2}),
    ({"page_number": 1, "page_size": 10}, {"status": HTTPStatus.UNAUTHORIZED, "length": 0}),
    ({"page_number": 1, "page_size": 10}, {"status": HTTPStatus.NOT_FOUND, "length": 0}),
    ({"page_number": 2, "page_size": 10}, {"status": HTTPStatus.BAD_REQUEST, "length": 0}),
    ({"page_number": 0, "page_size": 10}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 0}),
    ({"page_number": -1, "page_size": 10}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 0}),
    ({"page_number": 1, "page_size": 101}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 0}),
    ({"page_number": 1, "page_size": -10}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 0}),
])
@pytest.mark.asyncio
async def test_get_all_books(make_get_request, create_user, create_book, check_cache, db_session, get_access_token, query_data, expected):
    path = "/books/"

    if expected["status"] == HTTPStatus.UNAUTHORIZED:
        body, status, _ = await make_get_request(path, query_data=query_data)
        assert status == expected["status"]
        return

    await create_user(email="user@test.com", password="password", username="testuser")
    access_token = await get_access_token("testuser", "password")
    headers = {"Authorization": f"Bearer {access_token}"}

    if expected["status"] == HTTPStatus.NOT_FOUND:
        body, status, _ = await make_get_request(path, query_data=query_data, headers=headers)
        assert status == expected["status"]
        return

    published_date_1 = datetime.strptime("2020-01-01", "%Y-%m-%d")
    published_date_2 = datetime.strptime("2021-01-01", "%Y-%m-%d")
    book1 = await create_book(title="Book 1", author="Author 1", published_date=published_date_1)
    book2 = await create_book(title="Book 2", author="Author 2", published_date=published_date_2)

    # Первый запрос - данные не должны быть в кеше, мы их получим из БД
    body, status, _ = await make_get_request(path, query_data=query_data, headers=headers)

    assert status == expected["status"]

    if status == HTTPStatus.OK:
        assert len(body["books"]) == expected["length"]

        # Проверка, что данные попали в кеш
        pagination = {
            "limit": query_data["page_size"],
            "offset": (query_data["page_number"] - 1) * query_data["page_size"],
        }
        cached_books = await check_cache(service_name="bookservice", method_name="get_all", **pagination)

        assert cached_books is not None

        # # Удаляем книги из базы данных, но проверяем, что данные по-прежнему возвращаются из кеша
        await db_session.delete(book1)
        await db_session.delete(book2)
        await db_session.commit()

        body, status, _ = await make_get_request(path, query_data=query_data, headers=headers)

        assert status == expected["status"]
        assert len(body["books"]) == expected["length"]


@pytest.mark.parametrize("book_uuid, expected", [
    ("empty", {"status": HTTPStatus.OK}),
    ("a3943358-5cd5-4ee5-b8ff-4d1b34b6764b", {"status": HTTPStatus.NOT_FOUND}),
    ("a3943358-5cd5-4ee5-b8ff-4d1b34b6764b", {"status": HTTPStatus.UNAUTHORIZED}),
    ("invalid uuid", {"status": HTTPStatus.UNPROCESSABLE_ENTITY}),
])
@pytest.mark.asyncio
async def test_get_book_by_uuid(make_get_request, create_user, create_book, check_cache, db_session, get_access_token, book_uuid, expected):
    if expected["status"] == HTTPStatus.UNAUTHORIZED:
        body, status, _ = await make_get_request(f"/books/{book_uuid}/")
        assert status == expected["status"]
        return

    await create_user(email="user@test.com", password="password", username="testuser")
    access_token = await get_access_token("testuser", "password")
    headers = {"Authorization": f"Bearer {access_token}"}

    published_date = datetime.strptime("2020-01-01", "%Y-%m-%d")
    book = await create_book(title="Book 1", author="Author 1", published_date=published_date)
    if book_uuid == "empty":
        book_uuid = str(book.uuid)

    path = f"/books/{book_uuid}/"
    body, status, _ = await make_get_request(path, headers=headers)

    assert status == expected["status"]

    if status == HTTPStatus.OK:
        assert body["uuid"] == str(book_uuid)

        # Проверка, что книга попала в кеш
        cached_books = await check_cache("bookservice", "get", str(book_uuid))
        assert cached_books is not None

        # Удаляем книгу из базы данных, но проверяем, что данные по-прежнему возвращаются из кеша
        await db_session.delete(book)
        await db_session.commit()

        body, status, _ = await make_get_request(path, headers=headers)

        assert status == HTTPStatus.OK
        assert body["uuid"] == str(book.uuid)

@pytest.mark.parametrize("book_data, expected", [
    ({"title": "New Book", "author": "Author", "published_date": "2022-01-01"}, {"status": HTTPStatus.OK, "user": "admin"}),
    ({"title": "New Book", "author": "Author", "published_date": "2022-01-01"}, {"status": HTTPStatus.UNAUTHORIZED, "user": "nobody"}),
    ({"title": "New Book", "author": "Author", "published_date": "2022-01-01"}, {"status": HTTPStatus.FORBIDDEN, "user": "simple_user"}),
    ({"title": "New Book", "author": "Author", "published_date": "2022-01-01"}, {"status": HTTPStatus.BAD_REQUEST, "user": "admin"}),
    ({"author": "Author",}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "user": "admin"}),
    ({"invalid book data": "anything"}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "user": "admin"}),
])
@pytest.mark.asyncio
async def test_create_book_as_admin(make_post_request, create_user, get_access_token, book_data, expected):
    if expected["status"] == HTTPStatus.UNAUTHORIZED and expected["user"] == "nobody":
        body, status, _ = await make_post_request("/books/", body=book_data)

        assert status == expected["status"]
        return

    if expected["status"] == HTTPStatus.FORBIDDEN and expected["user"] == "simple_user":
        await create_user(email="user@test.com", password="password", username="testuser")
        access_token = await get_access_token("testuser", "password")
        headers = {"Authorization": f"Bearer {access_token}"}

        body, status, _ = await make_post_request("/books/", body=book_data, headers=headers)

        assert status == expected["status"]
        return

    await create_user(email="admin@test.com", password="admin", username="adminuser", is_admin=True)
    access_token = await get_access_token("adminuser", "admin")
    headers = {"Authorization": f"Bearer {access_token}"}

    if expected["status"] == HTTPStatus.BAD_REQUEST:
        body, status, _ = await make_post_request("/books/", body=book_data, headers=headers)
        body, status, _ = await make_post_request("/books/", body=book_data, headers=headers)

        assert status == expected["status"]
        return

    body, status, _ = await make_post_request("/books/", body=book_data, headers=headers)

    assert status == expected["status"]

    if status == HTTPStatus.OK:
        assert body["title"] == "New Book"
        assert body["author"] == "Author"


@pytest.mark.parametrize("query_data, expected", [
    (
        {"book_uuid": "empty", "book_data": {"author": "Author", "published_date": "2022-01-01"}}, {"status": HTTPStatus.OK, "user": "admin"}
    ),
    (
        {"book_uuid": "empty", "book_data": {"author": "Author", "published_date": "2022-01-01"}}, {"status": HTTPStatus.UNAUTHORIZED, "user": "nobody"}
    ),
    (
        {"book_uuid": "empty", "book_data": {"author": "Author", "published_date": "2022-01-01"}}, {"status": HTTPStatus.FORBIDDEN, "user": "simple_user"}
    ),
    (
        {"book_uuid": "a3943358-5cd5-4ee5-b8ff-4d1b34b6764b", "book_data": {"author": "Author", "published_date": "2022-01-01"}}, {"status": HTTPStatus.NOT_FOUND, "user": "admin"}
    ),
    (
        {"book_uuid": "empty", "book_data": {"invalid_field": "anything", "published_date": "2022-01-01"}}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "user": "admin"}
    ),
    (
        {"book_uuid": "empty", "book_data": "invalid book data"}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "user": "admin"}
    ),
])
@pytest.mark.asyncio
async def test_update_book_as_admin(make_patch_request, create_user, get_access_token, create_book, query_data, expected):
    published_date = datetime.strptime("2020-01-01", "%Y-%m-%d")
    book = await create_book(title="Book 1", author="Author 1", published_date=published_date)
    book_uuid = query_data["book_uuid"]
    if book_uuid == "empty":
        book_uuid = str(book.uuid)
    book_title = book.title

    path = f"/books/{book_uuid}"

    if expected["status"] == HTTPStatus.UNAUTHORIZED and expected["user"] == "nobody":
        body, status, _ = await make_patch_request(path, body=query_data["book_data"])

        assert status == expected["status"]
        return

    if expected["status"] == HTTPStatus.FORBIDDEN and expected["user"] == "simple_user":
        await create_user(email="user@test.com", password="password", username="testuser")
        access_token = await get_access_token("testuser", "password")
        headers = {"Authorization": f"Bearer {access_token}"}

        body, status, _ = await make_patch_request(path, body=query_data["book_data"], headers=headers)

        assert status == expected["status"]
        return

    await create_user(email="admin@test.com", password="admin", username="adminuser", is_admin=True)
    access_token = await get_access_token("adminuser", "admin")
    headers = {"Authorization": f"Bearer {access_token}"}

    body, status, _ = await make_patch_request(path, body=query_data["book_data"], headers=headers)

    assert status == expected["status"]

    if status == HTTPStatus.OK:
        assert body["title"] == book_title
        assert body["author"] == query_data["book_data"]["author"]


@pytest.mark.parametrize("book_uuid, expected", [
    ("empty", {"status": HTTPStatus.OK, "user": "admin"}),
    ("a3943358-5cd5-4ee5-b8ff-4d1b34b6764b", {"status": HTTPStatus.NOT_FOUND, "user": "admin"}),
    ("empty", {"status": HTTPStatus.UNAUTHORIZED, "user": "nobody"}),
    ("empty", {"status": HTTPStatus.FORBIDDEN, "user": "simple_user"}),
    ("invalid uuid", {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "user": "admin"}),
])
@pytest.mark.asyncio
async def test_delete_book_as_admin(make_delete_request, create_user, get_access_token, create_book, book_uuid, expected):
    published_date = datetime.strptime("2020-01-01", "%Y-%m-%d")
    book = await create_book(title="Book 1", author="Author 1", published_date=published_date)
    if book_uuid == "empty":
        book_uuid = str(book.uuid)

    path = f"/books/{book_uuid}"

    if expected["status"] == HTTPStatus.UNAUTHORIZED and expected["user"] == "nobody":
        body, status, _ = await make_delete_request(path)

        assert status == expected["status"]
        return

    if expected["status"] == HTTPStatus.FORBIDDEN and expected["user"] == "simple_user":
        await create_user(email="user@test.com", password="password", username="testuser")
        access_token = await get_access_token("testuser", "password")
        headers = {"Authorization": f"Bearer {access_token}"}

        body, status, _ = await make_delete_request(path, headers=headers)

        assert status == expected["status"]
        return

    await create_user(email="admin@test.com", password="admin", username="adminuser", is_admin=True)
    access_token = await get_access_token("adminuser", "admin")
    headers = {"Authorization": f"Bearer {access_token}"}

    body, status, _ = await make_delete_request(path, headers=headers)

    assert status == expected["status"]

    if status == HTTPStatus.OK:
        assert body["code"] == HTTPStatus.OK
        assert body["details"] == "Book deleted successfully"
