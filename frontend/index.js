/* global m, Chessground */

const kParams = new URLSearchParams(location.search);
const kEnv = kParams.get("env");

const kConfig = {
  baseUrl:
    kEnv == "dev"
      ? `http://${location.hostname}:5000`
      : "https://web-vrnocjtpaa-an.a.run.app",
  resizeTarget: 1000,
};

const imageToBlob = (image) => {
  const canvas = document.createElement("canvas");
  canvas.width = image.width;
  canvas.height = image.height;
  const context = canvas.getContext("bitmaprenderer");
  context.transferFromImageBitmap(image);
  return new Promise((resolve) => canvas.toBlob(resolve));
};

const resizeImage = async (image) => {
  const { width, height } = image;
  const ar = width / height;
  const { resizeTarget } = kConfig;
  const resizeWidth = width > height ? resizeTarget : resizeTarget * ar;
  const resizeHeight = width > height ? resizeTarget / ar : resizeTarget;
  const resizedImage = await createImageBitmap(image, {
    resizeWidth,
    resizeHeight,
    resizeQuality: "high",
  });
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
  const resp = await fetch(kConfig.baseUrl + "/detect?debug=True", {
    method: "POST",
    body: data,
  });
  const result = await resp.json();
  return result;
};

const RootView = () => {
  let file;
  let fileUrl;
  let fen = "8/8/8/8/8/8/8/8";
  let cg;
  let boardImageUrl;
  let enableCapture = false;
  let loading = false;

  const oninit = async () => {
    try {
      // domain needs to be under https
      await navigator.mediaDevices.getUserMedia({
        video: true,
        facingMode: { exact: "environment" },
      });
      enableCapture = true;
      m.redraw();
    } catch (e) {
      console.error("[navigator.mediaDevices.getUserMedia]", e);
    }
  };

  const oncreate = (vnode) => {
    cg = Chessground(vnode.dom.querySelector(".board-gui"), {
      fen,
      viewOnly: true,
      coordinates: false,
      animation: { enabled: false },
    });
  };

  const onImageInputChange = async (e) => {
    const selected = e.currentTarget.files[0];
    if (selected) {
      file = selected;
      fileUrl = URL.createObjectURL(file);
    }
  };

  const onDetectClick = async () => {
    loading = true;
    m.redraw();

    const result = await detect(file);
    fen = result.fen;
    boardImageUrl = result.debug.board_image;
    cg.set({ fen });

    loading = false;
    m.redraw();
  };

  const view = () => {
    return m("main", [
      m(".title", "CHESS OCR"),
      m(".image-inputs", [
        m("div", [
          m("label.button", { for: "image-input-1" }, [
            "select file",
            m("input#image-input-1", {
              type: "file",
              accept: "image/*",
              onchange: onImageInputChange,
            }),
          ]),
        ]),
        m("div", [
          m(
            "label.button",
            { for: "image-input-2", disabled: !enableCapture },
            [
              "take photo",
              m("input#image-input-2", {
                type: "file",
                accept: "image/*",
                capture: "environment",
                onchange: onImageInputChange,
                disabled: !enableCapture,
              }),
            ]
          ),
        ]),
      ]),

      m(
        ".image-preview.preview",
        { class: fileUrl ? "preview--selected" : "" },
        file ? m("img", { src: fileUrl }) : "image"
      ),

      m(".button", { disabled: !file, onclick: file && onDetectClick }, [
        loading && m(".spinner"),
        m("span", "Scan"),
      ]),

      m(".separator"),

      m(".result-board", [
        m(".board-gui"),
        m(
          ".board-image.preview",
          { class: boardImageUrl ? "preview--selected" : "" },
          boardImageUrl ? m("img", { src: boardImageUrl }) : "board"
        ),
      ]),

      m(".fen", [
        m("label", "FEN"),
        m("input", { value: fen, readonly: true }),
      ]),

      m(
        "a.button",
        {
          target: "_blank",
          href: `https://lichess.org/editor/${fen}_w`,
        },
        "Edit on Lichess"
      ),
    ]);
  };

  return { oninit, oncreate, view };
};

const main = () => {
  m.mount(document.body, RootView);
};

main();
