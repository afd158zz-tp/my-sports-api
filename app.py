from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
# 한글 깨짐 방지 설정
app.config['JSON_AS_ASCII'] = False

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    # 1. 간단한 구글 검색 결과 긁어오기 예시
    search_url = f"https://www.google.com/search?q={team_name}+경기결과"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 결과를 담을 바구니
    results_list = []

    try:
        # 실제로 구글에 노크해서 데이터를 가져옵니다.
        response = requests.get(search_url, headers=headers)
        # (여기에 각 사이트별 스크래핑 로직이 추가될 예정입니다)
        
        results_list.append({
            "site": "Google Search",
            "result": f"{team_name}의 최신 정보를 확인 중입니다.",
            "url": search_url
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

    return jsonify({
        "status": "success",
        "team": team_name,
        "results": results_list
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
