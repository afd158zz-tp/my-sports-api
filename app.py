from flask import Flask, request, jsonify
from flask_cors import CORS
import urllib.parse, requests, re, os

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

def get_direct_links(team_name):
    encoded_team = urllib.parse.quote(team_name)
    # 각 사이트별 실제 검색 결과 페이지 URL (사용자를 이리로 바로 보냅니다)
    return {
        "naver": f"https://search.naver.com/search.naver?query={encoded_team}+경기결과",
        "named": f"https://www.google.com/search?q=site:named.net+{encoded_team}+경기",
        "lux": f"https://kr.top-esport.com/search.php?q={encoded_team}",
        "flash": f"https://www.flashscore.co.kr/search/?q={encoded_team}",
        "ai": f"https://www.aiscore.com/ko/search/{encoded_team}"
    }

def scrape_match_info(team_name, site_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
        res = requests.get(site_url, headers=headers, timeout=5)
        if res.status_code != 200: return "상세 페이지 확인"
        
        # [데이터 추출 로직] 날짜와 점수가 붙어 있는 것만 골라내기
        content = res.text
        match = re.search(r'(\d{1,2}\.\d{1,2}\.).*?(\d{1,2}\s?[:\-]\s?\d{1,2})', content)
        if match:
            return f"최근: {match.group(1)} [{match.group(2).replace(' ', '')}]"
        return "경기 정보 요약 확인"
    except:
        return "클릭하여 확인"

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name: return jsonify({"status": "error"})

    links = get_direct_links(team_name)
    
    # 데이터 추출 + 무조건 생성되는 바로가기 링크
    results = [
        {"site": "네이버 스포츠", "url": links["naver"], "match_info": scrape_match_info(team_name, links["naver"])},
        {"site": "네임드(Named)", "url": links["named"], "match_info": scrape_match_info(team_name, links["named"])},
        {"site": "럭스코어", "url": links["lux"], "match_info": scrape_match_info(team_name, links["lux"])},
        {"site": "플래시스코어", "url": links["flash"], "match_info": "실시간 데이터 확인"},
        {"site": "AI스코어", "url": links["ai"], "match_info": "분석 데이터 확인"}
    ]

    return jsonify({"status": "success", "results": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
