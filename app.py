from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import urllib.parse

app = Flask(__name__)
CORS(app) 
app.config['JSON_AS_ASCII'] = False

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    encoded_team = urllib.parse.quote(team_name)
    
    # 직접 연결(1~3) 및 구글 경유 우회 연결(4~9)
    search_targets = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={encoded_team}+경기결과", "note": "최신 뉴스 및 국내외 공식 기록"},
        {"site": "구글 스포츠", "url": f"https://www.google.com/search?q={encoded_team}+경기결과", "note": "구글 자체 스코어 보드 및 통계"},
        {"site": "다음 스포츠", "url": f"https://search.daum.net/search?w=tot&q={encoded_team}+경기결과", "note": "영상 하이라이트 및 실시간 중계"},
        {"site": "플래시스코어", "url": f"https://www.google.com/search?q=site:flashscore.co.kr+{encoded_team}", "note": "플래시스코어 내 팀 정보 검색"},
        {"site": "네임드(Named)", "url": f"https://www.google.com/search?q=site:named.com+{encoded_team}", "note": "네임드 내 실시간 데이터 검색"},
        {"site": "라이브스코어", "url": f"https://www.google.com/search?q=site:livescore.co.kr+{encoded_team}", "note": "라이브스코어 내 커뮤니티 정보 검색"},
        {"site": "스포조이", "url": f"https://www.google.com/search?q=site:spojoy.com+{encoded_team}", "note": "스포조이 내 분석 정보 검색"},
        {"site": "AI스코어", "url": f"https://www.google.com/search?q=site:aiscore.com+{encoded_team}", "note": "AI스코어 내 통계 정보 검색"},
        {"site": "스코어맨", "url": f"https://www.google.com/search?q=site:scoreman123.com+{encoded_team}", "note": "스코어맨 내 게시판 정보 검색"}
    ]

    return jsonify({
        "status": "success",
        "team": team_name,
        "results": search_targets
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
