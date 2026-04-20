import { useCallback, useEffect, useRef, useState } from "react";

interface UseCameraResult {
  cameraReady: boolean;
  cameraError: string | null;
  captureFrameBase64: () => string;
}

export function useCamera(): UseCameraResult {
  const [cameraReady, setCameraReady] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    let active = true;
    const initCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user" },
          audio: false
        });
        if (!active) {
          stream.getTracks().forEach((track) => track.stop());
          return;
        }

        streamRef.current = stream;
        const hiddenVideo = document.createElement("video");
        hiddenVideo.srcObject = stream;
        hiddenVideo.muted = true;
        hiddenVideo.playsInline = true;
        await hiddenVideo.play();
        videoRef.current = hiddenVideo;
        setCameraReady(true);
        setCameraError(null);
      } catch (_error) {
        setCameraReady(false);
        setCameraError(
          "Permiso de camara requerido. Configura el acceso en el navegador y recarga la pagina."
        );
      }
    };

    initCamera().catch(() => {
      setCameraReady(false);
      setCameraError(
        "Permiso de camara requerido. Configura el acceso en el navegador y recarga la pagina."
      );
    });

    return () => {
      active = false;
      streamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  const captureFrameBase64 = useCallback((): string => {
    const video = videoRef.current;
    if (!video || !video.videoWidth || !video.videoHeight) {
      throw new Error("Camara no disponible");
    }

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");
    if (!context) {
      throw new Error("No se pudo capturar la imagen");
    }
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg", 0.9);
  }, []);

  return { cameraReady, cameraError, captureFrameBase64 };
}
