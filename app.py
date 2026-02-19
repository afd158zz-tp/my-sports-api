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
        # 가입/인증 필요 없는 DuckDuckGo 엔진으로 검색 (LOL, 농구, 야구 등 전 종목 대응)
        with DDGS() as ddgs:
            # 실시간 경기 결과 텍스트를 최우선으로 긁어옵니다.
            query = f"{team} 경기 결과 스코어"
            results = list(ddgs.text(query, max_results=3))

            if results:
                # 검색 결과 상단 텍스트에서 경기 정보를 조합합니다.
                main_info = results[0]['body']
                
                return jsonify({
                    "status": "success",
                    "match_data": {
                        "league": "실시간 스포츠",
                        "home_name": team,
                        "away_name": "상대팀(결과참조)",
                        "score": "결과 확인됨", 
                        "status": "최근 경기",
                        "summary": main_info, # 검색된 요약 텍스트 전체 전달
                        "home_logo": "", 
                        "away_logo": ""
                    }
                })
        
        return jsonify({"status": "fail", "message": "데이터를 찾을 수 없습니다."})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
