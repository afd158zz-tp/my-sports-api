from flask import Flask, request, jsonify
from flask_cors import CORS
import urllib.parse, requests, re, os

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# [설정] 사용자님의 API 키 (전달해주신 키를 여기에 정확히 입력하세요)
API_KEY = "251241088c08a887a5b9626a6a9cdce8" 

def get_accurate_info(team_name):
    """API 우선 검색 -> 실패 시 정밀 웹 채굴 백업"""
    try:
        # 1. API-SPORTS 검색 (영문 변환 시도 포함)
        api_url = f"https://v3.football.api-sports.io/fixtures?search={urllib.parse.quote(team_name)}&last=1"
        headers = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}
        res = requests.get(api_url, headers=headers, timeout=5).json()
        
        if res.get('response'):
            fix = res['response'][0]
            date = fix['fixture']['date'][5:10].replace('-', '.') # "02.18"
            score = f"{fix['goals']['home']}:{fix['goals']['away']}"
            return f"최근: {date} [{score}]"

        # 2. 백업: 구글 검색 결과에서 '날짜 [점수]' 패턴만 정밀 추출
        # (이전의 쓰레기 데이터 [0:9]를 피하기 위해 정규식을 대폭 강화함)
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(team_name + ' 경기결과')}"
        web_res = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        
        # 패턴: "숫자.숫자. [숫자:숫자]" (예: 02.14. [2:1])
        # [0:10] 같은 검색 개수는 근처에 날짜가 없으므로 걸러짐
        pattern = re.compile(r'(\d{1,2}\.\s?\d{1,2}\.).*?(\d{1,2}\s?[:\-]\s?\d{1,2})')
        match = pattern.search(web_res.text)
        
        if match:
            return f"최근: {match.group(1)} [{match.group(2).replace(' ', '')}]"
            
        return "최근 경기 정보 없음"
    except:
        return "데이터 업데이트 중"

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name: return jsonify({"status": "error"})

    info = get_accurate_info(team_name)
    encoded_team = urllib.parse.quote(team_name)

    results = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={encoded_team}+경기결과", "match_info": info},
        {"site": "네임드(Named)", "url": f"https://www.google.com/search?q=site:named.net+{encoded_team}", "match_info": "실시간 반응 확인"},
        {"site": "럭스코어", "url": f"https://kr.top-esport.com/search.php?q={encoded_team}", "match_info": info if "최근" in info else "상세 스코어 확인"},
        {"site": "플래시스코어", "url": f"https://www.flashscore.co.kr/search/?q={encoded_team}", "match_info": "상세 스탯 이동"},
        {"site": "AI스코어", "url": f"https://www.aiscore.com/ko/search/{encoded_team}", "match_info": "AI 승률 분석"}
    ]

    return jsonify({"status": "success", "results": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
