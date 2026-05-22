import { Link, useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';

import {
  getEpisode,
  getEpisodeProgress,
  resolveMediaUrl,
  updateEpisodeProgress,
  type EpisodeDetail,
  type ProgressResponse,
} from '../api/client';
import { VideoPlayer } from '../components/VideoPlayer';

export function PlayerPage() {
  const { episodeId = '' } = useParams();
  const [episode, setEpisode] = useState<EpisodeDetail | null>(null);
  const [progress, setProgress] = useState<ProgressResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [playbackError, setPlaybackError] = useState<string | null>(null);

  useEffect(() => {
    const numericEpisodeId = Number(episodeId);
    Promise.all([getEpisode(numericEpisodeId), getEpisodeProgress(numericEpisodeId)])
      .then(([episodeResponse, progressResponse]) => {
        setEpisode(episodeResponse);
        setProgress(progressResponse);
        setPlaybackError(null);
      })
      .catch((requestError) => {
        setError(requestError instanceof Error ? requestError.message : 'Could not load episode');
      });
  }, [episodeId]);

  if (error) {
    return <div className="panel panel--error">{error}</div>;
  }

  if (!episode || !progress) {
    return <div className="panel">Getting my episode ready...</div>;
  }

  return (
    <section className="stack-lg">
      <Link className="back-link" to={`/series/${episode.series_slug}`}>
        Back to my series
      </Link>
      <div className="player-heading">
        <div>
          <p className="eyebrow">Playing for me now</p>
          <h1>{episode.title}</h1>
        </div>
        <div className="player-heading__meta">
          <span>S{String(episode.season_number).padStart(2, '0')} E{String(episode.episode_number).padStart(2, '0')}</span>
          <span>{Math.round(episode.duration_seconds / 60)} min</span>
        </div>
      </div>
      <div className="player-layout">
        <div className="player-layout__video">
          <VideoPlayer
            initialPositionSeconds={progress.position_seconds}
            onProgress={async (positionSeconds, completed) => {
              const nextProgress = await updateEpisodeProgress(episode.id, positionSeconds, completed);
              setProgress(nextProgress);
            }}
            onPlaybackError={() => {
              setPlaybackError(
                'This video file loaded but the browser could not play its format. Convert this episode to MP4 with H.264 video and AAC audio.',
              );
            }}
            poster={episode.thumbnail_url}
            src={resolveMediaUrl(episode.media_url)}
          />
          {playbackError ? <div className="panel panel--error">{playbackError}</div> : null}
        </div>
        <aside className="player-layout__aside panel">
          <p>{episode.description}</p>
          <div className="progress-meter">
            <div className="progress-meter__bar">
              <span style={{ width: `${Math.min(100, (progress.position_seconds / Math.max(episode.duration_seconds, 1)) * 100)}%` }} />
            </div>
            <small>{progress.completed ? 'I finished this on my last watch' : 'Saved so I can come back anytime'}</small>
          </div>
          <dl className="detail-grid">
            <div>
              <dt>Duration</dt>
              <dd>{Math.round(episode.duration_seconds / 60)} min</dd>
            </div>
            <div>
              <dt>My resume point</dt>
              <dd>{Math.round(progress.position_seconds / 60)} min</dd>
            </div>
            <div>
              <dt>My status</dt>
              <dd>{progress.completed ? 'Finished' : 'Still watching'}</dd>
            </div>
          </dl>
        </aside>
      </div>
    </section>
  );
}
