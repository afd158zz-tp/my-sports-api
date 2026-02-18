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
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Wix 표의 'result' 칸에 날짜가 들어가도록 구성
    search_targets = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={encoded_team}+경기결과", "date": f"{today} 기준"},
        {"site": "구글 스포츠", "url": f"https://www.google.com/search?q={encoded_team}+경기결과", "date": "실시간 통계"},
        {"site": "다음 스포츠", "url": f"https://search.daum.net/search?w=tot&q={encoded_team}+경기결과", "date": f"{today} 업데이트"},
        {"site": "플래시스코어", "url": f"https://www.google.com/search?q=site:flashscore.co.kr+{encoded_team}", "date": "종료/예정 경기"},
        {"site": "네임드(Named)", "url": f"https://www.google.com/search?q=site:named.com+{encoded_team}", "date": "최신 스코어"},
        {"site": "라이브스코어", "url": f"https://www.google.com/search?q=site:livescore.co.kr+{encoded_team}", "date": "금일 결과"},
        {"site": "스포조이", "url": f"https://www.google.com/search?q=site:spojoy.com+{encoded_team}", "date": "최근 분석"},
        {"site": "AI스코어", "url": f"https://www.google.com/search?q=site:aiscore.com+{encoded_team}", "date": "통계 데이터"},
        {"site": "스코어맨", "url": f"https://www.google.com/search?q=site:scoreman123.com+{encoded_team}", "date": "최신 게시글"}
    ]

    return jsonify({
        "status": "success",
        "results": search_targets
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
