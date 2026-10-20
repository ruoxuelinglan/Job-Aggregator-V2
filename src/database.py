import sqlite3

DB_NAME = 'jobs.db'


def init_db():
    """初始化数据库，创建职位表和配置表"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. 创建职位表（新增 title_zh 字段，用于存储中文翻译）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            title_zh TEXT,
            company TEXT,
            salary TEXT,
            location TEXT,
            publish_date TEXT,
            url TEXT UNIQUE
        )
    ''')

    # 2. 创建系统配置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO config (key, value) VALUES ('github_page', '1')")

    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成！")


def insert_job(title, title_zh, company, salary, location, publish_date, url):
    """插入一条职位信息"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO jobs (title, title_zh, company, salary, location, publish_date, url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, title_zh, company, salary, location, publish_date, url))
        conn.commit()
    except sqlite3.Error as e:
        print(f"❌ 插入数据失败: {e}")
    finally:
        conn.close()


def get_all_jobs(keyword=None):
    """查询职位信息，支持中英文联合模糊查询"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if keyword:
        # 同时匹配 英文标题、中文翻译、公司名
        cursor.execute("SELECT * FROM jobs WHERE title LIKE ? OR title_zh LIKE ? OR company LIKE ?",
                       ('%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%'))
    else:
        cursor.execute("SELECT * FROM jobs")

    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_job(job_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()


def get_current_page():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM config WHERE key='github_page'")
    row = cursor.fetchone()
    conn.close()
    return int(row[0]) if row else 1


def update_page(new_page):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE config SET value=? WHERE key='github_page'", (str(new_page),))
    conn.commit()
    conn.close()