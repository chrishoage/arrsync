FROM python:alpine

WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
COPY setup.py .
COPY setup.cfg .
COPY arrsync/ ./arrsync/

# Install the package
RUN pip install --no-cache-dir -e .

VOLUME /config

ENTRYPOINT ["arrsync"]

CMD ["--config", "/config/config.conf"]