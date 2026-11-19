# GitHub API 接口自动化测试项目

![CI](https://github.com/shenmidaimengzhiren/api-autotest/actions/workflows/ci.yml/badge.svg)

基于 Python + pytest 的接口自动化测试实践项目，以 GitHub 公开 REST API 为被测对象，
覆盖正常场景、异常场景与参数化数据驱动，使用分层设计组织代码。

## 被测对象

| 接口 | 方法 | 说明 |
|---|---|---|
| `/users/{username}` | GET | 查询用户信息 |
| `/users/{username}/repos` | GET | 查询用户的公开仓库列表 |

接口文档：https://docs.github.com/rest

## 技术栈

- **Python 3.15** — 编程语言
- **requests** — HTTP 请求库
- **pytest** — 测试框架（用例组织、断言、参数化）
- **pytest-html** — HTML 测试报告

## 目录结构

```
.
├── api_github.py          # 封装层：接口定义、BASE_URL、超时时间
├── conftest.py            # pytest 公共配置文件，提供 fixture
├── test_github_api.py     # 用例层：基础用例（200 / 字段 / 404）
├── test_param.py          # 用例层：参数化数据驱动用例
├── requirements.txt       # 依赖清单
├── report.html            # 测试报告（运行后生成）
└── .gitignore
```

### 分层设计

```
用例层 test_*.py  →  只写断言（验证什么）
      ↓ 调用
封装层 api_github.py  →  只管发请求（怎么发）
      ↓ 由 conftest.py 注入
公共层 conftest.py  →  fixture、环境配置
```

这样设计的好处：切换测试环境只需修改 `api_github.py` 中的 `BASE_URL` 一处，
全部用例自动生效；新增接口只需在封装层加一个函数，用例层直接调用。

## 测试用例设计

共 **12 条用例**，覆盖以下场景：

| 场景类型 | 用例说明 | 断言要点 |
|---|---|---|
| 正常场景 | 查询存在的用户（4 个真实用户） | 状态码 200、`login` 与请求一致、`id` 为正 |
| 异常场景 | 查询不存在的用户 | 状态码 404、`message` = `Not Found` |
| 异常场景 | 访问不存在的路径 | 状态码 404 |
| 关联场景 | 查询用户及其仓库列表 | 状态码 200 |

用例数据通过 `@pytest.mark.parametrize` 参数化，一个测试函数生成多条独立用例，
单条失败不影响其他用例执行。

## 运行方式

```bash
# 安装依赖
python -m pip install -r requirements.txt

# 运行全部用例
python -m pytest -v

# 运行并生成 HTML 报告
python -m pytest -v --html=report.html --self-contained-html

# 只运行某个文件
python -m pytest test_param.py -v
```

## 测试报告

`report.html` 为自包含单文件报告（样式内嵌），可直接用浏览器打开或分享，
内容包括用例总数、通过/失败统计、每条用例耗时与失败详情。

## 持续集成（CI）

项目通过 GitHub Actions 实现自动化回归：每次推送到 `main` 分支，
云端自动搭建 Python 环境、安装依赖、执行全部用例并生成测试报告。

- CI 配置：`.github/workflows/ci.yml`
- 运行记录：仓库的 **Actions** 标签页
- 测试报告：每次运行结束后可在运行详情页下载 Artifact `test-report`

README 顶部的徽章实时反映最近一次构建状态：
绿色 passing 表示全部用例通过，红色 failing 表示有用例失败。

## 已知限制

- 依赖公网访问 GitHub API，未登录状态下有调用频率限制（60 次/小时）
- 断言值依赖真实用户数据（如 `octocat` 的 `id` 固定为 583231），
  真实项目中应使用独立的测试环境与可控数据

## 后续计划

- [ ] 引入 `conftest.py` 中的 session 级 fixture 复用 HTTP 连接
- [ ] 接入 Allure 报告，支持用例分级与历史趋势
- [x] 接入 GitHub Actions，实现提交即触发回归
- [ ] 补充 token 鉴权场景（Header 传 token，验证限流提升至 5000 次/小时）
