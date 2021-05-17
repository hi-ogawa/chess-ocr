FROM archlinux:base-20210509.0.21942

RUN pacman --noconfirm -Syu
RUN pacman --noconfirm -S python python-pip mesa

RUN mkdir -p /chess-ocr
WORKDIR /chess-ocr

# Cache dependencies first
COPY ./requirements-production.txt /chess-ocr
RUN pip install -r requirements-production.txt -f https://download.pytorch.org/whl/torch_stable.html

# Copy app
COPY . /chess-ocr

ENTRYPOINT ["bash", "docker-entrypoint.sh"]
