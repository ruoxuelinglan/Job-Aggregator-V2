# 求职/兼职信息聚合系统 (Job Aggregator)

## 📖 项目简介
本项目是一个基于 Python Flask + SQLite + Requests 开发的“求职/兼职信息聚合与数据分析系统”。旨在解决求职者在不同网站频繁切换搜索的痛点，通过后台爬虫抓取真实的 GitHub 开源社区外包/招聘数据，并利用 NLP 翻译接口进行并发清洗，最终在本地进行可视化展示、中英文检索与 Excel 导出。是一个具备完整业务闭环的 Web 软件应用。

## 📂 目录导览
- `src/`：核心源码目录
  - `app.py`：Flask 后端主程序，处理路由、Excel导出与网页渲染。
  - `database.py`：SQLite 数据库操作模块，负责建表、增删改查及分页配置。
  - `spider.py`：爬虫模块，负责并发抓取真实数据、调用翻译引擎并自动翻页。
  - `templates/index.html`：前端页面，包含响应式的搜索、数据表格与 ECharts 数据可视化图表。
  - `jobs.db`：SQLite 数据库文件。
- `docs/`：存放项目说明书与 AI 提示词记录。
- `requirements.txt`：项目依赖清单。

## 🚀 运行方式速览
1. 安装依赖：`pip install -r requirements.txt`
2. 进入源码目录：`cd src`  **(重要)**
3. 启动 Web 服务：`python app.py`
4. 在浏览器访问：`http://127.0.0.1:5000`
5. 点击页面右上角“抓取新数据”按钮，即可拉取真实数据、自动翻译并持久化入库。

*(注：本项目采用公开免认证数据接口及本地 SQLite，无任何需要配置的 API Key 或密码，不存在敏感信息泄露风险。)*