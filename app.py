from flask import Flask, request, jsonify
from flask_cors import CORS
import urllib.parse, requests, os

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# [설정] 사용자의 API-SPORTS 키를 여기에 넣으세요
API_KEY = "251241088c08a887a5b9626a6a9cdce8" # image_ad4599.png에서 확인하신 키

def get_api_match_data(team_name):
    """API-SPORTS를 통해 100% 정확한 점수와 날짜 채굴"""
    try:
        url = f"https://v3.football.api-sports.io/fixtures?search={team_name}&last=1"
        headers = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}
        response = requests.get(url, headers=headers, timeout=5).json()
        
        if response.get('response'):
            fix = response['response'][0]
            date = fix['fixture']['date'][:10].replace('-', '.') # 2026.02.18
            score = f"{fix['goals']['home']}:{fix['goals']['away']}"
            return f"최근: {date} [{score}]"
        return "경기 데이터 확인 필요"
    except:
        return "API 연결 확인 중"

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name: return jsonify({"status": "error"})

    # 100% 정확한 데이터 (API 기반)
    real_data = get_api_match_data(team_name)
    encoded_team = urllib.parse.quote(team_name)

    # 5대 사이트 통합 결과 (쓰레기 데이터 배제, 고품질 링크 중심)
    results = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={encoded_team}+경기결과", "match_info": real_data},
        {"site": "네임드(Named)", "url": f"https://www.google.com/search?q=site:named.net+{encoded_team}", "match_info": "커뮤니티 반응 확인"},
        {"site": "럭스코어", "url": f"https://kr.top-esport.com/search.php?q={encoded_team}", "match_info": "라이브 스코어 확인"},
        {"site": "플래시스코어", "url": f"https://www.flashscore.co.kr/search/?q={encoded_team}", "match_info": "실시간 세부 스탯"},
        {"site": "AI스코어", "url": f"https://www.aiscore.com/ko/search/{encoded_team}", "match_info": "AI 승률 분석 정보"}
    ]

    return jsonify({"status": "success", "results": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
