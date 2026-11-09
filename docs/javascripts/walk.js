// 데이터가 단계마다 어떻게 바뀌는지 한 화면씩 넘겨 보는 위젯.
(function () {
  const HEAD = ["repo", "path", "title"];
  const ROWS = [
    ["alpha-shop", "README.md", "쇼핑몰 소개"],
    ["alpha-shop", "docs/design.md", "설계 결정"],
    ["alpha-shop", "docs/design.md", "설계 결정"],
    ["beta-blog", "README.md", "(공백 3칸)"],
    ["beta-blog", "docs/deploy.md", "배포 방법"],
    ["gamma-bot", "README.md", "챗봇 소개"],
  ];
  const STEPS = [
    { stage: 0, title: "출발: 원천 파일", say: "documents.csv 파일에 6줄이 있다. 아직 프로그램은 이 내용을 모른다.", kind: "raw" },
    { stage: 1, title: "1. 수집", say: "파일을 읽어 행 6개를 메모리로 가져온다. 내용은 고치지 않는다.", kind: "table", count: "6건" },
    { stage: 2, title: "2. 정제: 제목 검사", say: "4번째 행은 제목이 공백뿐이다. 거부하고 이유를 적어 둔다.", kind: "table", bad: { 3: "제목 없음" }, count: "검사 중" },
    { stage: 2, title: "2. 정제: 중복 검사", say: "3번째 행은 2번째와 repo, path가 같다. 같은 문서이므로 거부한다. gamma-bot의 README.md는 repo가 달라서 통과한다.", kind: "table", bad: { 3: "제목 없음", 2: "중복" }, focus: [1, 2, 5], count: "통과 4건, 거부 2건" },
    { stage: 3, title: "3. 변환", say: "통과한 4건을 프로젝트별로 센다. 행 4개가 프로젝트 3개로 줄어든다.", kind: "summary", count: "프로젝트 3개" },
    { stage: 4, title: "4. 적재", say: "요약을 노트 파일로 저장한다. 이제 옵시디언에서 열어 볼 수 있다.", kind: "note", count: "파일 1개" },
  ];
  const STAGES = ["원천", "수집", "정제", "변환", "적재"];

  function table(step) {
    const bad = step.bad || {};
    const focus = step.focus || [];
    const body = ROWS.map((row, i) => {
      const cls = bad[i] ? "walk-bad" : focus.includes(i) ? "walk-focus" : "";
      const cells = row.map((v) => `<td>${v}</td>`).join("");
      return `<tr class="${cls}">${cells}<td>${bad[i] ? "거부: " + bad[i] : ""}</td></tr>`;
    }).join("");
    return `<table class="walk-table"><thead><tr>${HEAD.map((h) => `<th>${h}</th>`).join("")}<th>결과</th></tr></thead><tbody>${body}</tbody></table>`;
  }

  function view(step) {
    if (step.kind === "raw") {
      const lines = ["repo,path,title,updated_at"].concat(ROWS.map((r) => r.join(",") + ",...")).join("\n");
      return `<pre class="walk-pre">${lines}</pre>`;
    }
    if (step.kind === "summary") {
      return `<table class="walk-table"><thead><tr><th>프로젝트</th><th>문서 수</th></tr></thead><tbody><tr><td>alpha-shop</td><td>2</td></tr><tr><td>beta-blog</td><td>1</td></tr><tr><td>gamma-bot</td><td>1</td></tr></tbody></table>`;
    }
    if (step.kind === "note") {
      return `<pre class="walk-pre"># 내 프로젝트 지식 저장고\n\n- alpha-shop: 문서 2개\n- beta-blog: 문서 1개\n- gamma-bot: 문서 1개</pre>`;
    }
    return table(step);
  }

  function mount(root) {
    if (root.dataset.ready) return;
    root.dataset.ready = "1";
    root.className = "walk";
    let index = 0;
    let timer = null;

    root.innerHTML = `
      <div class="walk-stages"></div>
      <h4 class="walk-title"></h4>
      <p class="walk-say"></p>
      <div class="walk-view"></div>
      <p class="walk-count"></p>
      <div class="walk-buttons">
        <button type="button" class="md-button" data-a="prev">이전</button>
        <button type="button" class="md-button md-button--primary" data-a="next">다음</button>
        <button type="button" class="md-button" data-a="play">자동 재생</button>
        <span class="walk-pos"></span>
      </div>`;
    const $ = (s) => root.querySelector(s);

    function stop() {
      if (timer) clearInterval(timer);
      timer = null;
      $('[data-a="play"]').textContent = "자동 재생";
    }

    function draw() {
      const step = STEPS[index];
      $(".walk-stages").innerHTML = STAGES.map((name, i) =>
        `<span class="walk-stage${i === step.stage ? " on" : i < step.stage ? " done" : ""}">${name}</span>`).join("");
      $(".walk-title").textContent = step.title;
      $(".walk-say").textContent = step.say;
      $(".walk-view").innerHTML = view(step);
      $(".walk-count").textContent = step.count ? "지금 데이터: " + step.count : "";
      $(".walk-pos").textContent = `${index + 1} / ${STEPS.length}`;
      $('[data-a="prev"]').disabled = index === 0;
      $('[data-a="next"]').disabled = index === STEPS.length - 1;
    }

    root.addEventListener("click", (e) => {
      const action = e.target.dataset && e.target.dataset.a;
      if (!action) return;
      if (action === "play") {
        if (timer) return stop();
        if (index === STEPS.length - 1) index = 0;
        draw();
        e.target.textContent = "멈춤";
        timer = setInterval(() => {
          if (index >= STEPS.length - 1) return stop();
          index += 1;
          draw();
        }, 4000);
        return;
      }
      stop();
      index = Math.min(STEPS.length - 1, Math.max(0, index + (action === "next" ? 1 : -1)));
      draw();
    });

    draw();
  }

  function init() {
    const root = document.getElementById("walk-pipeline");
    if (root) mount(root);
  }

  if (window.document$) window.document$.subscribe(init);
  else document.addEventListener("DOMContentLoaded", init);
})();
