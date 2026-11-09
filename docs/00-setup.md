# 0. 환경 구성

교재는 이 웹사이트에서 그대로 읽으면 된다. 아래는 **실습을 위한 준비**다.

## 실습 파일 받기

PowerShell을 열고 실행한다. 이미 받아 둔 폴더가 있으면 `cd`만 한다.

```powershell
git clone https://github.com/toxh13/pipeline-course-sample
cd pipeline-course-sample
```

## 가상환경 만들기

처음 한 번만 실행한다.

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 실습 채점

터미널을 새로 열 때마다 가상환경을 먼저 켠다.

```powershell
.venv\Scripts\activate
pytest labs/01-what-is-pipeline -k todo1
```
