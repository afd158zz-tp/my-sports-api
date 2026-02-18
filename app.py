from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, os

app = Flask(__name__)
CORS(app)

# 사용자님의 API 키 고정
API_KEY = "251241088c08a887a5b9626a6a9cdce8"

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name: return jsonify({"status": "error"})

    try:
        # 1. API에 팀 이름으로 최근 1경기 요청
        url = f"https://v3.football.api-sports.io/fixtures?search={team_name}&last=1"
        headers = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}
        res = requests.get(url, headers=headers, timeout=5).json()
        
        if res.get('response'):
            data = res['response'][0]
            # 사용자님이 원하는 '상세 정보' 조립
            result = {
                "status": "success",
                "match_data": {
                    "date": data['fixture']['date'][:10], # 2026-02-14
                    "time": data['fixture']['date'][11:16], # 20:00
                    "home": data['teams']['home']['name'],
                    "away": data['teams']['away']['name'],
                    "score": f"{data['goals']['home']} : {data['goals']['away']}",
                    "league": data['league']['name'],
                    "status": "경기 종료" if data['fixture']['status']['short'] == "FT" else "진행 중/예정"
                }
            }
            return jsonify(result)
        
        return jsonify({"status": "fail", "message": "해당 팀의 최근 경기를 찾을 수 없습니다."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
