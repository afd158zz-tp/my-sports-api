from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import urllib.parse
import requests
import re
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# [필수] 실제 브라우저처럼 보이게 하는 정교한 헤더
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,.*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
    'Referer': 'https://www.google.com/'
}

def get_luxscore(team_name):
    try:
        # 럭스코어 404 방지를 위한 새로운 검색 주소 체계
        search_url = f"https://kr.top-esport.com/search.php?q={urllib.parse.quote(team_name)}"
        res = requests.get(search_url, headers=HEADERS, timeout=10)
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # 텍스트 전체에서 날짜와 점수 패턴을 더 넓게 탐색
            content = soup.get_text(separator=' ')
            date = re.search(r'(\d{2,4}[-./]\d{1,2}[-./]\d{1,2})', content)
            score = re.search(r'(\d{1,2}\s?-\s?\d{1,2})', content)
            
            if date:
                res_date = date.group(1).replace('-', '.')
                res_score = f" [{score.group(1)}]" if score else ""
                return f"최근: {res_date}{res_score}"
        return "검색결과 없음"
    except:
        return "확인 불가"

def get_naver_direct(team_name):
    try:
        # 네이버는 '경기결과'보다 '일정' 키워드가 더 정확한 표를 줍니다.
        url = f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name + ' 일정')}"
        res = requests.get(url, headers=HEADERS, timeout=7)
        
        if res.status_code == 200:
            content = res.text
            # 정규식으로 '풀타임' 근처의 날짜와 스코어를 직접 채굴
            date_match = re.search(r'(\d{1,2}\.\d{1,2}\.\([월화수목금토일]\))', content)
            score_match = re.search(r'(\d{1,2}\s?:\s?\d{1,2})', content)
            
            if date_match:
                res_date = f"2026.{date_match.group(1)}"
                res_score = f" [{score_match.group(1).strip()}]" if score_match else ""
                return f"최근: {res_date}{res_score}"
        return "데이터 확인 필요"
    except:
        return "일시적 오류"

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    # 각 사이트별 최적화된 링크와 데이터
    results = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name)}+경기일정", "match_info": get_naver_direct(team_name)},
        {"site": "럭스코어", "url": f"https://kr.top-esport.com/search.php?q={urllib.parse.quote(team_name)}", "match_info": get_luxscore(team_name)},
        {"site": "플래시스코어", "url": f"https://www.flashscore.co.kr/search/?q={urllib.parse.quote(team_name)}", "match_info": "상세 페이지 확인"},
        {"site": "AI스코어", "url": f"https://www.aiscore.com/ko/search/{urllib.parse.quote(team_name)}", "match_info": "예측 데이터 확인"}
    ]

    return jsonify({"status": "success", "results": results})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
