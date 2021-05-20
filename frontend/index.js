const kBaseUrl = "https://web-vrnocjtpaa-an.a.run.app";
const kDefaultSize = 1000;

const imageToBlob = (image) => {
  const canvas = document.createElement('canvas');
  canvas.width = image.width;
  canvas.height = image.height;
  const context = canvas.getContext('bitmaprenderer');
  context.transferFromImageBitmap(image);
  return new Promise(resolve => canvas.toBlob(resolve));
};

const resizeImage = async (image) => {
  const { width, height } = image;
  const ar = width / height;
  const resizeWidth  = (width > height) ? (kDefaultSize     ) : (kDefaultSize * ar);
  const resizeHeight = (width > height) ? (kDefaultSize / ar) : (kDefaultSize     );
  const resizedImage = await createImageBitmap(image, { resizeWidth, resizeHeight, resizeQuality: 'high' });
  return resizedImage;
};

const resizeBlob = async (blob) => {
  let image = await createImageBitmap(blob);
  image = await resizeImage(image);
  blob = await imageToBlob(image);
  return blob;
};

const detect = async (file) => {
  file = await resizeBlob(file);
  const data = new FormData();
  data.append("image", file);
  const resp = await fetch(kBaseUrl + '/detect', { method: "POST", body: data });
  const result = await resp.json()
  return result;
};

const detectBoard = async (file) => {
  file = await resizeBlob(file);
  const data = new FormData();
  data.append("image", file);
  const resp = await fetch(kBaseUrl + '/detect_board', { method: "POST", body: data });
  const result = await resp.blob();
  return result;
};

const RootView = () => {
  let file = null;
  let fen = '';
  let state = '';
  let debugBoardUrl = null;
  let chessboard = null;

  const onDebugBoard = async () => {
    const result = await detectBoard(file); // : Blob
    debugBoardUrl = URL.createObjectURL(result);
    m.redraw();
  };

  const oncreate = (vnode) => {
    const el = vnode.dom.querySelector("#board");
    chessboard = Chessboard(el, {
      position: 'start',
      pieceTheme: 'https://cdn.jsdelivr.net/gh/oakmac/chessboardjs/website/img/chesspieces/wikipedia/{piece}.png',
    });
  };

  const view = () => {
    return m("div", [
      m("input", {
        type: "file",
        capture: "environment",
        accept: "image/*",
        onchange: async (e) => {
          file = e.currentTarget.files[0];
          if (file) {
            const result = await detect(file);
            fen = result.fen;
            chessboard.position(fen, false);
            m.redraw();
          }
        }
      }),

      m("#board", { style: 'width: 256px' }),

      fen && m("div", `FEN: ${fen}`),

      fen && m("div", [ m("a", { href: `https://lichess.org/editor/${fen}` }, "Open on Lichess") ]),

      file && m("div", m("button", { onclick: onDebugBoard }, "Debug Board")),

      debugBoardUrl && m("div", m("img", { src: debugBoardUrl })),
    ]);
  };

  return { oncreate, view };
};

const main = () => {
  m.mount(document.querySelector("#root"), RootView);
};

main();
