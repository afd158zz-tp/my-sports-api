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
    today = datetime.now().strftime('%m/%d') # MM/DD 형식으로 깔끔하게
    
    # 각 사이트별로 '가장 최근 정보'를 묘사하는 문구로 변경
    search_targets = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={encoded_team}+경기결과", "match_info": f"{today} 최신 스코어 업데이트"},
        {"site": "구글 스포츠", "url": f"https://www.google.com/search?q={encoded_team}+경기결과", "match_info": "리그 순위 및 경기 종료 정보"},
        {"site": "다음 스포츠", "url": f"https://search.daum.net/search?w=tot&q={encoded_team}+경기결과", "match_info": f"{today} 하이라이트 준비됨"},
        {"site": "플래시스코어", "url": f"https://www.google.com/search?q=site:flashscore.co.kr+{encoded_team}", "match_info": "실시간 배당 및 종료 스코어"},
        {"site": "네임드(Named)", "url": f"https://www.google.com/search?q=site:named.com+{encoded_team}", "match_info": "전/후반 상세 기록 분석"},
        {"site": "라이브스코어", "url": f"https://www.google.com/search?q=site:livescore.co.kr+{encoded_team}", "match_info": "커뮤니티 실시간 응원톡 활성"},
        {"site": "스포조이", "url": f"https://www.google.com/search?q=site:spojoy.com+{encoded_team}", "match_info": "결장자 정보 및 맞대결 전적"},
        {"site": "AI스코어", "url": f"https://www.google.com/search?q=site:aiscore.com+{encoded_team}", "match_info": "AI 승률 예측 및 통계 완료"},
        {"site": "스코어맨", "url": f"https://scoreman123.com/bbs/board.php?bo_table=free&stx={encoded_team}", "match_info": "전문가 경기 분석글 확인"}
    ]

    return jsonify({
        "status": "success",
        "results": search_targets
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
