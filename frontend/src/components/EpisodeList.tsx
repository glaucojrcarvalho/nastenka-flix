import { Link } from 'react-router-dom';

import type { EpisodeSummary } from '../api/client';

type EpisodeListProps = {
  episodes: EpisodeSummary[];
};

export function EpisodeList({ episodes }: EpisodeListProps) {
  return (
    <div className="episode-list">
      {episodes.map((episode) => (
        <Link className="episode-item" key={episode.id} to={`/player/${episode.id}`}>
          <div className="episode-item__index">{String(episode.episode_number).padStart(2, '0')}</div>
          <div className="episode-item__content">
            <p className="eyebrow">
              S{String(episode.season_number).padStart(2, '0')} E{String(episode.episode_number).padStart(2, '0')}
            </p>
            <h3>{episode.title}</h3>
            <p>{episode.description}</p>
          </div>
          <span className="episode-item__duration">{Math.round(episode.duration_seconds / 60)} min</span>
        </Link>
      ))}
    </div>
  );
}
