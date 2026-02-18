from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import urllib.parse
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

def get_real_score(team_name):
    try:
        query = urllib.parse.quote(f"{team_name} 경기결과")
        url = f"https://search.naver.com/search.naver?query={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 네이버 스포츠 상단 스코어 박스 추출 시도 (네이버 구조에 따라 변경될 수 있음)
        score_box = soup.select_one('.score_wrap')
        if score_box:
            return score_box.get_text(separator=' ').strip()
        return None
    except:
        return None

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    # 네이버에서 실제 점수 크롤링 시도
    real_score = get_real_score(team_name)
    today = datetime.now().strftime('%m/%d')
    
    # 점수가 있으면 점수를, 없으면 기존처럼 안내 문구를 보냄
    display_info = real_score if real_score else f"{today} 경기 정보 확인"

    search_targets = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name)}+경기결과", "match_info": display_info},
        {"site": "구글 스포츠", "url": f"https://www.google.com/search?q={urllib.parse.quote(team_name)}+경기결과", "match_info": "리그 순위 및 실시간 통계"},
        {"site": "플래시스코어", "url": f"https://www.google.com/search?q=site:flashscore.co.kr+{urllib.parse.quote(team_name)}", "match_info": "종료 경기 상세 데이터"},
        {"site": "라이브스코어", "url": f"https://www.google.com/search?q=site:livescore.co.kr+{urllib.parse.quote(team_name)}", "match_info": "통합 스코어 보드"},
        {"site": "AI스코어", "url": f"https://www.google.com/search?q=site:aiscore.com+{urllib.parse.quote(team_name)}", "match_info": "AI 승률 및 분석 완료"}
    ]

    return jsonify({"status": "success", "results": search_targets})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
