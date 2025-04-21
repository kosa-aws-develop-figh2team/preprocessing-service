import boto3
from datetime import datetime
from typing import Optional
import logging
import os
import dotenv
dotenv.load_dotenv() 

# 로깅 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

region = os.getenv("AWS_REGION", "ap-northeast-2")
dynamodb = boto3.resource("dynamodb", region_name=region)
table = dynamodb.Table("ProcessingMetadata")

def update_metadata(
    service_id: str,
    step: str,
    status: str,
    error: Optional[str] = "",
    retry_count: int = 0
):
    """
    처리 상태를 DynamoDB에 기록
    """
    try:
        response = table.put_item(
            Item={
                "service_id": service_id,
                "step": step,
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "error_message": error,
                "retry_count": retry_count
            }
        )
        logger.info(f"[DynamoDB] {service_id} - {step} 단계 상태 기록: {status}")
    except Exception as e:
        logger.error(f"[DynamoDB] 기록 실패: {str(e)}")


def get_metadata(service_id: str) -> dict:
    """
    특정 service_id의 메타데이터 상태 조회
    """
    try:
        response = table.get_item(Key={"service_id": service_id})
        item = response.get("Item")
        if item:
            logger.info(f"[DynamoDB] 메타데이터 조회 성공: {service_id}")
        else:
            logger.warning(f"[DynamoDB] 메타데이터 없음: {service_id}")
        return item or {}
    except Exception as e:
        logger.error(f"[DynamoDB] 조회 실패: {str(e)}")
        return {}