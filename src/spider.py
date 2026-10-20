import requests
import sqlite3
import concurrent.futures  # 引入并发库
from database import insert_job, get_current_page, update_page, DB_NAME


def translate_text(text):
    """调用免费 API 将英文翻译成中文（带容错和降级机制）"""
    try:
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|zh-CN"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            translated = data.get('responseData', {}).get('translatedText', '')
            if translated and "MYMEMORY WARNING" not in translated:
                return translated
            else:
                return f"[降级原文] {text[:15]}..."
        else:
            return f"[降级原文] {text[:15]}..."

    except Exception as e:
        return text  # 彻底失败时返回英文原文


def crawl_real_jobs():
    current_page = get_current_page()
    print(f"🕷️ 开始抓取 GitHub 第 {current_page} 页，并启动并发翻译清洗...")

    # 👇 修改了这里：将 q=label:hiring 换成了 q=freelance，突破数据枯竭限制
    # 如果你想抓其他类型，可以改成 q=remote 或者 q=兼职
    query_keyword = "freelance"
    url = f"https://api.github.com/search/issues?q={query_keyword}+state:open&per_page=30&page={current_page}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/vnd.github.v3+json"
    }

    success_count = 0
    try:
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()
        items = data.get('items', [])

        if not items:
            print("⚠️ 已经没有更多数据了，或触发了GitHub深水区限流。")
            return 0

        # 第一步：先找出所有需要入库的新数据（过滤掉已有的）
        new_items = []
        for item in items:
            link = item.get('html_url', '')

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM jobs WHERE url=?", (link,))
            exists = cursor.fetchone()
            conn.close()

            if not exists:
                new_items.append(item)

        if not new_items:
            print("⚠️ 这一页的数据都已经在数据库里了。")
            update_page(current_page + 1)  # 防止卡死，依然翻页
            return 0

        # 第二步：把需要翻译的标题提取出来，使用“多线程”并发翻译
        titles = [item.get('title', '未知项目') for item in new_items]

        # 开启线程池，最多同时发 10 个翻译请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            translated_titles = list(executor.map(translate_text, titles))

        # 第三步：把翻译好的中文和原数据组合，写入数据库
        for item, title_zh in zip(new_items, translated_titles):
            title = item.get('title', '未知项目')
            repo_url = item.get('repository_url', '')
            repo_name = repo_url.split('/')[-1] if repo_url else "GitHub"
            pub_date = item.get('created_at', '')[:10]
            link = item.get('html_url', '')

            insert_job(
                title=f"[远程] {title}",
                title_zh=f"[远程] {title_zh}",
                company=repo_name,
                salary="按项目结算",
                location="线上远程",
                publish_date=pub_date,
                url=link
            )
            success_count += 1

        if len(items) > 0:
            update_page(current_page + 1)
            print(f"✅ 第 {current_page} 页抓取完成，并发翻译新增 {success_count} 条数据。")

    except Exception as e:
        print(f"GitHub 接口抓取失败: {e}")

    return success_count