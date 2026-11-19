# 今日任务卡：Python 基础第 1 课（接口场景版）

> 日期：2026-11-18 下午　预计 90 分钟
> 前置：Python 3.15 已装好，`first_api_test.py` 已跑通
> 核心思路：**每学一个语法点，立刻套在 GitHub 接口上**，不背语法书

## 总览

| 练习 | 语法点 | 对应你已有的 Apifox 经验 | 时长 |
|---|---|---|---|
| 1 | 变量 + f-string 格式化 | 报告里的标题/耗时拼接 | 10 min |
| 2 | **字典（dict）** | JSON 响应体、`$.login` | 20 min |
| 3 | **列表（list）** | `$[0].name`、数组响应 | 15 min |
| 4 | for 循环 + requests | **CSV 数据驱动**（跑 3 轮） | 20 min |
| 5 | if/else 判断 | 断言通过/失败 | 15 min |
| 6 | 函数封装 | 接口定义一次、用例无限组合 | 15 min |

打开练习文件：`python练习_第1课.py`，按编号从上往下做，每做完一个就运行一次。

```bash
cd /d "C:\Users\ASUS\WorkBuddy\2026-10-28-09-36-05"
python python练习_第1课.py
```

---

## 必须建立的一个认知：JSON 就是字典和列表

你在 Apifox 里写的 JSONPath，翻译成 Python 就是：

| Apifox（JSONPath） | Python 代码 | 含义 |
|---|---|---|
| `$.login` | `data["login"]` | 取字典里的值 |
| `$[0].name` | `data[0]["name"]` | 取列表第 1 个元素，再取它的字段 |
| `$.args.name` | `data["args"]["name"]` | 字典套字典，一层层往里走 |

**接口测试的本质操作，就是从字典和列表里取值、比对值。** 把这两个练熟，接口自动化就通了。

---

## 验收标准

全部做完后，你应该能不看答案独立写出这段代码：

```python
def check_user(name):
    resp = requests.get(f"https://api.github.com/users/{name}", timeout=10)
    if resp.status_code == 200 and resp.json()["login"] == name:
        print(f"{name} ✅ 通过")
        return True
    print(f"{name} ❌ 失败，状态码 {resp.status_code}")
    return False

for user in ["octocat", "torvalds", "defunkt"]:
    check_user(user)
```

这段 12 行的代码 = 你在 Apifox 里配置的全部内容（接口 + 提取 + 断言 + 数据驱动）。

---

## 卡住了怎么办

| 报错 | 原因 |
|---|---|
| `SyntaxError` | 括号/引号/冒号没写全，看报错指向的行号 |
| `KeyError: 'xxx'` | 字典里没有这个 key，先 `print(data)` 看看有什么 |
| `IndentationError` | 缩进不对，Python 靠缩进区分代码块（统一用 4 个空格） |
| `TypeError` | 类型和运算不匹配，比如字符串和数字相加 |

报错信息**最后一行**最重要，把那行发我即可。

---

## 参考答案（做完再看）

练习 2：`print(user["id"])`、`user["site_admin"] = False`
练习 3：`users.append("gaearon")`、`print(users[0])`、`print(len(users))`
练习 4：

```python
for name in users:
    resp = requests.get(f"https://api.github.com/users/{name}", timeout=10)
    print(name, resp.status_code, resp.json()["public_repos"])
```

练习 5：

```python
if resp.status_code == 200:
    print("通过")
else:
    print(f"失败，状态码 {resp.status_code}")
```

练习 6：见上文「验收标准」。

---

## 完成记录（2026-11-19 实测通过）

6 个练习全部做完并跑通，终端实测输出：

```
octocat:   id=583231,  仓库 8 个
torvalds:  id=1024025, 仓库 12 个
defunkt:   id=2,       仓库 107 个
gaearon:   id=810438,  仓库 302 个
no_such_user_123abc:   状态码 404      ← 被 if 分支优雅处理，程序没崩
```

### 本次踩过的 3 个真实错误（都已修好）

| 报错 | 真实原因 | 结论 |
|---|---|---|
| `IndentationError: expected an indented block` | 改代码时留下两行重复的 `for u in users:`，第 84 行下面没有循环体 | 每行 `for` 下面必须有缩进代码；多余行用 `Ctrl+Shift+K` 整行删除 |
| `KeyError: 'public_repos'` | 404 响应的字典里没有这个 key，直接取值就崩 | **先判 `status_code == 200`，再 `resp.json()` 取字段** —— 接口脚本第一条铁律 |
| 每个用户请求了两次 | 旧的 `requests.get` 没删，和新代码并存 | 改代码时先删旧行再加新行 |

### 已掌握的核心模式

```python
resp = requests.get(url, timeout=10)
if resp.status_code == 200:
    data = resp.json()          # 确认正常后再解析
    # 断言：data["login"] == 期望值
else:
    # 记录失败，而不是让程序崩掉
```

这段模式以后写每一个接口脚本都要用，是 pytests 里 `assert response.status_code == 200` 的前身。
