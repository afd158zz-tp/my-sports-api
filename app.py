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

# 검색 결과를 저장할 메모리 캐시
cache = {}

# [핵심] 차단 방지를 위한 '진짜 브라우저' 위장용 고성능 헤더
def get_headers(site_type="common"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,.*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    }
    if site_type == "naver":
        headers['Referer'] = 'https://search.naver.com/'
    elif site_type == "lux":
        headers['Referer'] = 'https://kr.top-esport.com/'
    return headers

def fetch_data(url, site_type="common"):
    try:
        # 서버 차단을 피하기 위해 접속 시마다 약간의 시차를 둠
        time.sleep(0.5)
        res = requests.get(url, headers=get_headers(site_type), timeout=8)
        return res.text if res.status_code == 200 else None
    except:
        return None

def extract_date_score(text):
    # 날짜와 스코어를 한 번에 찾아내는 정규식
    date = re.search(r'(\d{1,2}\.\d{1,2}\.|\d{2,4}-\d{1,2}-\d{1,2})', text)
    score = re.search(r'(\d{1,2}\s?[:\-]\s?\d{1,2})', text)
    
    res_date = date.group(1).replace('-', '.') if date else ""
    res_score = f" [{score.group(1).replace(' ', '')}]" if score else ""
    
    # 연도가 없는 경우 보정
    if res_date and len(res_date) <= 6:
        res_date = f"2026.{res_date}"
        
    return f"{res_date}{res_score}".strip()

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    # 1. 캐시 확인
    now = time.time()
    if team_name in cache:
        exp, data = cache[team_name]
        if now < exp:
            return jsonify({"status": "success", "results": data, "cached": True})

    # 2. 각 사이트별 정밀 타격
    # 네이버
    naver_html = fetch_data(f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name + ' 일정')}", "naver")
    naver_res = extract_date_score(naver_html) if naver_html else "검색결과 없음"

    # 럭스코어 (search.php 경로 보정)
    lux_html = fetch_data(f"https://kr.top-esport.com/search.php?q={urllib.parse.quote(team_name)}", "lux")
    lux_res = extract_date_score(lux_html) if lux_html else "연결 지연"

    # 플래시스코어 & AI스코어 (구글 검색 스니펫 채굴 - 보안 우회)
    # 이 사이트들은 직접 접속 시 차단되므로 구글이 긁어놓은 미리보기 텍스트를 이용합니다.
    google_html = fetch_data(f"https://www.google.com/search?q={urllib.parse.quote(team_name + ' 경기결과 site:flashscore.co.kr OR site:aiscore.com')}")
    extra_res = extract_date_score(google_html) if google_html else "상세 확인 필요"

    results = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name)}+일정", "match_info": f"최근: {naver_res}"},
        {"site": "럭스코어", "url": f"https://kr.top-esport.com/search.php?q={urllib.parse.quote(team_name)}", "match_info": f"최근: {lux_res}"},
        {"site": "플래시스코어", "url": f"https://www.flashscore.co.kr/search/?q={urllib.parse.quote(team_name)}", "match_info": f"최근: {extra_res}"},
        {"site": "AI스코어", "url": f"https://www.aiscore.com/ko/search/{urllib.parse.quote(team_name)}", "match_info": f"최근: {extra_res}"}
    ]

    # 3. 캐시 저장
    cache[team_name] = (now + 3600, results)

    return jsonify({"status": "success", "results": results, "cached": False})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
