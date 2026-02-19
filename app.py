from flask import Flask, request, jsonify
from flask_cors import CORS
from duckduckgo_search import DDGS

app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['GET'])
def sports_search():
    team = request.args.get('team')
    if not team:
        return jsonify({"status": "error", "message": "팀명을 입력하세요"}), 400

    try:
        with DDGS() as ddgs:
            # 실시간 경기 결과 텍스트를 우선적으로 긁어옵니다.
            query = f"{team} 최근 경기 결과 스코어"
            results = list(ddgs.text(query, max_results=1))

            if results:
                # 검색된 텍스트 전체를 'score' 자리에 넣어버립니다. (가장 확실한 노출 방법)
                return jsonify({
                    "status": "success",
                    "match_data": {
                        "league": "실시간 스포츠 검색",
                        "home_name": team,
                        "away_name": "최근 전적",
                        "score": results[0]['body'][:100] + "...", # 검색 요약 앞부분
                        "status": "검색 완료",
                        "summary": results[0]['body']
                    }
                })
        return jsonify({"status": "fail", "message": "데이터를 찾지 못했습니다."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
