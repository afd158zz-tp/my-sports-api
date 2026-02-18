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
        query = urllib.parse.quote(f"{team_name} 경기일정")
        url = f"https://search.naver.com/search.naver?query={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        res = requests.get(url, headers=headers, timeout=5)
        
        if res.status_code == 200:
            content = res.text
            # 1. 날짜 패턴 추출 (사용자님이 만족하신 02.11.(수) 형태)
            date_match = re.search(r'(\d{1,2}\.\s?\d{1,2}\.\s?\([월화수목금토일]\))', content)
            if date_match:
                return date_match.group(1), "success"
            
            # 2. 날짜는 없지만 시즌 종료 관련 단어가 있는지 확인 (아이디어 3번 적용!)
            if any(word in content for word in ["종료", "시즌 오프", "일정이 없습니다", "시즌이 끝났습니다"]):
                return None, "off_season"
                
        return None, "not_found"
    except:
        return None, "error"

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    # 공통 날짜 및 상태 정보 가져오기
    match_date, status = get_best_date(team_name)
    
    # 상황별 메시지 결정
    if status == "success":
        display_text = f"최근: {match_date}"
    elif status == "off_season":
        display_text = "시즌 종료 또는 일정 없음"
    else:
        display_text = "일정 확인 (직접 이동)"

    # 요청하신 5개 사이트로 구성 (AI스코어 추가)
    search_targets = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name)}+경기결과", "match_info": display_text},
        {"site": "구글 스포츠", "url": f"https://www.google.com/search?q={urllib.parse.quote(team_name)}+경기결과", "match_info": display_text},
        {"site": "플래시스코어", "url": f"https://www.google.com/search?q=site:flashscore.co.kr+{urllib.parse.quote(team_name)}", "match_info": display_text},
        {"site": "라이브스코어", "url": f"https://www.google.com/search?q=site:livescore.co.kr+{urllib.parse.quote(team_name)}", "match_info": display_text},
        {"site": "AI스코어", "url": f"https://www.google.com/search?q=site:aiscore.com+{urllib.parse.quote(team_name)}", "match_info": display_text}
    ]

    return jsonify({"status": "success", "results": search_targets})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
