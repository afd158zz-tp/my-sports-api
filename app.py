from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# [설정] 사용자님의 API KEY (가장 신뢰할 수 있는 데이터 소스)
API_KEY = "251241088c08a887a5b9626a6a9cdce8"

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    try:
        # API-SPORTS에 가장 최근 경기 1개 요청
        url = f"https://v3.football.api-sports.io/fixtures?search={team_name}&last=1"
        headers = {
            'x-rapidapi-key': API_KEY,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
        response = requests.get(url, headers=headers, timeout=5).json()

        if response.get('response') and len(response['response']) > 0:
            data = response['response'][0]
            
            # Wix 프론트엔드에서 바로 보여줄 수 있는 정제된 데이터 조립
            return jsonify({
                "status": "success",
                "match_data": {
                    "date": data['fixture']['date'][:10].replace('-', '.'),
                    "time": data['fixture']['date'][11:16],
                    "home": data['teams']['home']['name'],
                    "away": data['teams']['away']['name'],
                    "score": f"{data['goals']['home']} : {data['goals']['away']}",
                    "league": data['league']['name'],
                    "status": "경기 종료" if data['fixture']['status']['short'] == "FT" else "진행 중/예정",
                    "home_logo": data['teams']['home']['logo'], # 로고 이미지 추가
                    "away_logo": data['teams']['away']['logo']  # 로고 이미지 추가
                }
            })
        else:
            return jsonify({"status": "fail", "message": "최근 경기 데이터를 찾을 수 없습니다."})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
