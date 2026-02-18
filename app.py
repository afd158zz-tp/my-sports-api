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
        # 네이버에서 가장 정확한 날짜 패턴을 긁어옵니다.
        query = urllib.parse.quote(f"{team_name} 경기일정")
        url = f"https://search.naver.com/search.naver?query={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        res = requests.get(url, headers=headers, timeout=5)
        
        if res.status_code == 200:
            content = res.text
            # 사용자님이 만족하신 바로 그 날짜 패턴!
            date_match = re.search(r'(\d{1,2}\.\s?\d{1,2}\.\s?\([월화수목금토일]\))', content)
            if date_match:
                return date_match.group(1)
            
            # 요일이 없는 경우 대비
            simple_date = re.search(r'(\d{1,2}\.\s?\d{1,2}\.)', content)
            if simple_date:
                return simple_date.group(1)
        return None
    except:
        return None

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    # 공통으로 사용할 날짜 정보 획득
    match_date = get_best_date(team_name)
    display_text = f"최근: {match_date}" if match_date else "일정 확인 필요"

    # 모든 사이트의 match_info에 동일한 날짜를 넣어줍니다.
    search_targets = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name)}+경기결과", "match_info": display_text},
        {"site": "구글 스포츠", "url": f"https://www.google.com/search?q={urllib.parse.quote(team_name)}+경기결과", "match_info": display_text},
        {"site": "플래시스코어", "url": f"https://www.google.com/search?q=site:flashscore.co.kr+{urllib.parse.quote(team_name)}", "match_info": display_text},
        {"site": "라이브스코어", "url": f"https://www.google.com/search?q=site:livescore.co.kr+{urllib.parse.quote(team_name)}", "match_info": display_text}
    ]

    return jsonify({"status": "success", "results": search_targets})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
