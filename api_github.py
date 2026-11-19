# -*- coding: utf-8 -*-
# ─────────────────────────────────────────────
# API 封装层：所有"怎么发请求"的细节都集中在这里
# 测试用例不许直接写 requests.get(...)，只能调用这里的函数
#
# 好处：换环境/改超时/加 header，只改这一个文件，200 条用例全部生效
# 类比 Apifox：这一层就是「接口管理」里的接口文档
# ─────────────────────────────────────────────
import requests
BASE_URL = "https://api.github.com"
TIMEOUT = 10  # 秒，超过就报错，防止接口卡死拖慢整套测试


def get_user(username):
    """GET /users/{username} —— 查询用户信息"""
    return requests.get(f"{BASE_URL}/users/{username}", timeout=TIMEOUT)


def get_user_repos(username):
    """GET /users/{username}/repos —— 查询用户的公开仓库列表"""
    return requests.get(f"{BASE_URL}/users/{username}/repos", timeout=TIMEOUT)


def get_endpoint(path):
    """GET 任意路径 —— 通用方法，给异常路径的用例用"""
    return requests.get(f"{BASE_URL}{path}", timeout=TIMEOUT)
