#!/bin/bash

URL="https://app.chessvision.ai/predict"

PNG=$(mktemp --suffix=.png)
JSON=$(mktemp --suffix=.json)
trap "rm ${PNG} ${JSON}" EXIT

gnome-screenshot -a -f "${PNG}"
if [ "$(file -b ${PNG})" == "empty" ]; then
  exit 1
fi

JPEG_BASE64=$(convert $PNG jpeg:- | base64)

cat <<EOF >> $JSON
{
  "board_orientation": "predict",
  "cropped": true,
  "current_player": "white",
  "predict_turn": true,
  "image": "data:image/jpeg;base64,${JPEG_BASE64}"
}
EOF

RESPONSE=$(curl --silent --data "@${JSON}" ${URL})
if [ "$?" != "0" ]; then
    notify-send "[chessvision.sh] curl failed"
    exit 1
fi

RESULT=$(echo "${RESPONSE}" | jq -r '.result')
xdg-open "https://lichess.org/editor/${RESULT}"
