from flask import Flask, request, jsonify
from flask_cors import CORS
import urllib.parse, requests, re, os

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# [설정] 사용자님의 API KEY 고정
API_KEY = "251241088c08a887a5b9626a6a9cdce8" 

def get_pro_match_data(team_name):
    """구글 지능과 API의 정확도를 결합한 하이브리드 추출"""
    try:
        # 1. API 검색 (search 파라미터 최적화)
        api_url = f"https://v3.football.api-sports.io/fixtures?search={urllib.parse.quote(team_name)}&last=1"
        headers = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}
        api_res = requests.get(api_url, headers=headers, timeout=5).json()
        
        if api_res.get('response'):
            fix = api_res['response'][0]
            # 날짜를 한국인이 보기 편한 YYYY.MM.DD 형태로 가공
            date = fix['fixture']['date'][:10].replace('-', '.')
            score = f"{fix['goals']['home']}:{fix['goals']['away']}"
            return f"최근: {date} [{score}]"

        # 2. 구글 정밀 스캔 (API 실패 시 백업)
        # 단순히 숫자를 가져오지 않고 '경기결과' 박스의 정형화된 패턴만 추출
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(team_name + ' 경기결과')}"
        web_res = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5).text
        
        # [0:9] 같은 노이즈 차단을 위해 '날짜 + (점수:점수)' 형태만 정밀 타격
        refined_pattern = re.compile(r'(\d{1,2}\.\s?\d{1,2}\.).*?(\d{1,2}\s?[:\-]\s?\d{1,2})')
        found = refined_pattern.search(web_res)
        
        if found:
            date_str = found.group(1).strip()
            score_str = found.group(2).replace(' ', '')
            return f"최근: 2026.{date_str} [{score_str}]"
            
        return "경기 데이터 없음"
    except Exception:
        return "데이터 확인 중"

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name: return jsonify({"status": "error"})

    # 메인 데이터 추출
    match_info = get_pro_match_data(team_name)
    encoded_team = urllib.parse.quote(team_name)

    # 5대 사이트 통합 결과 (링크와 정보를 일관성 있게 배치)
    results = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={encoded_team}+경기결과", "match_info": match_info},
        {"site": "네임드(Named)", "url": f"https://www.google.com/search?q=site:named.net+{encoded_team}", "match_info": "실시간 반응 확인"},
        {"site": "럭스코어", "url": f"https://kr.top-esport.com/search.php?q={encoded_team}", "match_info": match_info},
        {"site": "플래시스코어", "url": f"https://www.flashscore.co.kr/search/?q={encoded_team}", "match_info": "상세 기록 이동"},
        {"site": "AI스코어", "url": f"https://www.aiscore.com/ko/search/{encoded_team}", "match_info": "AI 승부 예측"}
    ]

    return jsonify({"status": "success", "results": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
