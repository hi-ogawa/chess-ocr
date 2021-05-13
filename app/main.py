from flask import Flask, request
import PIL.Image as Image
from .detector import Detector, detect_board

app = Flask(__name__)
detector = Detector('data/checkpoint/model-2021-05-12-22-17-10.pt')


def get_form_image():
  file = request.files.get('image')
  if file is None:
    raise RuntimeError('Missing "image" form data')
  try:
      image = Image.open(file)
  except IOError:
      raise RuntimeError('Invalid image file')
  return image


def to_lichess_url(fen):
  return f"https://lichess.org/editor/{fen}"


@app.errorhandler(RuntimeError)
def handler(error):
  return {'status': 'error', 'message': error.args[0]}, 400


@app.route('/detect', methods=['POST'])
def route_detect():
  image = get_form_image()
  fen = detector.detect(image)
  return {'status': 'success', 'fen': fen, 'lichess': to_lichess_url(fen)}


@app.route('/board_to_fen', methods=['POST'])
def route_board_to_fen():
  image = get_form_image()
  fen = detector.board_to_fen(image)
  return {'status': 'success', 'fen': fen, 'lichess': to_lichess_url(fen)}