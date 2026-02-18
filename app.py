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
        # 브라우저인 척 속이는 마법의 문장 (User-Agent)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        # ★ timeout=5 를 넣어서 5초 넘게 걸리면 그냥 무시하게 만들었어요!
        res = requests.get(url, headers=headers, timeout=5)
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # 네이버 점수판 근처 글자 긁어오기
            score_area = soup.select_one('.score_wrap, .cs_common_module')
            if score_area:
                return score_area.get_text(separator=' ').strip()[:30]
        return None
    except:
        return None # 에러 나도 서버는 멈추지 말고 무조건 넘어가라!

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    # 점수 가져오기 시도
    real_score = get_real_score(team_name)
    today = datetime.now().strftime('%m/%d')
    
    # 점수가 있으면 점수, 없으면 기본 문구!
    match_display = real_score if real_score else f"{today} 경기 정보 확인"

    search_targets = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name)}+경기결과", "match_info": match_display},
        {"site": "구글 스포츠", "url": f"https://www.google.com/search?q={urllib.parse.quote(team_name)}+경기결과", "match_info": "실시간 리그 스코어"},
        {"site": "플래시스코어", "url": f"https://www.google.com/search?q=site:flashscore.co.kr+{urllib.parse.quote(team_name)}", "match_info": "종료 경기 상세 정보"},
        {"site": "라이브스코어", "url": f"https://www.google.com/search?q=site:livescore.co.kr+{urllib.parse.quote(team_name)}", "match_info": "전종목 실시간 스코어"},
        {"site": "AI스코어", "url": f"https://www.google.com/search?q=site:aiscore.com+{urllib.parse.quote(team_name)}", "match_info": "AI 승률 예측 통계"}
    ]

    return jsonify({"status": "success", "results": search_targets})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
