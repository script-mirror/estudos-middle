FROM python:3.12-alpine

RUN apk add --no-cache \
    musl-locales \
    musl-locales-lang \
    git \
    gcc \
    musl-dev && \
    echo "pt_BR.UTF-8 UTF-8" > /etc/locale.gen

ENV LANG=pt_BR.UTF-8
ENV LANGUAGE=pt_BR:pt
ENV LC_ALL=pt_BR.UTF-8

WORKDIR /app

COPY requirements.txt .

# Configure git credentials using build args
ARG GIT_USERNAME
ARG GIT_TOKEN
RUN git config --global credential.helper store && \
    echo "https://${GIT_USERNAME}:${GIT_TOKEN}@github.com" > ~/.git-credentials

RUN pip install --no-cache-dir -r requirements.txt

# Clean up git credentials
RUN rm -f ~/.git-credentials && \
    git config --global --unset credential.helper

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
