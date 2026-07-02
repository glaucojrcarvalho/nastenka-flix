import { useEffect, useRef } from 'react';

type VideoPlayerProps = {
  src: string;
  poster?: string | null;
  initialPositionSeconds: number;
  autoPlay?: boolean;
  onProgress: (positionSeconds: number, completed: boolean) => void;
  onEnded?: () => void;
  onPlaybackError?: () => void;
};

export function VideoPlayer({
  src,
  poster,
  initialPositionSeconds,
  autoPlay = false,
  onProgress,
  onEnded,
  onPlaybackError,
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const lastSyncedRef = useRef(0);
  const resumeAppliedRef = useRef<string | null>(null);
  const autoPlayAttemptedRef = useRef<string | null>(null);

  useEffect(() => {
    resumeAppliedRef.current = null;
    autoPlayAttemptedRef.current = null;
  }, [src]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video || !initialPositionSeconds) {
      return;
    }

    // Only restore the saved position once per source load.
    if (resumeAppliedRef.current === src) {
      return;
    }

    const applyResumePosition = () => {
      video.currentTime = initialPositionSeconds;
      lastSyncedRef.current = Math.floor(initialPositionSeconds);
      resumeAppliedRef.current = src;
    };

    if (video.readyState >= 1) {
      applyResumePosition();
      return;
    }

    video.addEventListener('loadedmetadata', applyResumePosition, { once: true });
    return () => {
      video.removeEventListener('loadedmetadata', applyResumePosition);
    };
  }, [initialPositionSeconds, src]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video || !autoPlay || autoPlayAttemptedRef.current === src) {
      return;
    }

    const startPlayback = () => {
      autoPlayAttemptedRef.current = src;
      void video.play().catch(() => {
        // Browser autoplay policies may block this. Controls stay available.
      });
    };

    if (video.readyState >= 2) {
      startPlayback();
      return;
    }

    video.addEventListener('canplay', startPlayback, { once: true });
    return () => {
      video.removeEventListener('canplay', startPlayback);
    };
  }, [autoPlay, src]);

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
        onEnded?.();
      }}
      onError={() => {
        onPlaybackError?.();
      }}
    />
  );
}
