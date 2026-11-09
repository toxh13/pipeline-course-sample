"""실습 채점용 공통 fixture.

기본은 사용자가 채우는 starter를 검사한다.
정답 확인: LAB_TARGET=solution pytest labs/NN-slug

실습 형식마다 fixture가 있다. 쓰지 않는 형식의 라이브러리는 설치하지 않아도 된다.
- lab: starter.py / solution.py 모듈
- db:  인메모리 DuckDB. 실습 폴더의 data/*.csv를 파일 이름과 같은 테이블로 올려 둔다.
       SQL 안의 상대 경로('data/x.csv')는 실습 폴더, 강의 루트 순으로 찾는다
- sql: starter.sql / solution.sql 의 이름 붙은 쿼리 블록(-- name: todo1_xxx)을 db에서 실행
- dbt: starter/ / solution/ dbt 프로젝트를 임시 폴더에서 dbt build 한 결과
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

import pytest


def _target():
    return os.environ.get("LAB_TARGET", "starter")


class Result(NamedTuple):
    columns: list
    rows: list


def _fetch(cursor):
    if cursor.description is None:  # CREATE VIEW처럼 결과가 없는 문장
        return Result([], [])
    return Result([d[0] for d in cursor.description], cursor.fetchall())


def search_path(*dirs):
    """DuckDB file_search_path 값. 같은 폴더가 두 번 들어가면 글롭이 파일을 두 번 읽으므로 중복을 뺀다.

    file_search_path를 걸면 글롭('out/*/*.parquet')은 현재 폴더를 찾지 않는다.
    현재 폴더에 쓴 파일을 글롭으로 읽어야 하면 search_path(Path.cwd(), ...)처럼 맨 앞에 넣는다.
    """
    unique = dict.fromkeys(Path(d).resolve().as_posix() for d in dirs)
    return ",".join(unique)


@pytest.fixture
def lab(request):
    target = _target()
    path = request.path.parent / f"{target}.py"
    spec = importlib.util.spec_from_file_location(f"{path.parent.name}_{target}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def db(request):
    import duckdb

    conn = duckdb.connect()
    conn.execute("SET file_search_path = ?", [search_path(Path.cwd(), request.path.parent, request.config.rootpath)])
    for csv in sorted((request.path.parent / "data").glob("*.csv")):
        conn.read_csv(str(csv)).create(csv.stem)
    yield conn
    conn.close()


class SqlLab:
    """`-- name: 이름` 줄로 나뉜 SQL 파일. 첫 name 줄 앞은 설명으로 보고 버린다."""

    def __init__(self, path, conn):
        self.path = path
        self.conn = conn
        parts = re.split(r"^--\s*name:\s*(\w+)\s*$", path.read_text(encoding="utf-8"), flags=re.M)
        self.queries = {name: body.strip() for name, body in zip(parts[1::2], parts[2::2])}

    def run(self, name):
        if name not in self.queries:
            raise KeyError(f"{self.path.name}에 '-- name: {name}' 블록이 없다. 블록 이름을 바꾸지 말 것")
        return _fetch(self.conn.execute(self.queries[name]))


@pytest.fixture
def sql(request, db):
    return SqlLab(request.path.parent / f"{_target()}.sql", db)


@pytest.fixture
def expected(request):
    """solution.sql의 블록을 새 DB에서 실행한 결과를 돌려주는 함수.

    작은 실습 데이터에서 '목표 결과'와 그대로 비교할 때 쓴다: assert sql.run(b) == expected(b).
    교재 화면의 '목표 결과'도 같은 방식(solution 블록 실행)으로 만든다.
    """
    import duckdb

    conn = duckdb.connect()
    conn.execute("SET file_search_path = ?", [search_path(Path.cwd(), request.path.parent, request.config.rootpath)])
    for csv in sorted((request.path.parent / "data").glob("*.csv")):
        conn.read_csv(str(csv)).create(csv.stem)
    lab = SqlLab(request.path.parent / "solution.sql", conn)
    yield lab.run
    conn.close()


@pytest.fixture
def same(request, sql, db):
    """내 블록과 solution 블록을 같은 데이터에서 실행해 결과가 같은지 본다.

    check(블록, 힌트) 꼴로 부른다. show를 주면 블록을 실행한 뒤 show 쿼리의 결과를 비교한다
    (CREATE TABLE처럼 결과가 없는 블록: show="SELECT * FROM stg_orders ORDER BY order_id").
    양쪽 모두 그 파일의 given_ 블록을 먼저 실행한다. 순서를 비교하려면 블록(또는 show)에 ORDER BY가 있어야 한다.
    """
    import duckdb

    conn = duckdb.connect()
    conn.execute("SET file_search_path = ?", [search_path(Path.cwd(), request.path.parent, request.config.rootpath)])
    for csv in sorted((request.path.parent / "data").glob("*.csv")):
        conn.read_csv(str(csv)).create(csv.stem)
    solution = SqlLab(request.path.parent / "solution.sql", conn)
    for lab in (solution, sql):
        for name in lab.queries:
            if name.startswith("given_"):
                lab.run(name)

    def check(block, hint="", show=None, drop=()):
        for table in drop:  # 블록이 만들 테이블과 같은 이름의 준비 테이블을 지운다 (안 지우면 아무것도 안 해도 통과한다)
            conn.execute(f"DROP TABLE IF EXISTS {table}")
            db.execute(f"DROP TABLE IF EXISTS {table}")
        want = solution.run(block)
        got = sql.run(block)
        if show:
            want, got = _fetch(conn.execute(show)), _fetch(db.execute(show))
        where = f" ({show})" if show else ""
        assert got.columns == want.columns, f"열이 다르다{where}. 목표: {want.columns} / 지금: {got.columns}. {hint}"
        assert len(got.rows) == len(want.rows), f"행 수가 다르다{where}. 목표 {len(want.rows)}행 / 지금 {len(got.rows)}행. {hint}"
        for i, (g, w) in enumerate(zip(got.rows, want.rows), 1):
            assert g == w, f"{i}번째 행이 다르다{where}. 목표: {w} / 지금: {g}. {hint}"

    yield check
    conn.close()


DBT_PROFILE = """lab:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: "{path}"
      schema: main
      threads: 1
