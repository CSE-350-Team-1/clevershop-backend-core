FROM python:3.12-slim

WORKDIR /app

# Use a requirements file to leverage Docker layer caching
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY run.py ./
COPY src ./src

EXPOSE 8000

# Keep runtime secrets out of the repository. Provide DB credentials and
# other environment variables at runtime (docker run / docker-compose / k8s).
ENV PORT=8000

CMD ["python", "run.py"]
