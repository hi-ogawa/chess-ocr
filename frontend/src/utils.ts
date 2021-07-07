import config from "./config";

async function imageToBlob(image: ImageBitmap): Promise<Blob> {
  const canvas = document.createElement("canvas");
  canvas.width = image.width;
  canvas.height = image.height;
  const context = canvas.getContext("bitmaprenderer")!;
  context.transferFromImageBitmap(image);
  return new Promise((resolve) => canvas.toBlob(resolve)) as any;
}

async function resizeImage(image: ImageBitmap): Promise<ImageBitmap> {
  const { width, height } = image;
  const ratio = width / height;
  const { resizeTarget } = config;
  const resizeWidth = width > height ? resizeTarget : resizeTarget * ratio;
  const resizeHeight = width > height ? resizeTarget / ratio : resizeTarget;
  const resizedImage = await createImageBitmap(image, {
    resizeWidth,
    resizeHeight,
    resizeQuality: "high",
  });
  return resizedImage;
}

async function resizeBlob(blob: Blob): Promise<Blob> {
  return createImageBitmap(blob).then(resizeImage).then(imageToBlob);
}

async function fetchJson<T>(...args: Parameters<typeof fetch>): Promise<T> {
  const response = await fetch(...args);
  if (!response.ok) {
    throw new Error(response.status.toString());
  }
  return response.json() as Promise<T>;
}

interface Detection {
  fen: string;
  debug: {
    board_image: string;
  };
}

export async function detect(blob: Blob): Promise<Detection> {
  const resizedBlob = await resizeBlob(blob);
  const formData = new FormData();
  formData.append("image", resizedBlob);
  return fetchJson(
    config.baseUrl + `/detect?debug=true&chessvision=${config.chessvision}`,
    {
      method: "POST",
      body: formData,
    }
  );
}

export async function isCameraAvailable(): Promise<boolean> {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    for (const device of devices) {
      if (device.kind === "videoinput") {
        return true;
      }
    }
  } catch (e) {
    console.error("[navigator.mediaDevices.enumerateDevices]", e);
  }
  return false;
}
