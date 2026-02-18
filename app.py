from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import urllib.parse
import requests
import re
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# 공통 헤더 (차단 방지)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_luxscore(team_name):
    try:
        # 럭스코어 검색 결과 페이지 직접 접근
        url = f"https://kr.top-esport.com/search.shtml?keyword={urllib.parse.quote(team_name)}"
        res = requests.get(url, headers=HEADERS, timeout=7)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # 럭스코어의 결과 테이블 행 탐색 (검색 결과 리스트의 첫 번째 경기)
            match_row = soup.select_one('.team_li_box') or soup.select_one('.match_item')
            if match_row:
                # 텍스트 내에서 날짜(00-00-00)와 점수(0 - 0) 추출
                text = match_row.get_text(separator=' ')
                date = re.search(r'(\d{2,4}-\d{1,2}-\d{1,2})', text)
                score = re.search(r'(\d{1,2}\s?-\s?\d{1,2})', text)
                
                res_date = date.group(1).replace('-', '.') if date else "날짜미상"
                res_score = f"[{score.group(1).replace(' ', '')}]" if score else ""
                return f"최근: {res_date} {res_score}"
        return "검색결과 없음"
    except:
        return "확인 불가"

def get_naver_direct(team_name):
    try:
        url = f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name + ' 경기결과')}"
        res = requests.get(url, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # 네이버 스포츠 일정/결과 섹션 타겟팅
            match_info = soup.select_one('.lst_schedule') or soup.select_one('.sc_new.cs_common_module')
            if match_info:
                text = match_info.get_text()
                # 날짜와 스코어 패턴 추출
                date = re.search(r'(\d{1,2}\.\d{1,2}\.)', text)
                score = re.search(r'(\d{1,2}\s?:\s?\d{1,2})', text)
                
                res_date = f"2026.{date.group(1)}" if date else "최근 일정"
                res_score = f"[{score.group(1).replace(' ', '')}]" if score else ""
                return f"최근: {res_date} {res_score}"
        return "검색결과 없음"
    except:
        return "확인 불가"

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    # 직접 크롤링 결과 조립
    results = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name)}+경기결과", "match_info": get_naver_direct(team_name)},
        {"site": "럭스코어", "url": f"https://kr.top-esport.com/search.shtml?keyword={urllib.parse.quote(team_name)}", "match_info": get_luxscore(team_name)},
        {"site": "플래시스코어", "url": f"https://www.google.com/search?q=site:flashscore.co.kr+{urllib.parse.quote(team_name)}", "match_info": "상세 페이지 확인"},
        {"site": "AI스코어", "url": f"https://www.google.com/search?q=site:aiscore.com+{urllib.parse.quote(team_name)}", "match_info": "예측 데이터 확인"}
    ]

    return jsonify({"status": "success", "results": results})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
