# 新建文件 app/scrapers/leetcode.py
import requests
from bs4 import BeautifulSoup
import json
import re

def get_leetcode_problem_info(url):
    """LeetCode题目爬虫"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', {'id': '__NEXT_DATA__'})
        
        if not script:
            return {"error": "未找到题目数据"}
            
        data = json.loads(script.string)
        
        # 查找题目数据
        question_data = None
        for query in data['props']['pageProps']['dehydratedState']['queries']:
            if 'question' in query['state']['data']:
                question_data = query['state']['data']['question']
                break
                
        if not question_data:
            return {"error": "题目数据解析失败"}
            
        # 清理内容
        cleaned_content = re.sub(r'<[^>]+>', '', question_data['translatedContent'])
        examples = re.findall(
            r'输入:?([^\n]+)\n输出:?([^\n]+)(?:\n解释:?([^\n]+))?', 
            cleaned_content
        )
        
        example_str = "\n\n## 示例\n"
        for i, (input_ex, output_ex, explain) in enumerate(examples, 1):
            example_str += f"\n### 示例 {i}\n**输入**: {input_ex.strip()}\n\n**输出**: {output_ex.strip()}"
            if explain:
                example_str += f"\n\n**解释**: {explain.strip()}"
        
        return {
            "external_id": question_data['questionFrontendId'],
            "title": question_data['translatedTitle'],
            "difficulty": question_data.get('difficulty', '未知'),
            "algorithm_tags": [tag['translatedName'] for tag in question_data['topicTags']],
            "content": re.sub(r'\n示例：[\s\S]*', '', cleaned_content).strip() + example_str
        }
        
    except requests.RequestException as e:
        return {"error": f"网络请求失败: {str(e)}"}
    except Exception as e:
        return {"error": f"数据解析失败: {str(e)}"}