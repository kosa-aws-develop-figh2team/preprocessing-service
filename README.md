# 📄 preprocessing-service
> **문서 전처리 API 서비스**  
> S3에 저장된 PDF, HWP 등 문서 파일을 텍스트로 변환하고, 이를 청크 단위로 분할하는 FastAPI 기반의 전처리 API 서버입니다.


## ✅ 개요
이 서비스는 다음과 같은 두 가지 API를 제공합니다:

1. `POST /process/convert`:  
   S3에 저장된 문서 파일 경로를 받아 텍스트로 변환합니다.
2. `POST /process/chunk`:  
   긴 텍스트를 적절한 크기의 청크 리스트로 분할합니다.

이 서비스는 RAG 시스템에서 문서 기반 질문 응답의 전처리 단계로 사용됩니다.

### ⏳ 과정 요약
```
[S3 원본 파일 다운로드]
      ↓
[확장자 확인 후 텍스트 변환]
      ↓
[변환된 텍스트 → S3 중간 저장 (e.g. txt/)]
      ↓
[텍스트 → 청킹 리스트]
      ↓
[청크 리스트 → S3 중간 저장 (e.g. chunks/)]
      ↓
[DynamoDB 상태 기록 (성공/실패)]
```

## 🧩 기능 명세
### 📑 1. 문서 텍스트 변환 API

- **Endpoint**: `POST /process/convert`
- **Request**:
```json
{
  "s3_file_path": "s3://my-bucket/input/abc.pdf"
}
```
- **Response**:
```json
{
  "txt_text": "청년 정책은..."
}
```
- Status Codes:
    - 200 OK: 변환 성공
    - 400 Bad Request: 잘못된 입력
    - 500 Internal Server Error: 내부 오류
- 비고: pdf2txt, hwp-parser 등의 변환기 사용 예정

### ✂️ 2. 텍스트 청킹 API

- **Endpoint**: `POST /process/chunk`
- **Request**:
```json
{
  "txt_text": "청년 정책은..."
}
```
- **Response**:
```json
{
  "chunk_list": [
    "청년 정책은...",
    "다양한 방식으로..."
  ]
}
```
- Status Codes:
    - 200 OK: 변환 성공
    - 400 Bad Request: 요청 오류
    - 500 Internal Server Error: 내부 오류


## 🚀 로컬 실행 방법
```bash
# 1. .venv 환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 2. 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt

# 3. pyhwp 별도 설치
pip install pyhwp

# 4. 서버 실행
uvicorn main:app --port 5100
```

## 🐳 Docker로 빌드 & 실행
```bash
# 이미지 빌드
docker build -t preprocessing-service .

# 컨테이너 실행
docker run --env-file .env -p 5100:5100 preprocessing-service
```
### 참고) .env 항목
```
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
S3_BUCKET=
```

## ⚙️ CI/CD (ECR 배포 - CD 구현 전)
GitHub Actions를 활용하여 main 브랜치에 push 시 AWS ECR로 자동 배포됩니다.
- ECR:
    - Repository: preprocessing-service
    - Tag: Git SHA 또는 latest
> 📦 .github/workflows/deploy.yml 참고

## 🛠️ TODO
- PDF/HWP 파일 처리 모듈 연결 (pdfminer, pyhwp, etc)
- 문서 유형 자동 감지 및 변환 분기 처리
- 슬라이딩 청크 알고리즘 고도화
- 로그 및 예외 처리 개선

## 📁 디렉토리 구조
(작성 중)