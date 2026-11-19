# -*- coding: utf-8 -*-
# ─────────────────────────────────────────────
# conftest.py 是 pytest 的"魔法文件"：
#   1. 名字必须是 conftest.py，放在测试文件同目录
#   2. pytest 启动时自动加载，测试文件里【不需要 import】
#   3. 里面的 @pytest.fixture 可以被所有测试用例直接用
# ─────────────────────────────────────────────
import pytest

import api_github


@pytest.fixture
def github():
    """提供 API 封装层。

    用法：测试函数的参数里写上 github，pytest 就自动把这个值传进来：

        def test_xxx(github):
            resp = github.get_user("octocat")

    这叫"依赖注入"：你只管声明要什么，pytest 负责把东西递给你。
    """
    return api_github
