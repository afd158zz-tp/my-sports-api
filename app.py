from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import urllib.parse
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    encoded_team = urllib.parse.quote(team_name)
    # 오늘 날짜를 기준으로 표시 (예: 2024-05-20 기준)
    today = datetime.now().strftime('%Y-%m-%d')
    
    search_targets = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={encoded_team}+경기결과", "date": f"{today} 업데이트"},
        {"site": "구글 스포츠", "url": f"https://www.google.com/search?q={encoded_team}+경기결과", "date": "실시간 정보"},
        {"site": "다음 스포츠", "url": f"https://search.daum.net/search?w=tot&q={encoded_team}+경기결과", "date": f"{today} 업데이트"},
        {"site": "플래시스코어", "url": f"https://www.google.com/search?q=site:flashscore.co.kr+{encoded_team}", "date": "경기 종료/예정"},
        {"site": "네임드(Named)", "url": f"https://www.google.com/search?q=site:named.com+{encoded_team}", "date": "실시간 스코어"},
        {"site": "라이브스코어", "url": f"https://www.google.com/search?q=site:livescore.co.kr+{encoded_team}", "date": "전일/금일 결과"},
        {"site": "스포조이", "url": f"https://www.google.com/search?q=site:spojoy.com+{encoded_team}", "date": "최근 분석 데이터"},
        {"site": "AI스코어", "url": f"https://www.google.com/search?q=site:aiscore.com+{encoded_team}", "date": "통계 기반 일자"},
        {"site": "스코어맨", "url": f"https://www.google.com/search?q=site:scoreman123.com+{encoded_team}", "date": "최신 게시물 기준"}
    ]

    return jsonify({
        "status": "success",
        "team": team_name,
        "results": search_targets
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
