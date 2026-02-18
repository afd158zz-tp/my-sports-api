from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import urllib.parse
import requests
import re
import time
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# 결과를 저장할 메모리 금고 (팀명: [만료시간, 데이터])
cache = {}

# 보안 통과를 위한 정교한 헤더
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ko-kr',
    'Referer': 'https://m.naver.com/'
}

def get_naver_data(team):
    try:
        # 모바일 네이버는 데이터가 더 가볍고 구조가 단순합니다.
        url = f"https://m.search.naver.com/search.naver?query={urllib.parse.quote(team + ' 경기일정')}"
        res = requests.get(url, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            text = res.text
            # 날짜와 점수 패턴 매칭
            date = re.search(r'(\d{1,2}\.\d{1,2}\.\([월화수목금토일]\))', text)
            score = re.search(r'(\d{1,2}\s?:\s?\d{1,2})', text)
            
            res_date = f"2026.{date.group(1)}" if date else "일정 확인"
            res_score = f" [{score.group(1).strip()}]" if score else ""
            return f"{res_date}{res_score}"
        return "데이터 없음"
    except:
        return "확인 불가"

def get_luxscore_data(team):
    try:
        # 404 에러를 피하기 위한 수정된 검색 경로
        url = f"https://kr.top-esport.com/search.php?q={urllib.parse.quote(team)}"
        res = requests.get(url, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            content = res.text
            # 텍스트 데이터에서 날짜(00-00-00)와 점수(0-0) 추출
            date = re.search(r'(\d{2,4}[-./]\d{1,2}[-./]\d{1,2})', content)
            score = re.search(r'(\d{1,2}\s?-\s?\d{1,2})', content)
            
            res_date = date.group(1).replace('-', '.') if date else "결과 없음"
            res_score = f" [{score.group(1).replace(' ', '')}]" if score else ""
            return f"{res_date}{res_score}"
        return "연결 실패"
    except:
        return "확인 불가"

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    # 1. 캐시 확인 (있으면 즉시 반환)
    now = time.time()
    if team_name in cache:
        exp, data = cache[team_name]
        if now < exp:
            return jsonify({"status": "success", "results": data, "cached": True})

    # 2. 우회 크롤링 실행
    results = [
        {
            "site": "네이버 스포츠", 
            "url": f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name)}+경기일정", 
            "match_info": get_naver_data(team_name)
        },
        {
            "site": "럭스코어", 
            "url": f"https://kr.top-esport.com/search.php?q={urllib.parse.quote(team_name)}", 
            "match_info": get_luxscore_data(team_name)
        },
        {
            "site": "플래시스코어", 
            "url": f"https://www.flashscore.co.kr/search/?q={urllib.parse.quote(team_name)}", 
            "match_info": "상세 페이지 이동" 
        },
        {
            "site": "AI스코어", 
            "url": f"https://www.aiscore.com/ko/search/{urllib.parse.quote(team_name)}", 
            "match_info": "데이터 분석 확인"
        }
    ]

    # 3. 캐시에 저장 (3600초 = 1시간)
    cache[team_name] = (now + 3600, results)

    return jsonify({"status": "success", "results": results, "cached": False})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
