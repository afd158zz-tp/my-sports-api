from flask import Flask, request, jsonify
from flask_cors import CORS
import urllib.parse, requests, re, os

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# [필독] 사용자님이 직접 찾은 API KEY를 여기에 정확히 고정했습니다.
API_KEY = "251241088c08a887a5b9626a6a9cdce8" 

def get_pro_match_data(team_name):
    """구글의 검색 지능과 API의 정확도를 결합한 하이브리드 추출"""
    try:
        # 1. API 우선순위 (영문 변환 없이도 검색 가능한 search 파라미터 활용)
        api_url = f"https://v3.football.api-sports.io/fixtures?search={urllib.parse.quote(team_name)}&last=1"
        headers = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}
        api_res = requests.get(api_url, headers=headers, timeout=5).json()
        
        # API 성공 시 최우선 노출
        if api_res.get('response'):
            fix = api_res['response'][0]
            # 날짜를 한국인이 보기 편한 2026.02.18 형태로 가공
            date = fix['fixture']['date'][:10].replace('-', '.')
            score = f"{fix['goals']['home']}:{fix['goals']['away']}"
            return f"최근: {date} [{score}]"

        # 2. 구글 정밀 스캔 (API 실패 시 작동하는 백업)
        # 단순히 0:10 같은 숫자를 가져오지 않도록 '경기결과' 키워드와 날짜 패턴 강제 결합
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(team_name + ' 경기결과')}"
        web_res = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5).text
        
        # [0:9] 같은 노이즈를 피하기 위해 "날짜 + (점수:점수)" 형태만 정밀 타격
        refined_pattern = re.compile(r'(\d{1,2}\.\d{1,2}\.).*?(\d{1,2}\s?[:\-]\s?\d{1,2})')
        found = refined_pattern.search(web_res)
        
        if found:
            return f"최근: 2026.{found.group(1)} [{found.group(2).replace(' ', '')}]"
            
        return "최신 경기 정보 확인 중"
    except Exception as e:
        return "데이터 연결 대기"

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name: return jsonify({"status": "error"})

    match_info = get_pro_match_data(team_name)
    encoded_team = urllib.parse.quote(team_name)

    # 링크 정보와 경기 결과 데이터를 명확히 분리하여 사용자에게 제공
    results = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={encoded_team}+경기결과", "match_info": match_info},
        {"site": "구글 스포츠", "url": f"https://www.google.com/search?q={encoded_team}+경기결과", "match_info": match_info},
        {"site": "플래시스코어", "url": f"https://www.flashscore.co.kr/search/?q={encoded_team}", "match_info": "상세 스코어 확인"},
        {"site": "라이브스코어", "url": f"https://kr.top-esport.com/search.php?q={encoded_team}", "match_info": "라이브 데이터 보기"},
        {"site": "AI스코어", "url": f"https://www.aiscore.com/ko/search/{encoded_team}", "match_info": "AI 데이터 분석"}
    ]

    return jsonify({"status": "success", "results": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
