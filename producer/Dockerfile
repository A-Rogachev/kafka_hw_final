FROM python:3.11-slim

WORKDIR /opt/app

ENV PYTHONPATH=/opt \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=1 \
    PYTHONDONTWRITEBYTECODE=1 \ 
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \ 
    PYTHONFAULTHANDLER=1 \ 
    PYTHONHASHSEED=random

COPY ./requirements.txt /opt/requirements.txt
RUN  pip install --upgrade pip && pip install -r /opt/requirements.txt --no-cache-dir