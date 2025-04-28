# 📄 preprocessing-service
> **문서 전처리 서비스**  
> S3에 저장된 PDF, HWP 등 문서 파일을 텍스트로 변환하고, 이를 청크 단위로 분할하고 저장하는 Lambda 코드입니다.


## ✅ 개요
이 서비스는 다음과 같은 기능을 제공합니다.

> DynamoDB에 step "standby" -> Amazon lambda 서비스에서 해당 열을 읽고 txt, 문서 파일 저장

이 서비스는 RAG 시스템에서 문서 전처리 단계로 사용됩니다.

### ⏳ 과정 요약
```
[DynamoDB Stream 이벤트 수신]
      ↓
[step이 standby인 레코드 필터링]
      ↓
[S3에서 파일 다운로드]
      ↓
[로컬에 파일 저장 (tmp 디렉토리)]
      ↓
[파일 확장자에 따라 텍스트 변환]
      ↓
[텍스트 전처리 (clean_txt 처리)]
      ↓
[텍스트를 청크 리스트로 분할]
      ↓
[청크 리스트를 벡터 DB에 저장 (임베딩 API 호출)]
      ↓
[DynamoDB에 각 단계별 상태(success/failed) 기록]
```

## 🚀 로컬 테스트 방법
```bash
# 1. .venv 환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 2. 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt

# 3. pyhwp 별도 설치
pip install pyhwp

# 4. 실행
# .test/tmp/sample.pdf 경로에 파일이 있어야함.
python .test/test.py 
```

### 참고) .env 항목
```
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
S3_BUCKET=
EMBED_API_URL=
EMBED_API_PORT=
```

## ⚙️ CI/CD (ECR 배포 - CD 구현 전)
GitHub Actions를 활용하여 main 브랜치에 push 시 AWS Lambda 함수로 자동 배포됩니다.
- Lambda:
  - 이름: preprocessing-service
  - 런타임: Python 3.9
  - 핸들러: lambda_function.lambda_handler
- 빌드 방식:
  - 필요한 코드(lambda_function.py, utils/)와 라이브러리(site-packages/)를 zip으로 묶어 업로드합니다.
> 📦 .github/workflows/deploy.yml 참고

## 🛠️ TODO
- PDF/HWP 파일 처리 모듈 연결 (pdfminer, pyhwp, etc)
- 문서 유형 자동 감지 및 변환 분기 처리
- 슬라이딩 청크 알고리즘 고도화
- 로그 및 예외 처리 개선

## 📁 디렉토리 구조
```
.
├── README.md
├── lambda_function.py
├── requirements.txt
├── utils/
│   ├── chunker.py
│   ├── converter.py
│   ├── dynamodb_logger.py
│   ├── embed.py
│   └── s3_handler.py
├── site-packages/   # Lambda 배포용 라이브러리
└── tmp/             # 테스트용 파일 (배포 제외)
```