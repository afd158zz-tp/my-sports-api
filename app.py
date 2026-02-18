from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import urllib.parse
import requests
import re

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

def get_best_date(team_name):
    try:
        # 네이버에서 '팀명 경기일정'으로 검색한 결과 페이지를 가져옵니다.
        query = urllib.parse.quote(f"{team_name} 경기일정")
        url = f"https://search.naver.com/search.naver?query={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        res = requests.get(url, headers=headers, timeout=5)
        
        if res.status_code == 200:
            content = res.text
            # [패턴] 사용자님이 사진에서 보여준 구글 스타일 '2. 11. (수)' 또는 '02.11.' 추출
            # 정규식을 더 유연하게 만들어서 공백이 있어도 다 잡아냅니다.
            date_match = re.search(r'(\d{1,2}\.\s?\d{1,2}\.\s?\([월화수목금토일]\))', content)
            
            if date_match:
                return date_match.group(1)
            
            # 요일이 없는 경우 (예: 2. 11. 또는 02.11.) 추가 시도
            simple_date = re.search(r'(\d{1,2}\.\s?\d{1,2}\.)', content)
            if simple_date:
                return simple_date.group(1)
        return None
    except:
        return None

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    # 날짜 추출
    match_date = get_best_date(team_name)
    
    # 날짜가 있으면 "최근: 2. 11. (수)", 없으면 "일정 확인 필요"
    display_text = f"최근: {match_date}" if match_date else "일정 확인 필요"

    # 사용자님의 요구대로 4개의 핵심 사이트로 구성
    search_targets = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name)}+경기결과", "match_info": display_text},
        {"site": "구글 스포츠", "url": f"https://www.google.com/search?q={urllib.parse.quote(team_name)}+경기결과", "match_info": "실시간 데이터 보기"},
        {"site": "플래시스코어", "url": f"https://www.google.com/search?q=site:flashscore.co.kr+{urllib.parse.quote(team_name)}", "match_info": "상세 경기 일정"},
        {"site": "라이브스코어", "url": f"https://www.google.com/search?q=site:livescore.co.kr+{urllib.parse.quote(team_name)}", "match_info": "실시간 스코어 보드"}
    ]

    return jsonify({"status": "success", "results": search_targets})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
