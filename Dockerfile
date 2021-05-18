FROM python:3.9.5-slim-buster

RUN mkdir -p /app
WORKDIR /app

# Cache dependencies
COPY ./requirements-production.txt ./
RUN pip install -r requirements-production.txt -f https://download.pytorch.org/whl/torch_stable.html

# Copy the rest
COPY . ./

ENTRYPOINT ["sh", "docker-entrypoint.sh"]
