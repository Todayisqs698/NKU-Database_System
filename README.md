# F1 赛事管理系统 (F1 Race Management System)

本项目是一个基于 **Python Flask** 后端框架与 **MySQL 8.0** 大型数据库管理系统开发的小型 F1（一级方程式）赛事管理系统。系统严格按照数据库工程规范设计，实现了完整的用户权限控制、多表关联架构以及底层的数据库高级特性（事务、触发器、存储过程、视图）。

---

## 项目核心技术栈

* **后台数据库：** MySQL 8.0.45
* **开发高级语言：** Python 3.13
* **后端核心框架：** Flask
* **前端技术选型：** Bootstrap 5.3.0 + HTML/CSS/JS
* **数据库驱动：** PyMySQL

---

## 角色与权限划分

系统基于 Web 机制实现了三种核心角色的权限隔离：

* **Admin (系统管理员)：** 拥有最高权限。可审核用户账号，增删改查车队、赛道、赛季安排，通过**存储过程**修改比赛成绩，执行**事务级联删除**等。
* **Steward (车队领队)：** 负责对应车队的车手管理。可在**触发器**的年龄合规校验下签约新车手（全职/储备）或解约车手。
* **Guest (访客/普通游客)：** 只读权限。仅能查询公开的比赛结果、车手排名和基于**视图**计算出来的实时积分榜。

---

## 🛠️ 数据库工程核心设计点

### 1. 含有事务应用的级联删除 (开启事务机制)
* **实现位置：** `services/team_service.py`
* **业务场景：** 管理员删除某一车队时，系统以数据库事务（Transaction）方式级联清空该车队底下的：比赛成绩 $\rightarrow$ 子类车手记录（全职/储备） $\rightarrow$ 车手主记录 $\rightarrow$ 车队记录（共涉及 5 张表）。
* **技术特性：** 严格遵循外键拓扑依赖顺序删除，任意一步失败自动回滚（Rollback），确保底层数据一致性。

### 2. 触发器防御机制 (BEFORE INSERT)
* **实现位置：** `trigger.sql`
* **业务场景：** 领队签约新车手向 `driver` 表插入数据时触发。
* **技术特性：** `before_driver_insert` 触发器会强行校验年龄边界条件。若 `driver_age < 18` 或为 `NULL`，直接利用 `SIGNAL SQLSTATE '45000'` 拦截插入并向后端抛出异常提示。

### 3. 存储过程控制下的成绩更新 (STORED PROCEDURE)
* **实现位置：** `procedure.sql`
* **业务场景：** 管理员修改某条大奖赛完赛成绩。
* **技术特性：** 封装存储过程 `update_race_result`，内部利用复合参数规避变量作用域同名冲突，通过 `JOIN grandprix` 校验赛事有效性，并通过 `OUT` 参数向 Flask 异步反馈执行状态。

### 4. 复杂多表聚合查询视图 (VIEW)
* **实现位置：** `schema.sql` (视图定义)
* **业务场景：** 实时动态车手积分榜展示页面 `/standings`。
* **技术特性：** 建立视图 `driver_standings_view`，联查 `driver`、`team`、`result`、`grandprix` 四张关系表，利用 `COALESCE(SUM(...))` 及 `COUNT(CASE WHEN...)` 聚合函数动态计算总积分与夺冠次数，实现高效的只读表现层解耦。

---

## 📂 项目目录结构说明

```plaintext
F1-Race-Management-System/
├── app.py                  # Flask 应用启动入口
├── config.py               # 数据库连接参数配置文件 (Host, User, Password 等)
├── schema.sql              # 数据库建表 DDL 语句及视图定义
├── seed_data.sql           # 初始演示数据（含初始化管理员及车队车手）
├── trigger.sql             # 拦截车手年龄的 BEFORE INSERT 触发器源码
├── procedure.sql           # 修改比赛成绩的存储过程源码
├── requirements.txt        # 项目 Python 依赖包列表
├── models/                 # 数据模型层 (可选定义)
├── routes/                 # 表现层/路由控制器
│   ├── auth.py             # 登录、注册及权限鉴权拦截路由
│   ├── admin.py            # 管理员核心业务路由
│   ├── steward.py          # 车队领队业务路由
│   └── public.py           # 游客公开查询路由
├── services/               # 业务逻辑层 (封装核心 SQL 及高级特性调用)
│   ├── user_service.py     # 用户账号审核及管理
│   ├── team_service.py     # 包含事务应用的删除车队业务
│   ├── driver_service.py   # 签约车手业务
│   └── result_service.py   # 调用存储过程修改成绩、查询积分榜视图业务
├── utils/
│   ├── db.py               # 数据库统一连接池及 get_db() 连接管理
│   └── auth.py             # 权限校验装饰器
├── static/                 # 静态资源 (CSS/JS/Bootstrap)
├── templates/              # 前端 Jinja2 模板页面 (按角色及功能分包)
└── tests/
    └── e2e_test.py         # 端到端功能自动化测试脚本
