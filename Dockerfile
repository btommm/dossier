FROM python:3.11-slim

# WeasyPrint system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libfontconfig1 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
COPY report_engine/ ./report_engine/
COPY examples/ ./examples/

RUN pip install --no-cache-dir -e .

# Output directory for generated reports
RUN mkdir -p /reports

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["report-engine"]
CMD ["--help"]
