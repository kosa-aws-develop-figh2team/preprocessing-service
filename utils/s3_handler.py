import boto3
import botocore
import json
import os
import tempfile
from typing import Union
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# S3 클라이언트 설정
s3 = boto3.client("s3")

from urllib.parse import urlparse

def parse_s3_path(s3_path: str):
    """
    s3://bucket-name/path/to/file → (bucket, key) 형태로 분리
    """
    parsed = urlparse(s3_path)
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")
    return bucket, key

def exists(bucket: str, key: str) -> bool:
    """S3 객체 존재 여부 확인"""
    try:
        s3.head_object(Bucket=bucket, Key=key)
        logger.info(f"S3 객체 존재 확인: {bucket}/{key} - 존재")
        return True
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            logger.info(f"S3 객체 존재 확인: {bucket}/{key} - 존재하지 않음")
            return False
        else:
            logger.error(f"S3 객체 존재 확인 실패: {bucket}/{key} - {str(e)}")
            raise

def download(bucket: str, key: str) -> str:
    """S3 파일 다운로드 후 로컬 경로 반환"""
    _, ext = os.path.splitext(key)
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
        s3.download_fileobj(bucket, key, tmp_file)
        logger.info(f"S3 파일 다운로드 완료: {bucket}/{key} - 로컬 경로: {tmp_file.name}")
        return tmp_file.name


def download_text(bucket: str, key: str) -> str:
    """S3 텍스트 파일 다운로드 (string 반환)"""
    obj = s3.get_object(Bucket=bucket, Key=key)
    logger.info(f"S3 텍스트 파일 다운로드 완료: {bucket}/{key}")
    return obj["Body"].read().decode("utf-8")

def download_json(bucket: str, key: str) -> list:
    """S3 JSON 파일 다운로드 (list 반환)"""
    content = download_text(bucket, key)
    logger.info(f"S3 JSON 파일 다운로드 완료: {bucket}/{key}")
    return json.loads(content)

def upload_text(bucket: str, key: str, text: str):
    """텍스트 데이터를 S3에 저장"""
    s3.put_object(Bucket=bucket, Key=key, Body=text.encode("utf-8"))
    logger.info(f"S3에 텍스트 데이터 업로드 완료: {bucket}/{key}")

def upload_json(bucket: str, key: str, data: Union[dict, list]):
    """JSON 데이터를 S3에 저장"""
    body = json.dumps(data, ensure_ascii=False, indent=2)
    upload_text(bucket, key, body)
    logger.info(f"S3에 JSON 데이터 업로드 완료: {bucket}/{key}")