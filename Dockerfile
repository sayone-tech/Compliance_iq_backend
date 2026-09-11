# WSP validation POC -- a new machine needs only Docker: no host poppler, no host
# Python. The Qdrant server is a separate service; see docker-compose.yml.
FROM python:3.12-slim

# PDF text extraction shells out to poppler's pdftotext, not a Python library.
# The image serves both the WSP validation CLI and the test-case execution API
# (scripts/testcase_poc, `uvicorn testcase_poc.app:app` -- see docker-compose.yml).
# tini reaps the child processes that subprocess call leaves behind, so Ctrl-C on
# a long run does not strand a pdftotext.
RUN apt-get update && apt-get install --no-install-recommends -y \
        poppler-utils \
        tini \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/scripts

# PYTHONDONTWRITEBYTECODE is not cosmetic here: scripts/__pycache__/ already
# exists on the host, and the compose file bind-mounts the repo over /app, so
# without it the container writes root-owned .pyc files into the working tree.

WORKDIR /app

# testcase_poc/requirements.txt includes wsp_poc/requirements.txt via `-r ../wsp_poc/...`,
# so the relative path must survive the copy.
COPY scripts/wsp_poc/requirements.txt /tmp/req/wsp_poc/requirements.txt
COPY scripts/testcase_poc/requirements.txt /tmp/req/testcase_poc/requirements.txt
RUN pip install -r /tmp/req/testcase_poc/requirements.txt

# The whole scripts/ tree, not just wsp_poc/: validate_wsp.py inserts its parent
# directory on sys.path and imports fetch_regulation from it.
COPY scripts/ /app/scripts/

RUN useradd -m -u 1000 -s /bin/bash app && chown -R app:app /app
USER app

ENTRYPOINT ["/usr/bin/tini", "--"]
# A bare `docker compose run wsp-poc` should do nothing surprising.
CMD ["python3", "scripts/wsp_poc/validate_wsp.py", "--help"]
