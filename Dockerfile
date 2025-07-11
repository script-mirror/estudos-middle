FROM python:3.12-alpine

RUN apk add --no-cache \
    musl-locales \
    musl-locales-lang && \
    echo "pt_BR.UTF-8 UTF-8" > /etc/locale.gen

ENV LANG=pt_BR.UTF-8
ENV LANGUAGE=pt_BR:pt
ENV LC_ALL=pt_BR.UTF-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
