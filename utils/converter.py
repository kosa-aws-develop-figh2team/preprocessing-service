import subprocess
import os
from pathlib import Path
import fitz  # PyMuPDF
import logging

# 로깅 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HwpConverter:
    def __init__(self, hwp5txt_path: str = "hwp5txt"):
        # hwp5txt 실행 파일 경로 확인
        if hwp5txt_path == "hwp5txt":
            result = subprocess.run(['which', 'hwp5txt'], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE,
                                    text=True)
            if result.returncode == 0:
                self.hwp5txt_path = result.stdout.strip()
                logger.info(f"hwp5txt 경로 설정 완료: {self.hwp5txt_path}")
            else:
                logger.error("hwp5txt 실행 파일을 찾을 수 없습니다. PATH 확인 필요.")
                raise RuntimeError("hwp5txt 실행 파일을 찾을 수 없습니다.")
        else:
            self.hwp5txt_path = hwp5txt_path
            logger.info(f"사용자 지정 hwp5txt 경로 설정: {self.hwp5txt_path}")

    def convert(self, input_path: str, output_dir: str = None) -> str:
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"HWP 파일이 존재하지 않습니다: {input_path}")

        output_dir = Path(output_dir) if output_dir else input_path.parent
        output_path = output_dir / (input_path.stem + ".txt")

        try:
            logger.info(f"HWP 파일 변환 시작: {input_path}")
            result = subprocess.run(
                [self.hwp5txt_path, str(input_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            text = result.stdout

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

            logger.info(f"HWP 파일 변환 완료: {output_path}")
            return text
        except subprocess.CalledProcessError as e:
            logger.error(f"hwp5txt 변환 실패: {e.stderr.strip()}")
            raise RuntimeError(f"hwp5txt 변환 실패: {e.stderr.strip()}")

class PdfConverter:
    def __init__(self):
        pass

    def convert(self, input_path: str, output_dir: str = None) -> str:
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"PDF 파일이 존재하지 않습니다: {input_path}")

        output_dir = Path(output_dir) if output_dir else input_path.parent
        output_path = output_dir / (input_path.stem + ".txt")

        try:
            logger.info(f"PDF 파일 변환 시작: {input_path}")
            text = ""
            with fitz.open(input_path) as doc:
                for page in doc:
                    text += page.get_text()

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

            logger.info(f"PDF 파일 변환 완료: {output_path}")
            return text
        except Exception as e:
            logger.error(f"PDF 변환 실패: {str(e)}")
            raise RuntimeError(f"PDF 변환 실패: {str(e)}")

# ✅ 공통 유틸 함수
def get_extension(file_path: str) -> str:
    return Path(file_path).suffix.lower()

def convert_to_text(file_path: str) -> str:
    ext = get_extension(file_path)
    logger.info(f"파일 경로: {file_path}, 확장자: {ext}")
    if ext == ".pdf":
        return PdfConverter().convert(file_path)
    elif ext == ".hwp":
        return HwpConverter().convert(file_path)
    elif ext == ".txt":
        # ✅ 텍스트 파일은 그대로 읽어서 반환
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        logger.info(f"TXT 파일 변환 생략: {file_path}")
        return text
    else:
        logger.error(f"지원하지 않는 파일 형식입니다: {ext}")
        raise ValueError(f"지원하지 않는 파일 형식입니다: {ext}")