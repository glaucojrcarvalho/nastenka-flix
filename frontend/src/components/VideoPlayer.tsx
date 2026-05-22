import { useEffect, useRef } from 'react';

type VideoPlayerProps = {
  src: string;
  poster?: string | null;
  initialPositionSeconds: number;
  onProgress: (positionSeconds: number, completed: boolean) => void;
  onPlaybackError?: () => void;
};

export function VideoPlayer({ src, poster, initialPositionSeconds, onProgress, onPlaybackError }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const lastSyncedRef = useRef(0);

  useEffect(() => {
    const video = videoRef.current;
    if (!video || !initialPositionSeconds) {
      return;
    }
    video.currentTime = initialPositionSeconds;
  }, [initialPositionSeconds]);

  return (
    <video
      ref={videoRef}
      className="video-player"
      controls
      playsInline
      poster={poster ?? undefined}
      src={src}
      onTimeUpdate={(event) => {
        const currentTime = Math.floor(event.currentTarget.currentTime);
        if (currentTime - lastSyncedRef.current < 10) {
          return;
        }
        lastSyncedRef.current = currentTime;
        onProgress(currentTime, false);
      }}
      onEnded={(event) => {
        const currentTime = Math.floor(event.currentTarget.duration || event.currentTarget.currentTime);
        onProgress(currentTime, true);
      }}
      onError={() => {
        onPlaybackError?.();
      }}
    />
  );
}
