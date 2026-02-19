from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

API_KEY = "cfba195cc6msh2007a2f5bf9f961p15da80jsn1fa91019b100"
BASE_URL = "https://allsportsapi2.p.rapidapi.com/api"

# 지원하는 모든 종목 리스트
SPORTS = ['football', 'basketball', 'baseball', 'volleyball', 'hockey', 'esports']

@app.route('/search', methods=['GET'])
def search_sports():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "No team name provided"}), 400

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "allsportsapi2.p.rapidapi.com"
    }

    try:
        # 모든 종목을 순차적으로 검색
        for sport in SPORTS:
            search_url = f"{BASE_URL}/{sport}/search/{team_name}"
            response = requests.get(search_url, headers=headers)
            search_data = response.json()

            if search_data.get('results'):
                # 팀 발견 시 해당 팀의 최근 경기 정보 가져오기
                team_id = search_data['results'][0]['entity']['id']
                match_url = f"{BASE_URL}/{sport}/team/{team_id}/matches/last/1"
                match_res = requests.get(match_url, headers=headers).json()

                if match_res.get('events'):
                    event = match_res['events'][0]
                    
                    # Wix 디자인에 맞춘 통합 데이터 구조 생성
                    return jsonify({
                        "status": "success",
                        "match_data": {
                            "league": event['tournament']['name'],
                            "date": event['status']['description'], # 경기 상태(종료 등)
                            "time": "", # 필요 시 시간 변환 로직 추가 가능
                            "home_name": event['homeTeam']['name'],
                            "away_name": event['awayTeam']['name'],
                            "score": f"{event['homeScore'].get('current', 0)} : {event['awayScore'].get('current', 0)}",
                            "status": "LIVE" if event['status']['type'] == "inprogress" else "FINISHED",
                            "home_logo": f"{BASE_URL}/{sport}/team/{event['homeTeam']['id']}/image",
                            "away_logo": f"{BASE_URL}/{sport}/team/{event['awayTeam']['id']}/image"
                        }
                    })

        return jsonify({"status": "fail", "message": "No data found in any sport"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
