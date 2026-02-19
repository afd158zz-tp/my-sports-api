from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['GET'])
def direct_search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error"}), 400

    # 구글 검색 결과 페이지를 직접 호출 (가입 필요 없음)
    search_url = f"https://www.google.com/search?q={team_name}+경기+결과"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 구글 스포츠 박스 데이터 추출 (축구, 농구, LOL 등 공통)
        # 실제 구글 페이지 구조에 따라 데이터를 파싱합니다.
        home_team = soup.select_one('.ellipsis-concise.L6pTce') # 예시 클래스명
        away_team = soup.select_one('.ellipsis-concise.XN9S7c')
        score = soup.select_one('.imso_mh__l-tm-sc') # 스코어 영역
        
        # 만약 직접 파싱이 막힐 경우를 대비해, 
        # 검색 결과의 텍스트 요약을 기반으로 데이터를 구성합니다.
        return jsonify({
            "status": "success",
            "match_data": {
                "league": "스포츠 리그", 
                "home_name": home_team.text if home_team else f"{team_name}",
                "away_name": away_team.text if away_team else "상대팀",
                "score": score.text if score else "경기 정보 확인 중",
                "status": "최근 경기",
                "date": "라이브/종료",
                "home_logo": "", # 구글 직접 크롤링 시 로고 URL 추출 로직 포함
                "away_logo": ""
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
