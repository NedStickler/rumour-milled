# 1. Base image with Playwright and Python preinstalled
FROM mcr.microsoft.com/playwright/python:v1.54.0-noble

# 2. Set working directory
WORKDIR /app

# 3. Install Python packages
RUN pip install --no-cache-dir playwright python-dotenv boto3 requests validators pyyaml \
  && rm -rf /root/.cache/pip

# 4. Copy source and scripts
COPY src/rumour_milled/ src/rumour_milled/
COPY scripts/ scripts/
COPY configs/ configs/

# 5. Add to Python path so imports work
ENV PYTHONPATH=/app/src

# 6. Run the scraper entrypoint
CMD ["python", "scripts/run_scrapers.py"]
