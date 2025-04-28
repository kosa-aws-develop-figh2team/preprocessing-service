# Lambda Python 3.9 베이스 이미지 사용
FROM public.ecr.aws/lambda/python:3.9

# 로컬 코드 복사
COPY lambda_function.py ${LAMBDA_TASK_ROOT}/
COPY utils/ ${LAMBDA_TASK_ROOT}/utils/
COPY requirements.txt  ${LAMBDA_TASK_ROOT}/

# 의존성 설치
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 기본 Lambda 핸들러 설정
CMD ["lambda_function.lambda_handler"]