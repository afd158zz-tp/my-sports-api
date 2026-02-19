import { fetch } from 'wix-fetch';

$w.onReady(function () {
    $w("#btnSearch").onClick(() => searchGame());
    $w("#teamInput").onKeyPress((event) => {
        if (event.key === "Enter") searchGame();
    });
});

async function searchGame() {
    const team = $w("#teamInput").value.trim();
    // 사용자님의 기존 Render 서버 주소를 그대로 사용합니다.
    const url = `https://my-sports-api.onrender.com/search?team=${encodeURIComponent(team)}`;

    if (!team) return;

    $w("#btnSearch").label = "조회 중...";

    try {
        const res = await fetch(url, { method: 'get' });
        const json = await res.json();
        
        $w("#btnSearch").label = "GO";

        if (json.status === "success") {
            const data = json.match_data;

            // 데이터 주입 (기존 ID 유지)
            $w("#txtLeague").text = data.league;
            $w("#txtDate").text = `${data.date} | ${data.time}`;
            $w("#txtHomeTeam").text = data.home_name;
            $w("#txtAwayTeam").text = data.away_name;
            $w("#txtScore").text = data.score;
            $w("#txtStatus").text = data.status;

            if (data.home_logo) $w("#imgHomeLogo").src = data.home_logo;
            if (data.away_logo) $w("#imgAwayLogo").src = data.away_logo;

            // 비공개 해제 (사용자님이 찾으신 해결책)
            const ids = ["#txtLeague", "#txtDate", "#txtHomeTeam", "#txtAwayTeam", "#txtScore", "#txtStatus", "#imgHomeLogo", "#imgAwayLogo"];
            ids.forEach(id => $w(id).show());

        } else {
            alert("검색 결과가 없습니다. (서버 응답 실패)");
        }
    } catch (err) {
        $w("#btnSearch").label = "GO";
        console.error("통신 에러:", err);
    }
}
