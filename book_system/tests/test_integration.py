import pytest
import httpx

BASE_URL = "http://47.79.18.126:8000"

auth_headers = {}
book_id = 0

@pytest.mark.asyncio
async def test_1_register():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        payload = {
            "username": "pytest_user_001",
            "password": "test_password"
        }
        response = await client.post("/auth/register", json=payload)
        assert response.status_code in [200, 400]
        print("\n注册接口测试通过")

@pytest.mark.asyncio
async def test_2_login():
    global auth_headers
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        data = {
            "username": "pytest_user_001",
            "password": "test_password"
        }
        response = await client.post("/auth/login", data=data)
        assert response.status_code == 200

        token = response.json()["access_token"]
        assert token is not None

        auth_headers = {"Authorization": f"Bearer {token}"}
        print(f"\n登录成功，Token：{token[:10]}...")

@pytest.mark.asyncio
async def test_3_create_book():
    global book_id
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        payload = {
            "title": "Pytest自动化测试指南",
            "author": "测试",
            "price": 99.9,
            "description": "这是一本自动创建的书"
        }
        response = await client.post("/books/", json=payload, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()["data"]
        book_id = data["id"]
        assert data["title"] == "Pytest自动化测试指南"
        print(f"\n创建书籍成功，ID：{book_id}")

@pytest.mark.asyncio
async def test_4_borrow_book():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.patch(f"/books/{book_id}/borrow", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()["data"]
        assert data["is_borrowed"] == True
        print(f"\n借书成功，状态已变为：{data["is_borrowed"]}")

@pytest.mark.asyncio
async def test_5_return_book():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.patch(f"/books/{book_id}/return", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()["data"]
        assert data["is_borrowed"] == False
        print(f"还书成功，状态已变为：{data["is_borrowed"]}")