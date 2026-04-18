# Build from repository root:
#   docker build -f components/collab_hub/Dockerfile -t collab-hub .
# Run:
#   docker run -p 8501:8501 collab-hub
FROM python:3.11-slim

WORKDIR /app

COPY publications.csv .
COPY components/collab_hub/requirements.txt ./components/collab_hub/requirements.txt
RUN pip install --no-cache-dir -r components/collab_hub/requirements.txt

COPY components/collab_hub/ ./components/collab_hub/

ENV STREAMLIT_SERVER_HEADLESS=true
EXPOSE 8501

CMD ["streamlit", "run", "components/collab_hub/app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
