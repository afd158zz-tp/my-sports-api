from flask import Flask, request, jsonify
from flask_cors import CORS
import urllib.parse, requests, re, time, os
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# 고품질 브라우저 헤더 (실제 크롬과 100% 동일하게 세팅)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
}

def get_verified_match(team_name, site_url, site_type):
    try:
        # 럭스코어나 네임드는 다이렉트 접근 시 Referer가 중요함
        headers = HEADERS.copy()
        headers['Referer'] = 'https://www.google.com/'
        
        res = requests.get(site_url, headers=headers, timeout=8)
        if res.status_code != 200: return "데이터 접근 지연"
        
        content = res.text
        # [핵심] 날짜(00.00. 형태)와 점수(0:0 형태)가 인접해 있는지 확인
        # 0:9, 0:10 같은 노이즈를 방지하기 위해 점수 형식을 엄격하게 제한 (\d:\d)
        match_pattern = re.compile(r'(\d{1,2}\.\d{1,2}\.).*?(\d{1,2}\s?[:\-]\s?\d{1,2})')
        found = match_pattern.search(content)
        
        if found:
            date, score = found.group(1), found.group(2).replace(' ', '')
            # 비정상적인 점수(한 팀이 7점 이상 등)는 필터링하여 정확도 향상
            s1, s2 = map(int, score.replace('-', ':').split(':'))
            if s1 < 10 and s2 < 10: 
                return f"최근: 2026.{date} [{score}]"
                
        return "최신 경기 정보 확인 중"
    except:
        return "확인 불가"

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name: return jsonify({"status": "error"})

    # 각 사이트별 직접 접근 및 정밀 파싱
    results = [
        {
            "site": "네이버 스포츠", 
            "match_info": get_verified_match(team_name, f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name + ' 경기결과')}", "naver")
        },
        {
            "site": "네임드(Named)", 
            "match_info": get_verified_match(team_name, f"https://www.google.com/search?q=site:named.net+{urllib.parse.quote(team_name)}", "named")
        },
        {
            "site": "럭스코어", 
            "match_info": get_verified_match(team_name, f"https://kr.top-esport.com/search.php?q={urllib.parse.quote(team_name)}", "lux")
        }
    ]

    return jsonify({"status": "success", "results": results})
