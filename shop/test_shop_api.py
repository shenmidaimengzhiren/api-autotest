"""
商城接口测试用例 —— 按模块组织，正向 + 反向 + 鉴权 + 越权

用例分层原则：这里只写"验证什么"，不写"怎么发请求"（封装在 conftest/app）。
每个用例 = 三段式：准备数据 → 调接口 → 断言。
"""

import secrets

import pytest

# ---------------- 通用小工具（测试内部的封装） ----------------


def register(client, username, password="pass123456"):
    return client.post("/api/register", json={
        "username": username, "password": password})


def login(client, username, password="pass123456"):
    resp = client.post("/api/login", json={
        "username": username, "password": password})
    assert resp.status_code == 200, f"登录失败: {resp.get_json()}"
    return resp.get_json()["data"]["token"]


def new_user(client):
    """造一个随机用户并登录，返回 (token, username)。
    随机用户名保证多条用例之间互不干扰（幂等）。"""
    username = "user_" + secrets.token_hex(4)
    register(client, username)
    token = login(client, username)
    return token, username


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# ================= 注册模块 =================


class TestRegister:

    def test_register_success(self, client):
        """正向：注册成功，返回 201 和赠送余额"""
        username = "user_" + secrets.token_hex(4)
        resp = register(client, username)

        assert resp.status_code == 201
        body = resp.get_json()
        assert body["message"] == "注册成功"
        assert body["data"]["username"] == username
        assert body["data"]["balance"] == 1000  # 新用户送 1000

    def test_register_missing_password(self, client):
        """反向：密码缺失 → 400"""
        resp = register(client, "user_" + secrets.token_hex(4), password=None)
        assert resp.status_code == 400
        assert "不能为空" in resp.get_json()["message"]

    def test_register_duplicate_username(self, client):
        """反向：重复注册 → 409"""
        username = "user_" + secrets.token_hex(4)
        register(client, username)              # 第一次注册
        resp = register(client, username)       # 第二次同名注册
        assert resp.status_code == 409
        assert "已存在" in resp.get_json()["message"]


# ================= 登录模块 =================


class TestLogin:

    def test_login_success(self, client):
        """正向：登录成功，拿到 token"""
        username = "user_" + secrets.token_hex(4)
        register(client, username)

        resp = client.post("/api/login", json={
            "username": username, "password": "pass123456"})
        assert resp.status_code == 200
        token = resp.get_json()["data"]["token"]
        assert isinstance(token, str) and len(token) == 32  # token_hex(16) => 32 字符

    @pytest.mark.parametrize("bad_username,bad_password,scene", [
        ("{username}", "wrongpass", "密码错误"),
        ("no_such_user_xyz", "pass123456", "用户不存在"),
    ])
    def test_login_failure(self, client, bad_username, bad_password, scene):
        """反向参数化：密码错误 / 用户不存在 → 401"""
        username = "user_" + secrets.token_hex(4)
        register(client, username)
        # {username} 占位符替换成真实用户名，密码保持错误
        used_name = bad_username.replace("{username}", username)

        resp = client.post("/api/login", json={
            "username": used_name, "password": bad_password})
        assert resp.status_code == 401, f"场景[{scene}] 应返回 401"
        assert "错误" in resp.get_json()["message"]


# ================= 商品模块 =================


class TestProducts:

    def test_product_list(self, client):
        """正向：商品列表 200，包含 3 个预置商品"""
        resp = client.get("/api/products")
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert len(data) == 3
        ids = {p["id"] for p in data}
        assert ids == {1, 2, 3}
        # 2 号商品是故意设置的缺货商品，库存为 0
        product2 = next(p for p in data if p["id"] == 2)
        assert product2["stock"] == 0


# ================= 下单模块 =================


