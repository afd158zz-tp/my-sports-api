from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    results_list = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    # 1. 네이버 스포츠 검색 (예시)
    try:
        naver_url = f"https://search.naver.com/search.naver?query={team_name}+경기결과"
        res = requests.get(naver_url, headers=headers)
        # 실제로는 여기서 특정 태그를 파싱해야 하지만, 
        # 우선 연결 확인을 위해 검색 링크와 요약을 제공합니다.
        results_list.append({
            "site": "네이버 스포츠",
            "result": f"[{team_name}] 최신 일정 및 결과 요약을 확인하세요.",
            "url": naver_url
        })
    except:
        pass

    # 2. 다음 스포츠 검색
    try:
        daum_url = f"https://search.daum.net/search?w=tot&q={team_name}+경기결과"
        results_list.append({
            "site": "다음 스포츠",
            "result": f"[{team_name}] 실시간 스코어 및 중계 정보를 제공합니다.",
            "url": daum_url
        })
    except:
        pass

    # 3. 플래시스코어 (바로가기)
    results_list.append({
        "site": "플래시스코어",
        "result": "전세계 실시간 스코어 보드 바로가기",
        "url": f"https://www.flashscore.co.kr/search/?q={team_name}"
    })

    return jsonify({
        "status": "success",
        "team": team_name,
        "results": results_list
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
