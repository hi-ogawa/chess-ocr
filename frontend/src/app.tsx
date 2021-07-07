import * as React from "react";
import { useRef, useState, useEffect } from "react";
import { Chessground } from "chessground";
import { Api as CgApi } from "chessground/api";
import classnames from "classnames";
import { detect, isCameraAvailable } from "./utils";

interface Image {
  file: File;
  url: string;
}

export default function App() {
  const cg = useRef<CgApi | null>(null);
  const cgEl = useRef<HTMLDivElement | null>(null);

  const [fen, setFen] = useState<string>("8/8/8/8/8/8/8/8");
  const [image, setImage] = useState<Image | null>(null);
  const [boardImageUrl, setBoardImageUrl] = useState<string | null>(null);
  const [enableCapture, setEnableCapture] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  const onMount = async () => {
    cg.current = Chessground(cgEl.current!, {
      fen,
      viewOnly: true,
      coordinates: false,
      animation: { enabled: false },
    });

    if (await isCameraAvailable()) {
      setEnableCapture(true);
    }
  };

  const onUnmount = () => {
    cg.current!.destroy();
  };

  const onImageInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.currentTarget.files![0];
    if (selected) {
      if (image && image.url) {
        URL.revokeObjectURL(image.url);
      }
      setImage({
        file: selected,
        url: URL.createObjectURL(selected),
      });
    }
  };

  const onClickScan = async () => {
    if (!image) {
      return;
    }
    setLoading(true);
    try {
      const result = await detect(image.file);
      setFen(result.fen);
      setBoardImageUrl(result.debug.board_image);
      cg.current!.set({ fen: result.fen });
    } catch (e) {
      window.alert(`[ERROR] ${e}`);
    }
    setLoading(false);
  };

  useEffect(() => {
    onMount();
    return onUnmount;
  }, []);

  return (
    <main>
      <div className="title">CHESS OCR</div>

      <div className="image-inputs">
        <div>
          <label className="button" htmlFor="image-input-1">
            Select file
            <input
              id="image-input-1"
              type="file"
              accept="image/*"
              onChange={onImageInputChange}
            />
          </label>
        </div>
        <div>
          <label
            className={classnames("button", {
              "button--disabled": !enableCapture,
            })}
            htmlFor="image-input-2"
          >
            Take photo
            <input
              id="image-input-2"
              type="file"
              accept="image/*"
              onChange={onImageInputChange}
              disabled={!enableCapture}
              capture="environment"
            />
          </label>
        </div>
      </div>

      <div
        className={classnames("image-preview preview", {
          "preview--selected": !!image,
        })}
      >
        {image ? <img src={image.url} /> : "image"}
      </div>

      <div
        className={classnames("button", { "button--disabled": !image })}
        onClick={onClickScan}
      >
        {loading && <div className="spinner"></div>}
        <span>Scan</span>
      </div>

      <div className="separator"></div>

      <div className="result-board">
        <div className="board-gui" ref={cgEl}></div>
        <div
          className={classnames("board-image preview", {
            "preview--selected": !!boardImageUrl,
          })}
        >
          {boardImageUrl ? <img src={boardImageUrl} /> : "board"}
        </div>
      </div>

      <div className="fen">
        <label>FEN</label>
        <input value={fen} readOnly={true} />
      </div>

      <a
        className="button"
        target="_blank"
        href={`https://lichess.org/editor/${fen}_w`}
      >
        Edit on Lichess
      </a>
    </main>
  );
}
