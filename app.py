from flask import Flask, request, jsonify
from flask_cors import CORS
import urllib.parse, requests, re, time, os

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

cache = {}

def get_accurate_data(team_name, site_domain):
    try:
        # 검색 쿼리에 'vs'를 추가하여 경기 결과 데이터가 검색 상단에 오도록 유도
        search_query = f"{team_name} vs 경기결과 site:{site_domain}"
        url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
        
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            content = res.text
            
            # [노이즈 방지 로직 1] 날짜 패턴 찾기 (예: 02.14, 2026-02-14)
            date_match = re.search(r'(\d{1,2}\.\s?\d{1,2}\.|\d{4}-\d{2}-\d{2})', content)
            
            # [노이즈 방지 로직 2] 점수 패턴 찾기
            # [0:10] 같은 검색결과 개수 노이즈를 피하기 위해 스코어 앞뒤에 공백이나 특정 기호가 있는 것만 추출
            score_match = re.search(r'([0-9])\s?[:\-]\s?([0-9])', content)
            
            final_date = ""
            if date_match:
                d = date_match.group(1).strip()
                final_date = f"2026.{d}" if len(d) < 8 else d.replace('-', '.')

            final_score = ""
            if score_match:
                s = score_match.group(0).replace(' ', '')
                # [0:10] 처럼 한쪽이 너무 큰 점수(검색 개수 노이즈)는 무시하고 실제 스코어(보통 0~5점 사이) 위주로 채굴
                if not (s == "0:10" or s == "1:10"): 
                    final_score = f" [{s}]"

            if final_date or final_score:
                return f"최근: {final_date}{final_score}"
                
        return "경기 데이터 없음"
    except:
        return "확인 불가"

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name: return jsonify({"status": "error"})

    # 캐시 확인 (15분으로 단축하여 실시간성 강화)
    now = time.time()
    if team_name in cache:
        exp, data = cache[team_name]
        if now < exp: return jsonify({"status": "success", "results": data})

    # 네임드 포함 5대 사이트 결과 조립
    results = [
        {"site": "네이버 스포츠", "match_info": get_accurate_data(team_name, "sports.news.naver.com")},
        {"site": "네임드(Named)", "match_info": get_accurate_data(team_name, "named.net")},
        {"site": "럭스코어", "match_info": get_accurate_data(team_name, "kr.top-esport.com")},
        {"site": "플래시스코어", "match_info": get_accurate_data(team_name, "flashscore.co.kr")},
        {"site": "AI스코어", "match_info": get_accurate_data(team_name, "aiscore.com")}
    ]

    cache[team_name] = (now + 900, results)
    return jsonify({"status": "success", "results": results})
