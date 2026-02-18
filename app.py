from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search():
    team_name = request.args.get('team')
    # 실제 스크래핑 로직은 여기에 추가될 예정입니다.
    # 지금은 연결 확인용 가짜 데이터를 보내줄게요.
    result = {
        "status": "success",
        "team": team_name,
        "message": f"{team_name}의 경기 결과를 찾고 있습니다..."
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
