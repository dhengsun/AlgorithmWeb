# 新建文件 app/scrapers/__init__.py
# 新建文件 app/scrapers/luogu.py
import requests
from bs4 import BeautifulSoup
import json

def get_luogu_problem(url):
    """洛谷题目爬虫"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.luogu.com.cn/"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', {'id': 'lentille-context'})
        
        if not script:
            return {"error": "未找到题目数据"}

        data = json.loads(script.string)
        problem_data = data['data']['problem']
        
        # 构建基础内容
        content = f"## 题目描述\n{problem_data['content']['description']}\n\n"
        content += f"## 输入格式\n{problem_data['content']['formatI']}\n\n"
        content += f"## 输出格式\n{problem_data['content']['formatO']}\n\n"
        
        # 添加样例
        if problem_data['samples']:
            content += "## 输入输出样例\n"
            for i, sample in enumerate(problem_data['samples'], 1):
                content += f"### 输入样例 #{i}\n```plain\n{sample[0].strip()}\n```\n"
                content += f"### 输出样例 #{i}\n```plain\n{sample[1].strip()}\n```\n"
        
        # 添加提示
        content += f"## 说明/提示\n{problem_data['content']['hint']}\n\n"
        
        # 添加时间内存限制到正文末尾
        time_limit = problem_data['limits']['time'][0] / 1000
        memory_limit = int(problem_data['limits']['memory'][0] / 1024)
        content += f"时间限制：{time_limit}秒\n内存限制：{memory_limit}MB"
        
        return {
            "external_id": problem_data['pid'],
            "title": problem_data['title'],
            "algorithm_tags": problem_data['tags'],
            "difficulty": problem_data['difficulty'],
            "content": content  # 包含完整内容
        }
        
    except requests.RequestException as e:
        return {"error": f"网络请求失败: {str(e)}"}
    except Exception as e:
        return {"error": f"数据解析失败: {str(e)}"}