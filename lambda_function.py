import json
import logging
import boto3
import os
import re
import requests
from utils.dynamodb_logger import update_metadata
from utils.converter import convert_to_text, handle_txt
from utils.chunker import split_into_chunks
from utils.embed import save_chunk_vectordb

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
            # file_path = new_image.get('file_path', {}).get('S')
            step = new_image.get('step', {}).get('S')
            content = new_image.get('content', {}).get('S')

            if not service_id or not content: #or not file_path
                logger.error("❌ service_id 또는 content가 누락되었습니다.")
                continue

            if step != "init":
                logger.info(f"⚡ step이 init이 아님 (현재: {step}), 처리 건너뜀")
                continue

            logger.info(f"🚀 처리 시작: service_id={service_id}, content={content[:100]}")

            # 1. 파일 다운로드
            # try:
            #     local_tmp_path = download_file_from_url(file_path)
            #     logger.info(f"✅ 파일 다운로드 완료: {local_tmp_path}")
            # except Exception as e:
            #     logger.exception(f"❌ 파일 다운로드 실패: {str(e)}")
            #     update_metadata(service_id=service_id, step="download", status="failed", error=str(e))
            #     continue
            

            # 2. 파일 텍스트 변환
            try:
                # txt_text = convert_to_text(local_tmp_path)
                clean_txt = handle_txt(content)
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
            save_chunk_vectordb(chunk_list, service_id)
            update_metadata(service_id=service_id, step="save", status="success")
            logger.info(f"✅ 청크 데이터 저장 전송 완료")

        except Exception as e:
            logger.exception(f"❌ 전체 처리 중 알 수 없는 에러 발생: {str(e)}")

    return {
        "statusCode": 200,
        "body": json.dumps("DynamoDB Stream 이벤트 처리 완료")
    }

def download_file_from_url(url: str, local_dir: str = "/tmp") -> str:
    """
    HTTP/HTTPS URL로부터 파일 다운로드하여 로컬에 저장하고, 저장 경로 반환
    - Content-Disposition 헤더에서 파일명 추출
    - 없으면 Content-Type 보고 확장자 추정
    - 그래도 없으면 URL basename 사용
    """
    response = requests.get(url)
    response.raise_for_status()

    # 1. Content-Disposition에서 filename 찾기
    content_disposition = response.headers.get('Content-Disposition')
    filename = None
    if content_disposition:
        match = re.search(r'filename="(.+)"', content_disposition)
        if match:
            filename = match.group(1)

    # 2. fallback: Content-Type 보고 확장자 추정
    if not filename:
        content_type = response.headers.get('Content-Type', '')
        if 'pdf' in content_type:
            ext = '.pdf'
        elif 'hwp' in content_type:
            ext = '.hwp'
        elif 'msword' in content_type:
            ext = '.doc'
        else:
            ext = ''  # 모를 때

        # URL 기반 이름 추정
        base_name = os.path.basename(url.split("?")[0])
        filename = base_name + ext if not base_name.endswith(ext) else base_name

    if not filename:
        raise ValueError("❌ 파일 이름을 결정할 수 없습니다.")

    local_path = os.path.join(local_dir, filename)

    with open(local_path, 'wb') as f:
        f.write(response.content)

    file_size = os.path.getsize(local_path)
    logger.info(f"다운로드한 파일 크기: {file_size} bytes")  

    return local_path