# -*- coding: utf-8 -*-
# pytest 第 3 课（续）：参数化 + 分层
#   数据表留在测试文件里 —— 因为"测哪些数据"是用例层的事
#   发请求交给 github（来自 conftest.py 的 fixture）—— 因为"怎么发"是封装层的事
import pytest

# ────────────────────────────────────────────
# ① 数据表：每一行就是 CSV 里的一行，格式 (用户名, 期望状态码)
# ────────────────────────────────────────────
USERS = [
    ("octocat", 200),
    ("torvalds", 200),
    ("defunkt", 200),
    ("gaearon", 200),
    ("thisuserdoesnotexist123abc", 404),
]


# ────────────────────────────────────────────
# ② 用例：参数 fixture（github）和参数化变量（username…）可以混用
#    pytest 会把它们都注入进来
# ────────────────────────────────────────────
@pytest.mark.parametrize("username, expected_status", USERS)
def test_user_status(github, username, expected_status):
    resp = github.get_user(username)

    # 第一层：状态码对不对
    assert resp.status_code == expected_status

    # 第二层：只有成功的用例，才继续校验业务字段
    # 这样拆开写，断言失败时 pytest 能直接告诉你卡在哪一层
    if expected_status == 200:
        data = resp.json()
        assert data["login"] == username  # 返回的 login 必须和请求的一致
        assert data["id"] > 0             # id 必须是正数


# ────────────────────────────────────────────
# ③ 通用路径检查：用封装层的 get_endpoint()
# ────────────────────────────────────────────
PATHS = [
    ("/users/octocat", 200),
    ("/users/octocat/repos", 200),
    ("/users/thisuserdoesnotexist123abc/repos", 404),
    ("/nonexistent-endpoint", 404),
]


@pytest.mark.parametrize("path, expected_code", PATHS)
def test_endpoints(github, path, expected_code):
    resp = github.get_endpoint(path)
    assert resp.status_code == expected_code
