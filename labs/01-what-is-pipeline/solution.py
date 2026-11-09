"""1장 실습 정답. starter.py와 구조가 같고 TODO만 채웠다."""
import csv
from pathlib import Path

HERE = Path(__file__).parent


def extract(csv_path):
    """1. 수집: CSV 파일을 읽어 딕셔너리 목록으로 돌려준다."""
    with open(csv_path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def clean(rows):
    """2. 정제: 통과한 행과 거부한 행을 나눠 (good, rejected)로 돌려준다."""
    good = []
    rejected = []
    seen = set()
    for row in rows:
        if not row["title"].strip():
            rejected.append({**row, "reason": "제목 없음"})
            continue
        key = (row["repo"], row["path"])
        if key in seen:
            rejected.append({**row, "reason": "중복"})
            continue
        seen.add(key)
        good.append(row)
    return good, rejected


def summarize(rows):
    """3. 변환: 프로젝트별 문서 수를 딕셔너리로 돌려준다."""
    counts = {}
    for row in rows:
        counts[row["repo"]] = counts.get(row["repo"], 0) + 1
    return counts


def load(summary, output_path):
    """4. 적재: 요약을 Markdown 노트로 저장한다."""
    lines = ["# 내 프로젝트 지식 저장고", ""]
    for repo in sorted(summary):
        lines.append(f"- {repo}: 문서 {summary[repo]}개")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_pipeline(csv_path, output_path):
    """네 단계를 순서대로 잇는다. 이 함수는 고치지 않아도 된다."""
    rows = extract(csv_path)
    print(f"[1 수집] {len(rows)}건 읽음")

    good, rejected = clean(rows)
    print(f"[2 정제] 통과 {len(good)}건, 거부 {len(rejected)}건")
    for row in sorted(rejected, key=lambda r: (r["repo"], r["path"])):
        print(f"  거부: {row['repo']}/{row['path']} ({row['reason']})")

    summary = summarize(good)
    print(f"[3 변환] 프로젝트 {len(summary)}개")

    load(summary, output_path)
    print(f"[4 적재] 저장 완료: {Path(output_path).name}")
    return summary


if __name__ == "__main__":
    run_pipeline(HERE / "data" / "documents.csv", HERE / "output" / "wiki.md")
