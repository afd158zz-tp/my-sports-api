from flask import Flask, request, jsonify
from flask_cors import CORS
import urllib.parse, requests, re, time, os

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# 검색 결과 캐시 (메모리 절약 및 속도 향상)
cache = {}

def get_refined_data(team_name, site_domain):
    try:
        # 각 사이트별 구글 검색 쿼리 최적화
        search_query = f"{team_name} 경기결과 site:{site_domain}"
        url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept-Language': 'ko-KR,ko;q=0.9'
        }
        
        # 구글 서버에 요청 (차단 방지를 위해 약간의 지연시간 권장)
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            # 1. 날짜 추출 (02.14. 또는 2026-02-14 등)
            date_match = re.search(r'(\d{1,2}\.\d{1,2}\.|\d{2,4}-\d{1,2}-\d{1,2})', res.text)
            # 2. 점수 추출 (0:0 ~ 15:15 사이의 정상적인 스코어만 허용)
            # [0:93] 같은 노이즈를 방지하기 위해 10의 자리 제한
            score_match = re.search(r'\b([0-9]|1[0-5])\s?[:\-]\s?([0-9]|1[0-5])\b', res.text)
            
            date_str = date_match.group(1).replace('-', '.') if date_match else ""
            # 연도가 짧을 경우 현재 연도(2026) 추가
            if date_str and len(date_str) <= 6:
                date_str = f"2026.{date_str}"
                
            score_str = f" [{score_match.group(0).replace(' ', '')}]" if score_match else ""
            
            if date_str or score_str:
                return f"최근: {date_str}{score_str}"
        
        return "데이터 확인 중"
    except:
        return "일시적 지연"

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    # 캐시 확인 (30분 이내 검색 데이터 재사용)
    now = time.time()
    if team_name in cache:
        exp, data = cache[team_name]
        if now < exp:
            return jsonify({"status": "success", "results": data, "from_cache": True})

    # 5대 사이트 동시 채굴 (네임드 추가)
    results = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name)}+일정", "match_info": get_refined_data(team_name, "sports.news.naver.com")},
        {"site": "네임드(Named)", "url": f"https://www.google.com/search?q=site:named.net+{urllib.parse.quote(team_name)}", "match_info": get_refined_data(team_name, "named.net")},
        {"site": "럭스코어", "url": f"https://kr.top-esport.com/search.php?q={urllib.parse.quote(team_name)}", "match_info": get_refined_data(team_name, "kr.top-esport.com")},
        {"site": "플래시스코어", "url": f"https://www.flashscore.co.kr/search/?q={urllib.parse.quote(team_name)}", "match_info": get_refined_data(team_name, "flashscore.co.kr")},
        {"site": "AI스코어", "url": f"https://www.aiscore.com/ko/search/{urllib.parse.quote(team_name)}", "match_info": get_refined_data(team_name, "aiscore.com")}
    ]

    # 캐시 저장 (1800초 = 30분)
    cache[team_name] = (now + 1800, results)

    return jsonify({"status": "success", "results": results, "from_cache": False})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
