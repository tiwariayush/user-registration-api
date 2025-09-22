FROM python:3.12-slim
WORKDIR /srv
RUN pip install --no-cache-dir fastapi==0.115.0 uvicorn[standard]==0.30.6 pydantic[email]==2.9.2
COPY . /srv
EXPOSE 8081
CMD ["uvicorn", "mock_mailer:app", "--host", "0.0.0.0", "--port", "8081"]
