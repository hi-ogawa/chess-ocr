#!/bin/bash

# NOTE:
# - Take screenshot and open lichess board editor
# - Setup keyboard shortcut to invoke this script
# - Dependencies
#     gnome-screenshot
#     notify-send
#     curl
#     xdg-open
#     jq

URL=${1:-"https://web-vrnocjtpaa-an.a.run.app/detect"}

IMG_FILE=$(mktemp --suffix=.png)
trap "rm ${IMG_FILE}" EXIT

gnome-screenshot -a -f "${IMG_FILE}"
if [ "$(file -b ${IMG_FILE})" == "empty" ]; then
    exit 1
fi

RESPONSE=$(curl --silent -F "image=@${IMG_FILE}" ${URL})
if [ "$?" != "0" ]; then
    notify-send "[chess-ocr.sh] curl failed"
    exit 1
fi

FEN=$(echo "${RESPONSE}" | jq -r '.fen')
xdg-open "https://lichess.org/editor/${FEN}"