class TestCreateOrder:

    def test_order_success(self, auth):
        """正向：下单成功，库存扣减、余额扣减（联动校验）"""
        client, token, username = auth
        headers = auth_header(token)

        # 下单前余额
        balance_before = client.get("/api/me", headers=headers).get_json()["data"]["balance"]

        resp = client.post("/api/orders", headers=headers, json={
            "product_id": 1, "qty": 1})  # 机械键盘 299 元
        assert resp.status_code == 201
        order = resp.get_json()["data"]
        assert order["amount"] == 299
        assert order["status"] == "已支付"

        # 联动断言 1：余额减少 299
        balance_after = client.get("/api/me", headers=headers).get_json()["data"]["balance"]
        assert balance_after == balance_before - 299

        # 联动断言 2：库存从 10 变 9
        product1 = next(p for p in client.get("/api/products").get_json()["data"]
                        if p["id"] == 1)
        assert product1["stock"] == 9

    def test_order_insufficient_balance(self, auth):
        """反向：余额不足（999 x 2 = 1998 > 赠送的 1000）→ 409"""
        client, token, _ = auth
        resp = client.post("/api/orders", headers=auth_header(token), json={
            "product_id": 3, "qty": 2})
        assert resp.status_code == 409
        assert "余额不足" in resp.get_json()["message"]

    def test_order_out_of_stock(self, auth):
        """反向：缺货商品（2 号商品库存 0）→ 409"""
        client, token, _ = auth
        resp = client.post("/api/orders", headers=auth_header(token), json={
            "product_id": 2, "qty": 1})
        assert resp.status_code == 409
        assert "库存不足" in resp.get_json()["message"]

    def test_order_product_not_exist(self, auth):
        """反向：商品不存在 → 404"""
        client, token, _ = auth
        resp = client.post("/api/orders", headers=auth_header(token), json={
            "product_id": 9999, "qty": 1})
        assert resp.status_code == 404

    def test_order_invalid_qty(self, auth):
        """反向：数量为 0 → 400"""
        client, token, _ = auth
        resp = client.post("/api/orders", headers=auth_header(token), json={
            "product_id": 1, "qty": 0})
        assert resp.status_code == 400

    @pytest.mark.parametrize("headers_desc,headers", [
        ("不带 token", {}),
        ("伪造 token", {"Authorization": "Bearer " + "f" * 32}),
        ("格式错误", {"Authorization": "abc123"}),
    ])
    def test_order_without_valid_token(self, client, headers_desc, headers):
        """反向参数化：无 token / 假 token / 格式错 → 一律 401"""
        resp = client.post("/api/orders", headers=headers, json={
            "product_id": 1, "qty": 1})
        assert resp.status_code == 401, f"场景[{headers_desc}] 应返回 401"


# ================= 订单查询模块 =================


class TestGetOrder:

    def test_get_own_order(self, auth):
        """正向：下单后能查到自己的订单，字段一致"""
        client, token, username = auth
        headers = auth_header(token)

        create = client.post("/api/orders", headers=headers, json={
            "product_id": 1, "qty": 2})
        order_id = create.get_json()["data"]["order_id"]

        resp = client.get(f"/api/orders/{order_id}", headers=headers)
        assert resp.status_code == 200
        order = resp.get_json()["data"]
        assert order["order_id"] == order_id
        assert order["username"] == username
        assert order["qty"] == 2
        assert order["amount"] == 299 * 2

    def test_get_order_of_other_user_forbidden(self, client):
        """安全测试：用户 B 查用户 A 的订单 → 403 越权"""
        token_a, _ = new_user(client)   # 用户 A 下单
        headers_a = auth_header(token_a)
        create = client.post("/api/orders", headers=headers_a, json={
            "product_id": 1, "qty": 1})
        order_id = create.get_json()["data"]["order_id"]

        token_b, _ = new_user(client)   # 用户 B 尝试查看
        resp = client.get(f"/api/orders/{order_id}", headers=auth_header(token_b))
        assert resp.status_code == 403
        assert "无权" in resp.get_json()["message"]

    def test_get_order_not_exist(self, auth):
        """反向：订单号不存在 → 404"""
        client, token, _ = auth
        resp = client.get("/api/orders/ORDNOTEXIST123", headers=auth_header(token))
        assert resp.status_code == 404
