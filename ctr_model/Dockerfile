
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "ctr_api:app", "--host", "0.0.0.0", "--port", "8001"]
