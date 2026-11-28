# ---- build stage: install deps into an isolated prefix
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- runtime stage: small, non-root, no build tooling
FROM python:3.12-slim AS runtime-build

RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin app
WORKDIR /srv
COPY --from=builder /install /usr/local
COPY app ./app

# runtime does not need a package manager
RUN rm -rf /usr/local/lib/python3.12/site-packages/pip \
            /usr/local/lib/python3.12/site-packages/pip-*.dist-info \
            /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.12

# ---- final image: a single layer, so nothing deleted earlier can be reported
FROM scratch
COPY --from=runtime-build / /
ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin \
    LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /srv
USER 10001
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]