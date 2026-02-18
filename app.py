from Flask import Flask, request, jsonify
from flask_cors import CORS
import os
import urllib.parse
import requests
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# 공통 날짜 추출 함수 (연도 포함)
def extract_date(text):
    # 1. 2026-02-14 또는 25-11-29 또는 2026.02.14 형태 추출
    date_pattern = re.search(r'(\d{2,4}[-./]\d{1,2}[-./]\d{1,2})', text)
    if date_pattern:
        return date_pattern.group(1).replace('-', '.')
    
    # 2. 연도가 없는 경우(02.11.) 올해 연도(2026)를 붙여줌
    short_date = re.search(r'(\d{1,2}\.\d{1,2}\.)', text)
    if short_date:
        return f"2026.{short_date.group(1)}"
    
    return None

def get_site_info(team_name, site_name):
    try:
        if site_name == "네이버":
            query = f"{team_name} 경기결과"
            url = f"https://search.naver.com/search.naver?query={urllib.parse.quote(query)}"
        else: # 구글 기반 검색 (구글, 플래시스코어, AI스코어)
            domain = {"구글": "", "플래시스코어": "site:flashscore.co.kr", "AI스코어": "site:aiscore.com"}
            url = f"https://www.google.com/search?q={urllib.parse.quote(domain[site_name] + ' ' + team_name + ' 경기결과')}"
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        res = requests.get(url, headers=headers, timeout=5)
        
        if res.status_code == 200:
            content = res.text
            found_date = extract_date(content)
            if found_date:
                return f"최근: {found_date}"
        return "검색결과 없음"
    except:
        return "확인 불가"

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    # [핵심] 이제 각 사이트마다 개별적으로 정보를 긁어옵니다!
    results = []
    targets = [
        {"name": "네이버 스포츠", "id": "네이버", "url": f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name)}+경기결과"},
        {"name": "구글 스포츠", "id": "구글", "url": f"https://www.google.com/search?q={urllib.parse.quote(team_name)}+경기결과"},
        {"name": "플래시스코어", "id": "플래시스코어", "url": f"https://www.google.com/search?q=site:flashscore.co.kr+{urllib.parse.quote(team_name)}"},
        {"name": "AI스코어", "id": "AI스코어", "url": f"https://www.google.com/search?q=site:aiscore.com+{urllib.parse.quote(team_name)}"}
    ]

    for t in targets:
        date_info = get_site_info(team_name, t['id'])
        results.append({
            "site": t['name'],
            "url": t['url'],
            "match_info": date_info
        })

    return jsonify({"status": "success", "results": results})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
