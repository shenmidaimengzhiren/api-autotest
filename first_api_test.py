"""
第一个接口测试脚本
对应你在 Apifox 里做的：GitHub-查询用户信息
"""
import requests

# ① 发送请求（相当于 Apifox 里点「发送」）
url = "https://api.github.com/users/octocat"
resp = requests.get(url, timeout=10)

# ② 看响应（相当于 Apifox 下方的响应区）
print("状态码:", resp.status_code)
print("耗时:", round(resp.elapsed.total_seconds() * 1000), "ms")

data = resp.json()  # 把响应体解析成字典
print("login:", data["login"])
print("id:", data["id"])

# ③ 断言（相当于 Apifox 的「后置操作 → 断言」）
assert resp.status_code == 200, f"状态码不对，实际 {resp.status_code}"
assert data["login"] == "octocat", f"login 不对，实际 {data['login']}"

print("\n断言全部通过 ✅")
