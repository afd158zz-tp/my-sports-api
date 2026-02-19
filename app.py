from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import urllib.parse

app = Flask(__name__)
CORS(app)

API_KEY = "251241088c08a887a5b9626a6a9cdce8"

def fetch_from_google_backup(team_name):
    """API에 데이터가 없을 때 구글 검색 결과를 지능적으로 분석"""
    try:
        search_query = f"{team_name} 경기결과"
        url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(url, headers=headers, timeout=5).text
        
        # 날짜와 점수가 붙어있는 패턴 정밀 타격 (제가 어제 팩트체크한 로직)
        pattern = re.compile(r'(\d{1,2}\.\d{1,2}\.).*?(\d{1,2}\s?[:\-]\s?\d{1,2})')
        found = pattern.search(res)
        
        if found:
            return {
                "date": f"2026년 {found.group(1).replace('.', '월 ')}일",
                "time": "시간 정보 확인 중",
                "home_name": team_name,
                "away_name": "상대팀",
                "score": found.group(2).replace(' ', '').replace('-', ':'),
                "league": "스포츠 리그",
                "status": "경기 종료",
                "home_logo": "", # 구글 크롤링은 로고 추출이 불안정함
                "away_logo": ""
            }
        return None
    except:
        return None

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name: return jsonify({"status": "error"})

    # 1단계: API-SPORTS (가장 정확한 팩트 + 로고)
    try:
        api_url = f"https://v3.football.api-sports.io/fixtures?search={team_name}&last=1"
        headers = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}
        api_res = requests.get(api_url, headers=headers, timeout=5).json()

        if api_res.get('response'):
            m = api_res['response'][0]
            return jsonify({
                "status": "success",
                "match_data": {
                    "date": m['fixture']['date'][:10].replace('-', '년 ') + '일',
                    "time": m['fixture']['date'][11:16],
                    "home_name": m['teams']['home']['name'],
                    "away_name": m['teams']['away']['name'],
                    "home_logo": m['teams']['home']['logo'],
                    "away_logo": m['teams']['away']['logo'],
                    "score": f"{m['goals']['home']} : {m['goals']['away']}",
                    "league": m['league']['name'],
                    "status": "경기 종료" if m['fixture']['status']['short'] == "FT" else "예정"
                }
            })
    except:
        pass

    # 2단계: 구글 검색 백업 (API에 없을 경우 실행)
    backup_data = fetch_from_google_backup(team_name)
    if backup_data:
        return jsonify({"status": "success", "match_data": backup_data})

    return jsonify({"status": "fail", "message": "모든 경로에서 데이터를 찾을 수 없습니다."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
