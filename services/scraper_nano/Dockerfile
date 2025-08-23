# 1. Base image with Playwright and Python preinstalled
FROM mcr.microsoft.com/playwright/python:v1.54.0-noble

# 2. Set working directory
WORKDIR /app

# 4. Copy source and scripts
COPY services/scraper/ services/scraper/
COPY src/rumour_milled/ src/rumour_milled/
COPY configs/scraping/ configs/scraping/

# 3. Install Python packages
RUN pip install -r services/scraper/requirements.txt --no-cache-dir  \
  && rm -rf /root/.cache/pip

# 5. Add to Python path so imports work
ENV PYTHONPATH=/app/src

# 6. Run the scraper entrypoint
CMD ["python", "services/scraper/job.py"]
