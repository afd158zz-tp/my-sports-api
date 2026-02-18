from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import urllib.parse

app = Flask(__name__)
# Wix에서 접근할 수 있도록 보안 허용
CORS(app) 
# 한글 깨짐 방지
app.config['JSON_AS_ASCII'] = False

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    # 검색어를 URL용으로 변환
    encoded_team = urllib.parse.quote(team_name)
    
    # 각 사이트별 연결 리스트 (플래시스코어는 에러 방지를 위해 메인으로 연결)
    search_targets = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={encoded_team}+경기결과", "note": "최신 뉴스 및 국내외 공식 기록"},
        {"site": "구글 스포츠", "url": f"https://www.google.com/search?q={encoded_team}+경기결과", "note": "구글 자체 스코어 보드 및 통계"},
        {"site": "다음 스포츠", "url": f"https://search.daum.net/search?w=tot&q={encoded_team}+경기결과", "note": "영상 하이라이트 및 실시간 중계"},
        {"site": "플래시스코어", "url": "https://www.flashscore.co.kr/", "note": "전세계 실시간 스코어 (메인페이지)"},
        {"site": "네임드(Named)", "url": f"https://www.named.com/game/search/{encoded_team}", "note": "실시간 데이터 및 커뮤니티 분석"},
        {"site": "라이브스코어", "url": f"https://www.livescore.co.kr/bbs/board.php?bo_table=game&sca=&sop=and&sfl=wr_subject&stx={encoded_team}", "note": "국내 최대 실시간 스코어 커뮤니티"},
        {"site": "스포조이", "url": f"http://www.spojoy.com/search/?q={encoded_team}", "note": "경기 분석 및 배당 정보 정보"},
        {"site": "AI스코어", "url": f"https://www.aiscore.com/ko/search/{encoded_team}", "note": "AI 기반 경기 예측 및 통계"},
        {"site": "스코어맨", "url": f"https://scoreman123.com/bbs/board.php?bo_table=free&sfl=wr_subject&stx={encoded_team}", "note": "경기 결과 및 자유 분석 게시판"}
    ]

    return jsonify({
        "status": "success",
        "team": team_name,
        "results": search_targets
    })

if __name__ == '__main__':
    # Render 환경에 맞는 포트 설정
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
