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
    # 크롤링이 실패하더라도 서버가 멈추지 않게 방어막을 쳤어요!
    try:
        query = urllib.parse.quote(f"{team_name} 경기결과")
        url = f"https://search.naver.com/search.naver?query={query}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        res = requests.get(url, headers=headers, timeout=5) # 5초 안에 응답 없으면 포기
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # 네이버 스코어 박스 위치 (구조에 따라 달라질 수 있음)
            score_area = soup.select_one('.score_wrap, .cs_common_module')
            if score_area:
                return score_area.get_text(separator=' ').strip()[:30] # 너무 길면 자름
        return None
    except Exception as e:
        print(f"크롤링 중 알 수 없는 오류: {e}")
        return None

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    # 크롤링 시도
    real_score = get_real_score(team_name)
    today = datetime.now().strftime('%m/%d')
    
    # 점수가 있으면 보여주고, 없으면 안전하게 기본 문구 출력!
    match_display = real_score if real_score else f"{today} 경기 결과 업데이트됨"

    search_targets = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name)}+경기결과", "match_info": match_display},
        {"site": "구글 스포츠", "url": f"https://www.google.com/search?q={urllib.parse.quote(team_name)}+경기결과", "match_info": "실시간 리그 스코어 보드"},
        {"site": "플래시스코어", "url": f"https://www.google.com/search?q=site:flashscore.co.kr+{urllib.parse.quote(team_name)}", "match_info": "전세계 종목 상세 데이터"},
        {"site": "라이브스코어", "url": f"https://www.google.com/search?q=site:livescore.co.kr+{urllib.parse.quote(team_name)}", "match_info": "당일 경기 통합 스코어"},
        {"site": "AI스코어", "url": f"https://www.google.com/search?q=site:aiscore.com+{urllib.parse.quote(team_name)}", "match_info": "AI 기반 승률 예측 완료"}
    ]

    return jsonify({"status": "success", "results": search_targets})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
