from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import urllib.parse
import requests
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

def get_best_date(team_name):
    try:
        query = urllib.parse.quote(f"{team_name} 경기일정")
        url = f"https://search.naver.com/search.naver?query={query}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        res = requests.get(url, headers=headers, timeout=5)
        
        if res.status_code == 200:
            content = res.text
            # 1. 02.11.(수) 또는 2.11. 형태만 엄격하게 추출
            date_matches = re.findall(r'(\d{1,2}\.\s?\d{1,2}\.\s?(?:\([월화수목금토일]\))?)', content)
            
            if date_matches:
                # 중복 제거
                unique_dates = list(set([d.strip() for d in date_matches]))
                
                # 오늘 날짜 정보 (2026년 2월 18일 기준)
                today_month = 2
                
                # 2. 오늘 날짜(2월)와 가장 가까운 달의 날짜를 우선적으로 찾음
                # 28.12. 같은 엉뚱한 데이터를 거르기 위해 월(Month) 범위를 1~12로 제한
                valid_dates = []
                for d in unique_dates:
                    month_part = int(d.split('.')[0])
                    if 1 <= month_part <= 12:
                        # 오늘 달(2월)과 차이가 적은 순서대로 후보군 등록
                        valid_dates.append((abs(month_part - today_month), d))
                
                if valid_dates:
                    # 차이가 가장 적은(가장 현재 시점과 가까운) 날짜 반환
                    valid_dates.sort()
                    return valid_dates[0][1], "success"
            
            if any(word in content for word in ["종료", "시즌 오프", "일정이 없습니다"]):
                return None, "off_season"
        return None, "not_found"
    except:
        return None, "error"

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    if not team_name:
        return jsonify({"status": "error", "message": "팀명을 입력해주세요."})

    match_date, status = get_best_date(team_name)
    
    # [깔끔한 텍스트로 수정] 날짜 뒤의 추가 문구 제거
    if status == "success":
        display_text = f"최근: {match_date}"
    elif status == "off_season":
        display_text = "시즌 종료/일정 없음"
    else:
        display_text = "일정 확인 필요"

    # 모든 사이트에 군더더기 없이 깔끔한 날짜만 전달
    search_targets = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name)}+경기결과", "match_info": display_text},
        {"site": "구글 스포츠", "url": f"https://www.google.com/search?q={urllib.parse.quote(team_name)}+경기결과", "match_info": display_text},
        {"site": "플래시스코어", "url": f"https://www.google.com/search?q=site:flashscore.co.kr+{urllib.parse.quote(team_name)}", "match_info": display_text},
        {"site": "라이브스코어", "url": f"https://www.google.com/search?q=site:livescore.co.kr+{urllib.parse.quote(team_name)}", "match_info": display_text},
        {"site": "AI스코어", "url": f"https://www.google.com/search?q=site:aiscore.com+{urllib.parse.quote(team_name)}", "match_info": display_text}
    ]

    return jsonify({"status": "success", "results": search_targets})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
