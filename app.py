from flask import Flask, request, jsonify
from flask_cors import CORS
from duckduckgo_search import DDGS

app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['GET'])
def sports_search():
    team = request.args.get('team')
    if not team:
        return jsonify({"status": "error", "message": "No team name"}), 400

    try:
        # 가입 필요 없는 DuckDuckGo 검색 엔진 활용
        with DDGS() as ddgs:
            query = f"{team} 경기 결과 스코어"
            # 텍스트 검색 결과 중 가장 관련성 높은 3개를 긁어옵니다.
            results = list(ddgs.text(query, max_results=3))

            if results:
                return jsonify({
                    "status": "success",
                    "match_data": {
                        "league": "실시간 통합 검색",
                        "home_name": team,
                        "away_name": "최근 경기",
                        "score": "결과 확인됨",
                        "status": "라이브/종료",
                        "summary": results[0]['body'] # Wix UI의 txtScore에 표시될 핵심 내용
                    }
                })
        return jsonify({"status": "fail", "message": "No data found"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
