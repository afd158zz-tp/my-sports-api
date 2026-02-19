from flask import Flask, request, jsonify
from flask_cors import CORS
from duckduckgo_search import DDGS  # 이 줄이 핵심입니다.

app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['GET'])
def sports_search():
    team = request.args.get('team')
    if not team:
        return jsonify({"status": "error", "message": "No team name"}), 400

    try:
        with DDGS() as ddgs:
            # 실시간 경기 결과 텍스트를 긁어옵니다.
            query = f"{team} 경기 결과 스코어"
            results = list(ddgs.text(query, max_results=3))

            if results:
                # 첫 번째 검색 결과 요약을 보냅니다.
                return jsonify({
                    "status": "success",
                    "match_data": {
                        "league": "실시간 검색 결과",
                        "home_name": team,
                        "away_name": "상대팀",
                        "score": "결과 확인됨",
                        "status": "최근/라이브",
                        "summary": results[0]['body'] # Wix에서 이 텍스트를 크게 보여줍니다.
                    }
                })
        return jsonify({"status": "fail", "message": "No results found"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
