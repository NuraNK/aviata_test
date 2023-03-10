FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR provider-b/
COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r r.txt


CMD ["python", "main.py"]