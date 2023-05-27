import requests
from bs4 import BeautifulSoup
import html2text
import os
from readability import Document
from concurrent.futures import ThreadPoolExecutor
import time

# 设置请求头，模拟浏览器行为
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# 爬取的网址
url = 'https://nextjs.org/docs'

# 发送HTTP请求，添加重试逻辑


def send_request(url):
    max_retries = 5
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, headers=headers)
            return response
        except requests.exceptions.RequestException:
            retries += 1
            time.sleep(1)  # 等待1秒后重试
    return None


response = send_request(url)

# 初始化BeautifulSoup对象，用于HTML解析
soup = BeautifulSoup(response.text, 'html.parser')

# 获取所有的链接
links = [a['href'] for a in soup.find_all('a', href=True) if a.text.strip()]

# 对链接进行过滤，只保留 /docs 开头的链接
links = ['https://nextjs.org' +
         link for link in links if link.startswith('/docs')]

# 初始化html2text对象
h = html2text.HTML2Text()
h.ignore_links = True

# 定义一个函数来获取单个链接的Markdown文本


def get_markdown(link):
    print(link)
    response = send_request(link)
    if response is not None:
        doc = Document(response.text)
        html_content = doc.summary()
        markdown_text = h.handle(html_content)
        return markdown_text
    else:
        return ''


# 使用 ThreadPoolExecutor 并发获取所有链接的Markdown文本
with ThreadPoolExecutor(max_workers=10) as executor:
    markdown_texts = executor.map(get_markdown, links)

merged_text = '\n\n'.join(markdown_texts)

# 将合并的md文件保存到本地
with open('merged.md', 'w') as f:
    f.write(merged_text)

print('Markdown files merged and saved as merged.md')
