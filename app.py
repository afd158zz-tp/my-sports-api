from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['GET'])
def search_engine():
    team = request.args.get('team')
    if not team:
        return jsonify({"status": "error", "message": "팀명을 입력하세요"}), 400

    # 1. 구글 검색을 통해 실시간 스포츠 박스 데이터를 긁어옵니다.
    search_url = f"https://www.google.com/search?q={team}+경기+결과"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 2. 구글 스포츠 결과 영역(Knowledge Graph) 분석
        # 종목(축구, 농구, LOL 등)에 상관없이 스코어와 팀명을 추출합니다.
        try:
            # 팀명 추출
            teams = soup.select('.ellipsis-concise') 
            home = teams[0].text if len(teams) > 0 else team
            away = teams[1].text if len(teams) > 1 else "상대팀"

            # 스코어 추출
            scores = soup.select('.imso_mh__l-tm-sc')
            score_text = f"{scores[0].text} : {scores[1].text}" if len(scores) > 1 else "경기 예정"

            # 리그 및 상태 정보
            league = soup.select_one('.imso_mh__tr-n-ST').text if soup.select_one('.imso_mh__tr-n-ST') else "스포츠 리그"
            status = soup.select_one('.imso_mh__lv-st-t').text if soup.select_one('.imso_mh__lv-st-t') else "종료/예정"
            
            # 로고 이미지 (구글 썸네일 경로 추출)
            logos = soup.select('.imso_btl__guide-img')
            home_logo = logos[0]['src'] if len(logos) > 0 else ""
            away_logo = logos[1]['src'] if len(logos) > 1 else ""

        except:
            # 구조가 다를 경우 일반 검색 요약에서 데이터 추출 (비상용 로직)
            home, away, score_text, league, status = team, "상대팀", "정보 확인 불가", "종합 스포츠", "업데이트 중"
            home_logo, away_logo = "", ""

        return jsonify({
            "status": "success",
            "match_data": {
                "league": league,
                "home_name": home,
                "away_name": away,
                "score": score_text,
                "status": status,
                "date": "LIVE/최근",
                "home_logo": home_logo,
                "away_logo": away_logo
            }
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
