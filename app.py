from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import urllib.parse
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

def get_real_date(team_name):
    try:
        query = urllib.parse.quote(f"{team_name} 경기일정")
        url = f"https://search.naver.com/search.naver?query={query}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        res = requests.get(url, headers=headers, timeout=5)
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # 1. 네이버 스포츠 박스에서 날짜 패턴(00.00) 찾기
            text = soup.get_text()
            date_pattern = re.compile(r'\d{1,2}\.\d{1,2}\.') # "02.18." 형태 찾기
            found_dates = date_pattern.findall(text)
            
            if found_dates:
                # 가장 마지막에 언급된 날짜가 보통 최근 경기일 확률이 높음
                return f"최근 경기: {found_dates[-1]}"
        return None
    except:
        return None

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    # 네이버에서 날짜 정보 획득 시도
    scraped_date = get_real_date(team_name)
    today = datetime.now().strftime('%m/%d')
    
    # 날짜를 못 가져오면 '날짜 확인 필요'라고 명시해서 다른 사이트 클릭을 유도함
    match_display = scraped_date if scraped_date else "경기 일자 확인 필요"

    search_targets = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name)}+경기결과", "match_info": match_display},
        {"site": "구글 스포츠", "url": f"https://www.google.com/search?q={urllib.parse.quote(team_name)}+경기결과", "match_info": "실시간 데이터 확인"},
        {"site": "플래시스코어", "url": f"https://www.google.com/search?q=site:flashscore.co.kr+{urllib.parse.quote(team_name)}", "match_info": "종료/예정 상세일정"},
        {"site": "라이브스코어", "url": f"https://www.google.com/search?q=site:livescore.co.kr+{urllib.parse.quote(team_name)}", "match_info": "전종목 통합 일정"}
    ]

    return jsonify({"status": "success", "results": search_targets})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
