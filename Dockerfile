FROM archlinux:base-20210509.0.21942

RUN pacman --noconfirm -Syu
RUN pacman --noconfirm -S python python-pip

RUN mkdir -p /chess-ocr
WORKDIR /chess-ocr

# Cache dependencies first
COPY ./requirements-production.txt /chess-ocr
RUN pip install -r requirements-production.txt -f https://download.pytorch.org/whl/torch_stable.html

# Copy app and run
COPY . /chess-ocr

# libGL.so for opencv
RUN pacman --noconfirm -S mesa

CMD FLASK_APP=app/main.py FLASK_ENV=production flask run --host 0.0.0.0 --port ${PORT:-5000}
