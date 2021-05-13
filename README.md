# Chess OCR

```
curl -F "image=@data/example/ex000.png" http://chess-ocr.herokuapp.com/board_to_fen
{"fen":"1r3k2/2b2pn1/p2q2pB/2pP4/2B1p2Q/1P6/P1K2P1P/6R1","lichess":"https://lichess.org/editor/1r3k2/2b2pn1/p2q2pB/2pP4/2B1p2Q/1P6/P1K2P1P/6R1","status":"success"}
```

# Generate Dataset

```bash
TYPES=(wP wN wB wR wQ wK bP bN bB bR bQ bK)
SIZE=32x32

# Download base piece image as SVG
mkdir -p data/{tmp,piece}/{cburnett,merida}
for TYPE in ${TYPES[@]}; do
  wget -O data/tmp/cburnett/$TYPE.svg https://raw.githubusercontent.com/ornicar/lila/master/public/piece/cburnett/$TYPE.svg
  wget -O data/tmp/merida/$TYPE.svg   https://raw.githubusercontent.com/ornicar/lila/master/public/piece/merida/$TYPE.svg
done

# Convert to PNG (data/piece)
for TYPE in ${TYPES[@]}; do
  convert -background none data/tmp/cburnett/$TYPE.svg -resize $SIZE png32:data/piece/cburnett/$TYPE.png
  convert -background none data/tmp/merida/$TYPE.svg -resize $SIZE png32:data/piece/merida/$TYPE.png
done

# Empty image
convert -size $SIZE xc:transparent png32:data/empty/ex000.png

# Generate random background (data/background)
PATTERNS=(BRICKS CHECKERBOARD CIRCLES CROSSHATCH CROSSHATCH30 CROSSHATCH45 FISHSCALES GRAY30 GRAY40 GRAY50 GRAY60 GRAY70 GRAY80 GRAY90 GRAY100 HEXAGONS HORIZONTAL HORIZONTAL2 HORIZONTAL3 HORIZONTALSAW HS_BDIAGONAL HS_CROSS HS_DIAGCROSS HS_FDIAGONAL HS_HORIZONTAL HS_VERTICAL LEFT30 LEFT45 LEFTSHINGLE OCTAGONS RIGHT30 RIGHT45 RIGHTSHINGLE SMALLFISHSCALES VERTICAL VERTICAL2 VERTICAL3 VERTICALBRICKS VERTICALLEFTSHINGLE VERTICALRIGHTSHINGLE VERTICALSAW)
SCALES=(60% 80% 100%)
i=0
for PATTERN in ${PATTERNS[@]}; do
  for SCALE in ${SCALES[@]}; do
    convert -size 1024x1024 pattern:$PATTERN -scale $SCALE -extent $SIZE png24:data/background/$(printf "ex%03d.png" $i)
    i=$((i + 1))
  done
done

# Compose piece image with background (data/train)
for BACK in data/background/*.png; do
  for FRONT in $(find data/piece -mindepth 1 -maxdepth 1 -type d); do
    SUFFIX=$(basename $FRONT)-$(basename ${BACK%.*}).png
    for TYPE in ${TYPES[@]}; do
      convert $BACK $FRONT/$TYPE.png -flatten png24:data/train/$TYPE--$SUFFIX
    done
  done
done

for BACK in data/background/*.png; do
  for FRONT in data/empty/*.png; do
    SUFFIX=$(basename ${FRONT%.*})-$(basename ${BACK%.*}).png
    convert $BACK $FRONT -flatten png24:data/train/empty--$SUFFIX
  done
done
```

See also `generate.ipynb`.

# Training

See `detect_piece.ipynb`

# Board detection

See `detect_board.ipynb`

# API Server

```
FLASK_APP=app/main.py FLASK_ENV=development flask run --reload --debugger
curl -F "image=@data/example/ex000.png" http://localhost:5000/board_to_fen
```

# Deployment

```
# Build container image
docker-compose build

# Test locally
docker-compose up

# Deploy
docker push registry.heroku.com/chess-ocr/web
heroku container:release web

# Check logs
heroku logs -t

# (Heroku one-time setup)
heroku login
heroku container:login
heroku apps:create chess-ocr
```
