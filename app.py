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
            # 1. 모든 날짜 패턴 추출 (02.11.(수) 또는 02.11. 형태)
            date_matches = re.findall(r'(\d{1,2}\.\s?\d{1,2}\.\s?(?:\([월화수목금토일]\))?)', content)
            
            if date_matches:
                # 중복 제거 및 깔끔하게 정리
                clean_dates = sorted(list(set([d.strip() for d in date_matches])), reverse=True)
                
                # 2. '펴고 접기' 같은 텍스트가 섞인 것 제외하고 진짜 날짜 같은 것 중 맨 위(최신) 선택
                # 보통 네이버 검색 결과 상단에 있는 날짜가 최신입니다.
                for d in clean_dates:
                    if len(d) >= 5: # "2.11." 처럼 최소 5자 이상인 것만 인정
                        return d, "success"
            
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
    
    # [3번 아이디어 기반] 상황별 메시지 결정
    if status == "success":
        display_text = f"최근: {match_date}"
    elif status == "off_season":
        display_text = "시즌 종료 또는 일정 없음"
    else:
        display_text = "일정 확인 (직접 이동)"

    search_targets = [
        {"site": "네이버 스포츠", "url": f"https://search.naver.com/search.naver?query={urllib.parse.quote(team_name)}+경기결과", "match_info": f"{display_text} / 영상&뉴스"},
        {"site": "구글 스포츠", "url": f"https://www.google.com/search?q={urllib.parse.quote(team_name)}+경기결과", "match_info": f"{display_text} / 순위표 확인"},
        {"site": "플래시스코어", "url": f"https://www.google.com/search?q=site:flashscore.co.kr+{urllib.parse.quote(team_name)}", "match_info": f"{display_text} / 세부 데이터"},
        {"site": "라이브스코어", "url": f"https://www.google.com/search?q=site:livescore.co.kr+{urllib.parse.quote(team_name)}", "match_info": f"{display_text} / 통합 전적"},
        {"site": "AI스코어", "url": f"https://www.google.com/search?q=site:aiscore.com+{urllib.parse.quote(team_name)}", "match_info": f"{display_text} / 승률 예측"}
    ]

    return jsonify({"status": "success", "results": search_targets})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
