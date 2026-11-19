"""
Python 基础第 1 课练习
按编号从上往下做，每做完一个就运行一次：
    cd /d "C:\\Users\\ASUS\\WorkBuddy\\2026-10-28-09-36-05"
    python python练习_第1课.py

带 TODO 注释的地方就是要你动手的地方。
"""
import requests

print("=" * 40)
print("练习 1：变量与格式化字符串")
print("=" * 40)
# 变量：给数据起个名字。字符串用引号，数字不用。
name = "torvalds"
repo_count = 7

# f-string：在字符串里嵌变量，{} 里放变量名
print(f"用户 {name} 有 {repo_count} 个公开仓库")

# TODO 1-1：把 name 改成 "torvalds"，repo_count 改成任意数字，运行看输出
# TODO 1-2：再加一行 print，输出"今天是学习 Python 的第 1 天"（用 f-string 嵌一个 day = 1）
day=1
print (f"今天是学习python的第{day}天")


print()
print("=" * 40)
print("练习 2：字典（dict）—— JSON 的本质")
print("=" * 40)
# 字典 = 一堆"键: 值"的集合，用 {} 包起来
# 它就是接口返回的 JSON！Apifox 里的 $.login 就是取这里的 "login"
user = {
    "login": "octocat",
    "id": 583231,
    "public_repos": 8,
}

# 取值：字典名["键名"]
print("login:", user["login"])
print("id:", user["id"])

# 往字典里添加新键值对
user["blog"] = "https://github.blog"
print("blog:", user["blog"])
print("public_repos:", user["public_repos"]) 
user["site_admin"] = False                        
print("site_admin:", user["site_admin"])
user["login"] = "torvalds"                         
print(user)
# TODO 2-1：打印 user 里的 public_repos
# TODO 2-2：新增一个键 "site_admin"，值是 False（注意大写开头），然后打印它
# TODO 2-3：把 "login" 的值改成 "torvalds"，再打印整个字典：print(user)


print()
print("=" * 40)
print("练习 3：列表（list）—— 数组响应的本质")
print("=" * 40)
# 列表 = 按顺序排的一串值，用 [] 包起来，编号从 0 开始
users = ["octocat", "torvalds", "defunkt"]

print("第 1 个:", users[0])     # 列表[序号]
print("共几个:", len(users))    # len() 数个数

# 往列表末尾添加
users.append("gaearon")
print("添加后:", users)
print("第 2 个:", users[1])      
users.remove("defunkt")          
print(users)
# TODO 3-1：打印列表里的第 2 个用户（记得序号从 0 开始）
# TODO 3-2：把 "defunkt" 从列表里删掉（提示：users.remove("defunkt")），然后 print(users)


print()
print("=" * 40)
print("练习 4：for 循环 —— 这就是 Apifox 的 CSV 数据驱动")
print("=" * 40)
# for 循环：对列表里的每一项，执行一遍缩进里的代码
# 注意：for 那行末尾有冒号，下面的代码要缩进 4 个空格
users = ["octocat", "torvalds", "defunkt", "gaearon", "no_such_user_123abc"]


for u in users:
    resp = requests.get(f"https://api.github.com/users/{u}", timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        print(f"{u}  状态码 {resp.status_code}  公开仓库 {data['public_repos']} 个")
    else:
        print(f"{u}  状态码 {resp.status_code}  ❌ 用户不存在或请求失败")
# TODO 4-1：把列表换成 users（练习 3 里那个），运行看有什么不同
# TODO 4-2：再加一个用户 "gaearon" 进列表，运行看他有多少仓库
# TODO 4-3：试着在循环里故意放一个不存在的用户 "no_such_user_123abc"，
#           观察状态码 —— 和你在 Apifox 里做异常用例时的 404 是同一件事


print()
print("=" * 40)
print("练习 5：if/else 判断 —— 这就是断言的通过/失败")
print("=" * 40)
resp = requests.get("https://api.github.com/users/thisuserdoesnotexist123abc", timeout=10)

# == 是"比较是否相等"（两个等号），= 是"赋值"（一个等号），别搞混
if resp.status_code == 200:
    print("✅ 通过")
elif resp.status_code == 404:
    print("❌ 用户不存在")
else:
    print(f"❌ 失败，状态码 {resp.status_code}")

# TODO 5-1：把 URL 里的 octocat 换成不存在的用户，运行看走哪个分支
# TODO 5-2：加一个 elif 分支：状态码是 404 时打印 "❌ 用户不存在"


print()
print("=" * 40)
print("练习 6：函数 —— 接口定义一次，用例无限组合")
print("=" * 40)
# 函数 = 把一段逻辑打包起个名字，以后随时调用
# def 函数名(参数):  下面缩进的代码是函数体，return 把结果交出去
def check_user(username):
    resp = requests.get(f"https://api.github.com/users/{username}", timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ {username}: id={data['id']}, 仓库 {data['public_repos']} 个")
        return True
    print(f"❌ {username}: 状态码 {resp.status_code}")
    return False

# 调用函数：写函数名 + 括号 + 参数
check_user("octocat")
check_user("torvalds")
check_user("defunkt")
check_user("thisuserdoesnotexist123abc")


# TODO 6-1：再用 check_user 测 "torvalds" 和 "defunkt"
# TODO 6-2（挑战）：写一个 for 循环，把 users 列表里每个用户都测一遍
#                  提示：for name in users: check_user(name)



print("🎉 全部练习完成！有报错就把最后一行发出来。")
for name in users:
    check_user(name)
print()