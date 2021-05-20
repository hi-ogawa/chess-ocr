from flask import Flask, request, send_file
import PIL.Image as Image
from .detector import Detector, detect_board
import io

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


@app.errorhandler(RuntimeError)
def handle_runtime_error(error):
  return {'status': 'error', 'message': error.args[0]}, 400


@app.after_request
def handle_cors(response):
  response.headers.set('Access-Control-Allow-Origin', '*')
  response.headers.set('Access-Control-Allow-Methods', 'GET, POST')
  return response


@app.route('/detect', methods=['POST'])
def route_detect():
  image = get_form_image()
  fen = detector.detect(image)
  return {'status': 'success', 'fen': fen}


@app.route('/detect_board', methods=['POST'])
def route_detect_board():
  image = get_form_image()
  image = detector.detect_board(image)
  f = io.BytesIO()
  image.save(f, format='png')
  f.seek(0)
  return send_file(f, mimetype='image/png')


@app.route('/board_to_fen', methods=['POST'])
def route_board_to_fen():
  image = get_form_image()
  fen = detector.board_to_fen(image)
  return {'status': 'success', 'fen': fen}
