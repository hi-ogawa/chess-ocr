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

IMG_FILE=$(mktemp --suffix=.png)
trap "rm ${IMG_FILE}" EXIT

gnome-screenshot -a -f "${IMG_FILE}"
if [ "$(file -b ${IMG_FILE})" == "empty" ]; then
    exit 1
fi

RESPONSE=$(curl --silent -F "image=@${IMG_FILE}" http://chess-ocr.herokuapp.com/detect)
if [ "$?" != "0" ]; then
    notify-send "[Chess OCR] curl failed: ${STATUS}"
    exit 1
fi

xdg-open $(echo "$RESPONSE" | jq -r '.lichess')
