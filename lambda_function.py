import json
import logging
import boto3
import os
import requests
from utils.dynamodb_logger import update_metadata
from utils.converter import convert_to_text, handle_txt
from utils.chunker import split_into_chunks
from utils.embed import save_chunk_vectordb

from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"🚀 DynamoDB Stream 이벤트 수신: {json.dumps(event)}")

    for record in event.get('Records', []):
        try:
            # 이벤트 종류 체크 (INSERT, MODIFY 만 처리)
            event_name = record.get('eventName')
            if event_name not in ['INSERT', 'MODIFY']:
                continue

            # NewImage에서 데이터 꺼내기
            new_image = record.get('dynamodb', {}).get('NewImage', {})
            if not new_image:
                continue

            service_id = new_image.get('service_id', {}).get('S')
            file_path = new_image.get('file_path', {}).get('S')
            step = new_image.get('step', {}).get('S')

            if not service_id or not file_path:
                logger.error("❌ service_id 또는 file_path가 누락되었습니다.")
                continue

            if step != "standby":
                logger.info(f"⚡ step이 standby가 아님 (현재: {step}), 처리 건너뜀")
                continue

            logger.info(f"🚀 처리 시작: service_id={service_id}, file_path={file_path}")

            # 1. 파일 다운로드 (URL 방식)
            local_tmp_path = f"/tmp/{os.path.basename(file_path)}"
            try:
                download_file_from_url(file_path, local_tmp_path)
                logger.info(f"✅ 파일 다운로드 완료: {local_tmp_path}")
            except Exception as e:
                logger.exception(f"❌ 파일 다운로드 실패: {str(e)}")
                update_metadata(service_id=service_id, step="download", status="failed", error=str(e))
                continue

            # 2. 파일 텍스트 변환
            try:
                txt_text = convert_to_text(local_tmp_path)
                clean_txt = handle_txt(txt_text)
                update_metadata(service_id=service_id, step="convert", status="success")
                logger.info(f"✅ 파일 텍스트 변환 완료")
            except Exception as e:
                logger.exception(f"❌ 파일 변환 실패: {str(e)}")
                update_metadata(service_id=service_id, step="convert", status="failed", error=str(e))
                continue

            # 3. 텍스트 청킹
            try:
                chunk_list = split_into_chunks(clean_txt)
                update_metadata(service_id=service_id, step="chunk", status="success")
                logger.info(f"✅ 텍스트 청킹 완료: {len(chunk_list)}개 청크 생성")
            except Exception as e:
                logger.exception(f"❌ 텍스트 청킹 실패: {str(e)}")
                update_metadata(service_id=service_id, step="chunk", status="failed", error=str(e))
                continue

            # 4. 청크 데이터 저장
            try:
                save_chunk_vectordb(chunk_list, service_id)
                update_metadata(service_id=service_id, step="save", status="success")
                logger.info(f"✅ 청크 데이터 저장 완료")
            except Exception as e:
                logger.exception(f"❌ 청크 데이터 저장 실패: {str(e)}")
                update_metadata(service_id=service_id, step="save", status="failed", error=str(e))
                continue

        except Exception as e:
            logger.exception(f"❌ 전체 처리 중 알 수 없는 에러 발생: {str(e)}")

    return {
        "statusCode": 200,
        "body": json.dumps("DynamoDB Stream 이벤트 처리 완료")
    }

def download_file_from_url(url: str, local_path: str):
    """
    HTTP/HTTPS URL로부터 파일 다운로드하여 로컬에 저장
    """
    response = requests.get(url)
    response.raise_for_status()  # HTTP 오류 발생 시 예외 던짐

    with open(local_path, 'wb') as f:
        f.write(response.content)