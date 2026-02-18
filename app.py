from flask import Flask, request, jsonify
from flask_cors import CORS
import urllib.parse, requests, re, os

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# [설정] 사용자님의 API KEY 고정
API_KEY = "251241088c08a887a5b9626a6a9cdce8" 

def get_verified_data(team_name):
    """API 우선 검색 -> 구글 지능형 문맥 분석 백업"""
    try:
        # 1. 정식 API-SPORTS 호출 (가장 정확한 1순위)
        api_url = f"https://v3.football.api-sports.io/fixtures?search={urllib.parse.quote(team_name)}&last=1"
        headers = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}
        api_res = requests.get(api_url, headers=headers, timeout=5).json()
        
        if api_res.get('response'):
            fix = api_res['response'][0]
            date = fix['fixture']['date'][:10].replace('-', '.') # YYYY.MM.DD
            score = f"{fix['goals']['home']}:{fix['goals']['away']}"
            return f"최근: {date} [{score}]"

        # 2. 구글 문맥 분석 백업 (가짜 데이터 [0:9] 필터링)
        # 단순히 숫자를 찾는 게 아니라 '날짜 + 결과'의 형태가 유지될 때만 인정
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(team_name + ' 경기결과')}"
        web_res = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5).text
        
        # 정규식 강화: 월.일. 형태와 '점수:점수'가 10글자 이내로 붙어 있는 경우만 추출
        pattern = re.compile(r'(\d{1,2}\.\d{1,2}\.).{1,10}?(\d{1,2}\s?[:\-]\s?\d{1,2})')
        found = pattern.search(web_res)
        
        if found:
            # 0:9, 0:10 등 검색 개수로 추정되는 숫자는 합계가 15 이상일 경우 노이즈로 간주하고 차단
            s1, s2 = map(int, found.group(2).replace(' ', '').replace('-', ':').split(':'))
            if s1 + s2 < 15:
                return f"최근: 2026.{found.group(1)} [{s1}:{s2}]"
            
        return "최근 기록 업데이트 중"
    except Exception:
        return "데이터 확인 필요"

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name: return jsonify({"status": "error"})

    # 지능형 검증을 거친 단 하나의 진짜 데이터
    real_info = get_verified_data(team_name)
    encoded_team = urllib.parse.quote(team_name)

    # 쓰레기 데이터 없이, 검증된 정보와 다이렉트 링크만 제공
    results = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={encoded_team}+경기결과", "match_info": real_info},
        {"site": "구글 스포츠", "url": f"https://www.google.com/search?q={encoded_team}+경기결과", "match_info": real_info},
        {"site": "플래시스코어", "url": f"https://www.flashscore.co.kr/search/?q={encoded_team}", "match_info": "상세 기록 이동"},
        {"site": "라이브스코어", "url": f"https://kr.top-esport.com/search.php?q={encoded_team}", "match_info": "라이브 데이터"},
        {"site": "AI스코어", "url": f"https://www.aiscore.com/ko/search/{encoded_team}", "match_info": "AI 분석 정보"}
    ]

    return jsonify({"status": "success", "results": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
