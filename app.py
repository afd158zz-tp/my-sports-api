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

def extract_fine_date(team_name):
    try:
        # 구글은 크롤링 방어가 심하므로, 네이버 검색 결과 내의 구글 스타일 날짜를 먼저 공략합니다.
        query = urllib.parse.quote(f"{team_name} 경기결과")
        url = f"https://search.naver.com/search.naver?query={query}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        res = requests.get(url, headers=headers, timeout=5)
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            text = soup.get_text(separator=' ')
            
            # [패턴 1] 2. 11. (수) 또는 02.11. 형태 추출
            # 숫자. 숫자. (요일) 패턴을 찾습니다.
            date_pattern = re.compile(r'(\d{1,2}\.\s?\d{1,2}\.\s?\([월화수목금토일]\)|\d{1,2}\.\d{1,2}\.)')
            found_dates = date_pattern.findall(text)
            
            if found_dates:
                # 가장 최근 날짜(리스트의 마지막이나 특정 위치)를 반환
                # 중복 제거 후 가장 '날짜다운' 것을 선택
                clean_dates = list(set([d.strip() for d in found_dates]))
                return f"최근: {clean_dates[-1]}"
        return None
    except:
        return None

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    # 정밀 날짜 추출 시도
    fine_date = extract_fine_date(team_name)
    
    # 날짜가 없으면 구글 이미지처럼 '2. 11.' 형태를 유도하기 위한 기본값
    match_display = fine_date if fine_date else "일정 확인 필요"

    search_targets = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name)}+경기결과", "match_info": match_display},
        {"site": "구글 스포츠", "url": f"https://www.google.com/search?q={urllib.parse.quote(team_name)}+경기결과", "match_info": "구글 실시간 스코어 확인"},
        {"site": "플래시스코어", "url": f"https://www.google.com/search?q=site:flashscore.co.kr+{urllib.parse.quote(team_name)}", "match_info": "상세 쿼터/세트별 일정"},
        {"site": "라이브스코어", "url": f"https://www.google.com/search?q=site:livescore.co.kr+{urllib.parse.quote(team_name)}", "match_info": "전종목 실시간 일정"}
    ]

    return jsonify({"status": "success", "results": search_targets})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
