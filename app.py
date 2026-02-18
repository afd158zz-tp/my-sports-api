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
    today = datetime.now().strftime('%m/%d')
    
    # Wix 표의 'result' 칸에 꽂힐 최종 텍스트
    search_targets = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={encoded_team}+경기결과", "match_info": f"{today} 경기 결과 및 뉴스"},
        {"site": "구글 스포츠", "url": f"https://www.google.com/search?q={encoded_team}+경기결과", "match_info": "리그 정보 및 스코어"},
        {"site": "다음 스포츠", "url": f"https://search.daum.net/search?w=tot&q={encoded_team}+경기결과", "match_info": f"{today} 영상 하이라이트"},
        {"site": "플래시스코어", "url": f"https://www.google.com/search?q=site:flashscore.co.kr+{encoded_team}", "match_info": "상세 경기 데이터 확인"},
        {"site": "네임드(Named)", "url": f"https://www.google.com/search?q=site:named.com+{encoded_team}", "match_info": "실시간 기록 분석"},
        {"site": "라이브스코어", "url": f"https://www.google.com/search?q=site:livescore.co.kr+{encoded_team}", "match_info": "통합 스코어 보드"},
        {"site": "스포조이", "url": f"https://www.google.com/search?q=site:spojoy.com+{encoded_team}", "match_info": "전적 분석 자료"},
        {"site": "AI스코어", "url": f"https://www.google.com/search?q=site:aiscore.com+{encoded_team}", "match_info": "AI 승률 예측"},
        {"site": "스코어맨", "url": f"https://scoreman123.com/bbs/board.php?bo_table=free&stx={encoded_team}", "match_info": "전문가 분석글"}
    ]

    return jsonify({
        "status": "success",
        "results": search_targets
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
