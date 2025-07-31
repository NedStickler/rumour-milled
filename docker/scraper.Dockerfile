# 1. Base image with Playwright and Python preinstalled
FROM mcr.microsoft.com/playwright/python:v1.53.0-noble

# 2. Set working directory
WORKDIR /app

# 3. Copy dependencies
COPY poetry.lock pyproject.toml ./

# 4. Install Python packages
RUN pip install --no-cache-dir poetry \
  && poetry config virtualenvs.create false \
  && poetry install --only main --no-root \
  && rm -rf /root/.cache/pip /root/.cache/pypoetry

# 5. Copy source and scripts
COPY src/rumour_milled/ src/rumour_milled/
COPY scripts/ scripts/
COPY configs/ configs/

# 6. Add to Python path so imports work
ENV PYTHONPATH=/app

# 7. Run the scraper entrypoint
CMD ["python", "scripts/run_scrapers.py"]
