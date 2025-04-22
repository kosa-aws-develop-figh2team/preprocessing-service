import boto3
from datetime import datetime
from typing import Optional, List, Union
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
    vector_ids: Optional[List[str]] = None,
    error: Optional[str] = "",
    retry_count: int = 0,
    source: Optional[str] = ""
):
    try:
        timestamp = datetime.utcnow().isoformat()

        # SET 블록 구성
        update_parts = [
            "#s = :step",
            "#st = :status",
            "#t = :timestamp",
            "#e = :error",
            "#r = :retry",
            "#src = :source"
        ]
        expression_values = {
            ":step": step,
            ":status": status,
            ":timestamp": timestamp,
            ":error": error,
            ":retry": retry_count,
            ":source": source,
            ":empty_list": []
        }
        expression_names = {
            "#s": "step",
            "#st": "status",
            "#t": "timestamp",
            "#e": "error_message",
            "#r": "retry_count",
            "#src": "source"
        }
        if vector_ids is not None:
            update_parts.append("#v = :vector_ids")
            expression_values[":vector_ids"] = vector_ids
            expression_names["#v"] = "vector_ids"

        update_expression = (
            f"SET {', '.join(update_parts)}, "
            "#h = list_append(if_not_exists(#h, :empty_list), :history_entry_list)"
        )
        expression_names["#h"] = "status_history"
        expression_values[":history_entry_list"] = [{
            "step": step,
            "status": status,
            "timestamp": timestamp,
            "error_message": error
        }]

        table.update_item(
            Key={"service_id": service_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names
        )

        logger.info(f"[DynamoDB] 상태 갱신 완료 - {service_id} / step: {step} / status: {status}")
    except Exception as e:
        logger.error(f"[DynamoDB] 상태 갱신 실패: {str(e)}")


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