import { Link, useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';

import { getSeriesDetail, type SeriesDetail } from '../api/client';
import { EpisodeList } from '../components/EpisodeList';

export function SeriesPage() {
  const { seriesSlug = '' } = useParams();
  const [series, setSeries] = useState<SeriesDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getSeriesDetail(seriesSlug)
      .then(setSeries)
      .catch((requestError) => {
        setError(requestError instanceof Error ? requestError.message : 'Could not load series');
      });
  }, [seriesSlug]);

  if (error) {
    return <div className="panel panel--error">{error}</div>;
  }

  if (!series) {
    return <div className="panel">Opening this story for me...</div>;
  }

  return (
    <section className="stack-lg">
      <Link className="back-link" to="/">
        Back to my library
      </Link>
      <article className="series-hero" style={series.poster_url ? { backgroundImage: `linear-gradient(90deg, rgba(7, 8, 15, 0.94) 0%, rgba(7, 8, 15, 0.74) 52%, rgba(7, 8, 15, 0.1) 100%), url(${series.poster_url})` } : undefined}>
        <div className="series-hero__content">
          <p className="eyebrow">One of my favorites</p>
          <h1>{series.title}</h1>
          <p>{series.synopsis}</p>
          <div className="series-hero__stats">
            <span>{series.stats.total_episodes} episodes</span>
            <span>{series.stats.watched_episodes} finished by me</span>
            <span>{series.stats.completion_percent}% of this rewatch</span>
          </div>
          {series.episodes[0] ? (
            <Link className="primary-button" to={`/player/${series.episodes[0].id}`}>
              Begin again from episode one
            </Link>
          ) : null}
        </div>
        {series.poster_url ? <img alt={series.title} className="series-hero__poster" src={series.poster_url} /> : null}
      </article>
      <EpisodeList episodes={series.episodes} />
    </section>
  );
}
