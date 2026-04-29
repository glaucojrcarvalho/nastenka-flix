import { Link } from 'react-router-dom';

import type { SeriesSummary } from '../api/client';

type SeriesCardProps = {
  series: SeriesSummary;
};

export function SeriesCard({ series }: SeriesCardProps) {
  return (
    <Link className="series-card" to={`/series/${series.slug}`}>
      <div className="series-card__poster">
        <div className="series-card__badge">{series.stats.completion_percent > 0 ? 'Picked up before' : 'Ready to start'}</div>
        {series.poster_url ? (
          <img alt={series.title} src={series.poster_url} />
        ) : (
          <div className="series-card__placeholder">{series.title.slice(0, 1)}</div>
        )}
      </div>
      <div className="series-card__body">
        <p className="eyebrow">Signature rewatch</p>
        <h3>{series.title}</h3>
        <p>{series.synopsis}</p>
        <div className="series-card__meta">
          <span>{series.stats.total_episodes} episodes</span>
          <span>{series.stats.completion_percent}% complete</span>
        </div>
      </div>
    </Link>
  );
}
