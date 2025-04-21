from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def split_into_chunks(text: str, max_tokens: int = 300, overlap: int = 50) -> List[str]:
    """
    긴 텍스트를 최대 토큰 수 기준으로 LangChain의 슬라이딩 윈도우 방식으로 청크 분할
    :param text: 전체 입력 텍스트
    :param max_tokens: 한 청크의 최대 길이
    :param overlap: 청크 간 중복되는 길이
    :return: 청크 리스트
    """
    logger.info(f"텍스트 청킹 시작: 길이={len(text)}, 청크 크기={max_tokens}, 중복={overlap}")

    # LangChain 기반 텍스트 분할기
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_tokens,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = splitter.split_text(text)

    logger.info(f"청킹 완료: 총 {len(chunks)}개의 청크 생성")
    return chunks