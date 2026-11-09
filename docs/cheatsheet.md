# 치트시트

| 단계 | 질문 | 이번 실습의 함수 |
|---|---|---|
| 수집 | 어디서 읽어 오나? | `extract` |
| 정제 | 무엇을 거부하나? | `clean` |
| 변환 | 어떤 모양으로 바꾸나? | `summarize` |
| 적재 | 어디에 저장하나? | `load` |

**확인 공식:** 통과 건수 + 거부 건수 = 수집 건수

```python
with open(path, encoding="utf-8", newline="") as f:   # CSV 읽기
    rows = list(csv.DictReader(f))

key = (row["repo"], row["path"])                       # 같은 문서인지 판단하는 키
```
