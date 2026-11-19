"""
pytest 公共配置（商城模块）

两个 fixture：
- client   : Flask 测试客户端，代替"启动真实服务 + 发 HTTP 请求"，
             用例直接调用接口，不占端口、不依赖网络，CI 里最稳定
- auth     : 一个"已注册并已登录"的用户，返回 (client, token, username)
"""

import sys
import os

# 保证能 import 同目录的 app.py
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from app import app


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture()
def auth(client):
    """注册 + 登录一个随机用户，返回 (client, token, username)"""
    import secrets
    username = "user_" + secrets.token_hex(4)
    password = "pass123456"

    resp = client.post("/api/register", json={
        "username": username, "password": password})
    assert resp.status_code == 201, "fixture 注册失败"

    resp = client.post("/api/login", json={
        "username": username, "password": password})
    assert resp.status_code == 200, "fixture 登录失败"
    token = resp.get_json()["data"]["token"]

    return client, token, username
