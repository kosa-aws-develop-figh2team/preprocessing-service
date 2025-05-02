import os
import requests
import dotenv
import logging

dotenv.load_dotenv()

# 환경변수 읽기
EMBED_API_URL = os.getenv("EMBED_API_URL")
# EMBED_API_PORT = os.getenv("EMBED_API_PORT", "5001")  # 기본값 5001
FULL_EMBED_API_URL = f"http://{EMBED_API_URL}/embed/chunks"

# 로깅 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def save_chunk_vectordb(chunk_list, service_id):
    """
    청크 리스트와 서비스 ID를 /embed/chunks 엔드포인트로 POST 전송
    """
    payload = {
        "chunk_list": chunk_list,
        "service_id": service_id
    }

    try:
        logger.info(f"🚀 청크 데이터 저장 요청: {FULL_EMBED_API_URL}")
        response = requests.post(FULL_EMBED_API_URL, json=payload, timeout=100)

        if response.status_code == 200:
            logger.info("✅ 청크 데이터 저장 성공")
        else:
            logger.error(f"❌ 청크 데이터 저장 실패: {response.status_code} - {response.text}")
            response.raise_for_status()

    except requests.exceptions.RequestException as e:
        logger.exception(f"❌ 청크 데이터 저장 요청 중 오류 발생: {str(e)}")
        raise