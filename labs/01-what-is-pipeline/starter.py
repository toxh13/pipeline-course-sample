"""1장 실습: 문서 목록을 읽어 요약 노트를 만드는 파이프라인.

TODO 1~4를 차례로 채운다. 하나 채울 때마다 채점한다.
    pytest labs/01-what-is-pipeline -k todo1
"""
import csv
from pathlib import Path

HERE = Path(__file__).parent


def extract(csv_path):
    """1. 수집: CSV 파일을 읽어 딕셔너리 목록으로 돌려준다.

    돌려줄 값 예: [{"repo": "alpha-shop", "path": "README.md", "title": "...", "updated_at": "..."}, ...]
    """
    # TODO 1: csv.DictReader로 파일을 읽어 list로 돌려준다. encoding="utf-8"을 꼭 쓴다.
    raise NotImplementedError("TODO 1: extract")


def clean(rows):
    """2. 정제: 통과한 행과 거부한 행을 나눠 (good, rejected)로 돌려준다.

    규칙
    - title이 비었거나 공백뿐이면 거부한다. reason은 "제목 없음"
    - repo와 path가 둘 다 같은 행이 이미 있었으면 거부한다. reason은 "중복"
    거부한 행은 원래 내용에 "reason"을 더한 딕셔너리다.
    """
    # TODO 2: 교재의 힌트 순서대로 작성한다.
    raise NotImplementedError("TODO 2: clean")


def summarize(rows):
    """3. 변환: 프로젝트별 문서 수를 딕셔너리로 돌려준다.

    돌려줄 값 예: {"alpha-shop": 2, "beta-blog": 1}
    """
    # TODO 3: rows를 돌면서 row["repo"]별로 센다.
    raise NotImplementedError("TODO 3: summarize")


def load(summary, output_path):
    """4. 적재: 요약을 Markdown 노트로 저장한다.

    파일 내용은 정확히 다음 모양이며, 프로젝트는 이름순이다.

    # 내 프로젝트 지식 저장고

    - alpha-shop: 문서 2개
    - beta-blog: 문서 1개
    """
    # TODO 4: 줄을 만들어 output_path에 utf-8로 저장한다. 폴더가 없으면 먼저 만든다.
    raise NotImplementedError("TODO 4: load")


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
