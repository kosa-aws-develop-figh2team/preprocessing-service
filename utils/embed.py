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

from utils.dynamodb_logger import update_metadata

def save_chunk_vectordb(chunk_list, service_id):
    """
    청크 리스트와 서비스 ID를 /embed/chunks 엔드포인트로 비동기 전송
    성공 여부와 관계없이 Lambda는 즉시 반환하며 상태는 embedding_pending으로 기록
    실패 시 embedding → failed 상태 기록
    """
    payload = {
        "chunk_list": chunk_list,
        "service_id": service_id
    }

    try:
        logger.info(f"🚀 청크 데이터 저장 요청 (비동기): {FULL_EMBED_API_URL}")
        response = requests.post(FULL_EMBED_API_URL, json=payload, timeout=3)

        # 성공 여부와 관계없이 요청이 정상 전송되었으면 pending 상태 기록
        update_metadata(service_id=service_id, step="embedding", status="pending")
        logger.info("✅ 요청 전송 성공 → embedding_pending 상태 기록")

    except requests.exceptions.RequestException as e:
        update_metadata(service_id=service_id, step="embedding", status="failed", error=str(e))
        logger.exception(f"❌ 청크 데이터 저장 요청 실패 → embedding_failed 상태 기록: {str(e)}")
        raise