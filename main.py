from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from utils import s3_handler as s3
from utils.converter import convert_to_text
from utils.dynamodb_logger import update_metadata
from utils.chunker import split_into_chunks

import uuid
import logging
import os

# main.py 상단
import dotenv
dotenv.load_dotenv()

bucket = os.getenv("S3_BUCKET", "my-processing-bucket")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# 📄 텍스트 변환 요청
class ConvertRequest(BaseModel):
    service_id: str
    s3_file_path: str

class ConvertResponse(BaseModel):
    txt_text: str

@app.post("/process/convert", response_model=ConvertResponse)
def convert_file(request: ConvertRequest):
    service_id = request.service_id
    s3_key_txt = f"txt/{service_id}/converted.txt"

    # ✅ 중복 처리 방지: 변환된 텍스트 존재 시 바로 리턴
    if s3.exists(bucket, s3_key_txt):
        logger.info("이미 변환된 텍스트가 존재합니다. 변환 생략.")
        return {"txt_text": s3.download_text(bucket, s3_key_txt)}

    try:
        # ✅ (1) 실제 원본 S3 경로에서 bucket, key 분리
        parsed_bucket, parsed_key = s3.parse_s3_path(request.s3_file_path)
        logger.info(f"S3 경로 분리 완료: bucket={parsed_bucket}, key={parsed_key}")

        # ✅ (2) S3 원본 파일 다운로드
        file_path = s3.download(parsed_bucket, parsed_key)
        logger.info(f"S3 원본 파일 다운로드 완료: 로컬 경로={file_path}")

        # ✅ (3) 텍스트 변환
        text = convert_to_text(file_path)
        logger.info(f"텍스트 변환 완료: 텍스트={text}")

        # ✅ (4) 변환된 텍스트를 중간 결과로 S3에 저장
        s3.upload_text(bucket, s3_key_txt, text)
        logger.info(f"변환된 텍스트 S3에 저장 완료: bucket={bucket}, key={s3_key_txt}")

        # ✅ (5) DynamoDB 기록
        update_metadata(service_id, step="convert", status="success")
        logger.info(f"DynamoDB에 변환 성공 상태 기록 완료: service_id={service_id}")

        return {"txt_text": text}

    except Exception as e:
        update_metadata(service_id, step="convert", status="failed", error=str(e))
        raise HTTPException(status_code=500, detail="변환 실패")

# ✂️ 청킹 요청
class ChunkRequest(BaseModel):
    service_id: str
    txt_text: str

class ChunkResponse(BaseModel):
    chunk_list: List[str]

@app.post("/process/chunk", response_model=ChunkResponse)
def chunk_text(request: ChunkRequest):
    service_id = request.service_id
    s3_key_chunk = f"chunks/{service_id}/chunks.json"

    if s3.exists(bucket, s3_key_chunk):
        return {"chunk_list": s3.download_json(bucket, s3_key_chunk)}

    try:
        chunk_list = split_into_chunks(request.txt_text)

        s3.upload_json(bucket, s3_key_chunk, chunk_list)
        update_metadata(service_id, step="chunk", status="success")

        return {"chunk_list": chunk_list}

    except Exception as e:
        update_metadata(service_id, step="chunk", status="failed", error=str(e))
        raise HTTPException(status_code=500, detail="청킹 실패")