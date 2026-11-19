# -*- coding: utf-8 -*-
# pytest 第 3 课：用例分层后的测试文件
#
# 变化对比（改写前 → 改写后）：
#   import requests                          ← 不需要了，请求细节在 api_github.py
#   requests.get("https://api.github.com/…") ← 换成 github.get_user("octocat")
#
# 现在这个文件只剩一件事：断言（验证什么），一行"怎么发请求"都没有
# pytest 的两条命名铁律不变：文件名和函数名都必须以 test_ 开头


# ────────────────────────────────────────────
# 测试 1：最简单的用例 —— 接口通不通
# 注意参数里的 github：不用 import，conftest.py 自动提供
# ────────────────────────────────────────────
def test_octocat_exists(github):
    resp = github.get_user("octocat")
    assert resp.status_code == 200


# ────────────────────────────────────────────
# 测试 2：字段断言 —— 返回的数据对不对
# 对应你在 Apifox 里配的：$.login 等于 octocat
# ────────────────────────────────────────────
def test_octocat_login(github):
    resp = github.get_user("octocat")
    data = resp.json()
    assert data["login"] == "octocat"


# ────────────────────────────────────────────
# 测试 3：异常用例 —— 不存在的用户必须返回 404
# 断言 404，所以接口"报错"反而是测试通过
# ────────────────────────────────────────────
def test_user_not_found(github):
    resp = github.get_user("thisuserdoesnotexist123abc")
    assert resp.status_code == 404
    assert resp.json()["message"] == "Not Found"
