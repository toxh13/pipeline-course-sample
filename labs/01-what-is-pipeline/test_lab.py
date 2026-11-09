"""1장 채점. TODO 하나만 보려면: pytest labs/01-what-is-pipeline -k todo1"""
import csv
from pathlib import Path

DATA = Path(__file__).parent / "data" / "documents.csv"


def row(repo, path, title="제목"):
    return {"repo": repo, "path": path, "title": title, "updated_at": "2026-01-01"}


def test_todo1_extract_reads_every_row(lab):
    with open(DATA, encoding="utf-8", newline="") as f:
        expected = sum(1 for _ in csv.reader(f)) - 1  # 머리글 제외
    rows = lab.extract(DATA)
    assert len(rows) == expected, "CSV의 데이터 행을 전부 읽어야 한다"


def test_todo1_extract_returns_dicts_with_korean(lab):
    first = lab.extract(DATA)[0]
    assert isinstance(first, dict), "행 하나는 딕셔너리여야 한다. csv.DictReader를 쓴다"
    assert first["repo"] == "alpha-shop"
    assert first["title"] == "쇼핑몰 소개", "한글이 깨졌다면 encoding='utf-8'을 확인한다"


def test_todo2_rejects_blank_title(lab):
    good, rejected = lab.clean([row("a", "x.md", "   "), row("a", "y.md", "")])
    assert good == [], "제목이 비었거나 공백뿐인 행은 통과하면 안 된다. .strip()을 쓴다"
    assert [r["reason"] for r in rejected] == ["제목 없음", "제목 없음"]


def test_todo2_rejects_duplicate_and_keeps_first(lab):
    first = row("a", "x.md", "처음")
    good, rejected = lab.clean([first, row("a", "x.md", "나중")])
    assert good == [first], "같은 문서는 처음 나온 행만 남긴다"
    assert rejected[0]["reason"] == "중복"
    assert rejected[0]["title"] == "나중", "거부한 행의 원래 내용을 유지하고 reason만 더한다"


def test_todo2_same_path_in_other_repo_is_not_duplicate(lab):
    good, rejected = lab.clean([row("a", "README.md"), row("b", "README.md")])
    assert len(good) == 2 and rejected == [], "중복 판단은 path만이 아니라 (repo, path)로 한다"


def test_todo2_counts_add_up_on_real_input(lab):
    rows = lab.extract(DATA)
    good, rejected = lab.clean(rows)
    assert len(good) + len(rejected) == len(rows), "통과 + 거부 = 입력이어야 한다. 말없이 사라진 행이 있다"
    assert (len(good), len(rejected)) == (4, 2)


def test_todo3_counts_by_repo(lab):
    rows = [row("a", "1.md"), row("a", "2.md"), row("b", "1.md")]
    assert lab.summarize(rows) == {"a": 2, "b": 1}


def test_todo3_empty_input(lab):
    assert lab.summarize([]) == {}, "입력이 없으면 빈 딕셔너리를 돌려준다"


def test_todo4_writes_note_sorted(lab, tmp_path):
    out = tmp_path / "new" / "wiki.md"
    lab.load({"b": 1, "a": 2}, out)
    assert out.exists(), "폴더가 없어도 파일을 만들어야 한다. mkdir(parents=True, exist_ok=True)"
    assert out.read_text(encoding="utf-8").splitlines() == [
        "# 내 프로젝트 지식 저장고",
        "",
        "- a: 문서 2개",
        "- b: 문서 1개",
    ], "프로젝트는 이름순이고 형식은 '- 이름: 문서 N개'이다"


def test_todo4_whole_pipeline(lab, tmp_path, capsys):
    out = tmp_path / "wiki.md"
    summary = lab.run_pipeline(DATA, out)
    assert summary == {"alpha-shop": 2, "beta-blog": 1, "gamma-bot": 1}
    assert "통과 4건, 거부 2건" in capsys.readouterr().out
    assert "- alpha-shop: 문서 2개" in out.read_text(encoding="utf-8")
