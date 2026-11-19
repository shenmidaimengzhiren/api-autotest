"""
模拟商城后端 —— 被测系统（Flask 实现）

这是"被测对象"，不是测试代码。测试代码在 test_shop_api.py。

业务规则（测试设计的依据）：
1. 注册：用户名+密码必填、不可重复注册，新用户送 1000 元余额
2. 登录：密码错误 / 用户不存在 → 401，成功返回 token
3. 下单：必须带 token；校验商品存在、库存充足、余额充足
4. 查订单：只能查自己的订单（越权 → 403）

真实项目里数据存数据库、token 用 JWT，这里用内存字典简化，
方便每次重启得到干净的测试数据。
"""

from flask import Flask, request, jsonify
import secrets

app = Flask(__name__)

# ---------------- 内存数据库 ----------------

users = {}     # 用户名 -> {"password": ..., "balance": 余额}
tokens = {}    # token -> 用户名（登录后发放）
orders = {}    # 订单号 -> 订单详情

INIT_BALANCE = 1000  # 新用户赠送余额

products = {  # 商品池（2 号故意 0 库存，供缺货场景测试）
    1: {"name": "机械键盘", "price": 299, "stock": 10},
    2: {"name": "无线鼠标", "price": 99, "stock": 0},
    3: {"name": "显示器", "price": 999, "stock": 5},
}


def _check_token():
    """从请求头取出 token 并校验。
    返回 (用户名, 错误响应)。校验通过时错误响应为 None。"""
    auth = request.headers.get("Authorization", "")
    # 约定格式: "Bearer <token>"
    token = auth.replace("Bearer ", "").strip()
    if not token or token not in tokens:
        return None, (jsonify({"code": 401, "message": "未登录或 token 无效"}), 401)
    return tokens[token], None


# ---------------- 接口定义 ----------------

@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"code": 400, "message": "用户名和密码不能为空"}), 400
    if username in users:
        return jsonify({"code": 409, "message": "用户名已存在"}), 409

    users[username] = {"password": password, "balance": INIT_BALANCE}
    return jsonify({
        "code": 201,
        "message": "注册成功",
        "data": {"username": username, "balance": INIT_BALANCE},
    }), 201


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    user = users.get(username)
    if user is None or user["password"] != password:
        return jsonify({"code": 401, "message": "用户名或密码错误"}), 401

    token = secrets.token_hex(16)  # 每次登录生成新 token
    tokens[token] = username
    return jsonify({"code": 200, "message": "登录成功", "data": {"token": token}})


@app.get("/api/products")
def product_list():
    data = [{"id": pid, **info} for pid, info in products.items()]
    return jsonify({"code": 200, "message": "ok", "data": data})


@app.get("/api/me")
def my_account():
    """查询当前登录用户的信息（含余额），供下单前后对比扣款"""
    username, err = _check_token()
    if err:
        return err
    user = users[username]
    return jsonify({"code": 200, "message": "ok",
                    "data": {"username": username, "balance": user["balance"]}})


@app.post("/api/orders")
def create_order():
    username, err = _check_token()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    qty = data.get("qty", 1)

    if not isinstance(qty, int) or qty < 1:
        return jsonify({"code": 400, "message": "购买数量必须为正整数"}), 400

    product = products.get(product_id)
    if product is None:
        return jsonify({"code": 404, "message": "商品不存在"}), 404
    if product["stock"] < qty:
        return jsonify({"code": 409, "message": "库存不足"}), 409

    amount = product["price"] * qty
    user = users[username]
    if user["balance"] < amount:
        return jsonify({"code": 409, "message": "余额不足"}), 409

    # 扣库存、扣余额、生成订单
    product["stock"] -= qty
    user["balance"] -= amount
    order_id = "ORD" + secrets.token_hex(4).upper()
    orders[order_id] = {
        "order_id": order_id,
        "username": username,
        "product_id": product_id,
        "qty": qty,
        "amount": amount,
        "status": "已支付",
    }
    return jsonify({"code": 201, "message": "下单成功", "data": orders[order_id]}), 201


@app.get("/api/orders/<order_id>")
def get_order(order_id):
    username, err = _check_token()
    if err:
        return err

    order = orders.get(order_id)
    if order is None:
        return jsonify({"code": 404, "message": "订单不存在"}), 404
    if order["username"] != username:
        # 越权访问：查别人的订单
        return jsonify({"code": 403, "message": "无权查看他人订单"}), 403
    return jsonify({"code": 200, "message": "ok", "data": order})


if __name__ == "__main__":
    app.run(debug=True)