"""

DBT_OK = {"success", "pass"}


class DbtBuild:
    def __init__(self, project, proc, conn):
        self.nodes = {}
        self.error = None
        run_results = project / "target" / "run_results.json"
        if run_results.exists():
            for r in json.loads(run_results.read_text(encoding="utf-8"))["results"]:
                # unique_id는 "model.lab.stg_orders", "test.lab.unique_stg_orders_order_id.<해시>" 꼴
                self.nodes[r["unique_id"].split(".")[2]] = (r["status"], r.get("message"))
        if not self.nodes and proc.returncode != 0:
            self.error = (proc.stdout + proc.stderr)[-2000:]
        self.conn = conn

    def failed(self):
        """성공하지 못한 노드(모델·시드·데이터 테스트) 목록. 프로젝트 자체가 깨졌으면 dbt 출력 끝부분."""
        if self.error is not None:
            return [("dbt", "error", self.error)]
        return [(name, status, msg) for name, (status, msg) in self.nodes.items() if status not in DBT_OK]

    def query(self, sql):
        return _fetch(self.conn.execute(sql))


@pytest.fixture(scope="module")
def dbt(request, tmp_path_factory):
    import duckdb

    target = _target()
    work = tmp_path_factory.mktemp(f"dbt_{target}")
    project = work / "project"
    shutil.copytree(request.path.parent / target, project,
                    ignore=shutil.ignore_patterns("target", "logs", "dbt_packages", "*.duckdb"))
    db_path = work / "lab.duckdb"
    (work / "profiles.yml").write_text(DBT_PROFILE.format(path=db_path.as_posix()), encoding="utf-8")

    # 별도 프로세스로 돌린다. Windows에서 dbt는 파일을 시스템 인코딩(cp949)으로 읽어 한글 주석에서 깨지므로
    # PYTHONUTF8=1을 줘야 하고, 이 설정은 이미 떠 있는 파이썬에는 적용되지 않는다.
    env = {**os.environ, "PYTHONUTF8": "1", "DBT_SEND_ANONYMOUS_USAGE_STATS": "false"}
    proc = subprocess.run(
        [sys.executable, "-c", "from dbt.cli.main import cli; cli()", "build",
         "--project-dir", str(project), "--profiles-dir", str(work)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
    )
    conn = duckdb.connect(str(db_path))
    yield DbtBuild(project, proc, conn)
    conn.close()
