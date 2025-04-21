# 📦 1. 기본 Python 환경
FROM python:3.11-slim

# 🛠️ 2. 시스템 패키지 설치 (hwp5txt 및 기타 필요 도구)
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libgl1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    poppler-utils \
    curl \
    unzip && \
    rm -rf /var/lib/apt/lists/*

# 🧩 3. hwp5txt 설치 (공식 빌드된 바이너리 사용)
RUN curl -L -o /usr/local/bin/hwp5txt https://github.com/mete0r/hwp5txt/releases/download/v0.2.4/hwp5txt && \
    chmod +x /usr/local/bin/hwp5txt

# 🧪 4. 로컬에서 PATH 인식 테스트
RUN hwp5txt --help || echo "hwp5txt 설치 실패 시 확인 필요"

# 🐍 5. Python 기본 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 🗂️ 6. 프로젝트 복사
WORKDIR /app
COPY ./utils /app/utils
COPY ./main.py /app
COPY ./requirements.txt /app

# 📦 7. Python 패키지 설치
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 🔓 8. 포트 개방
EXPOSE 5100

# 🚀 9. FastAPI 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5100"]