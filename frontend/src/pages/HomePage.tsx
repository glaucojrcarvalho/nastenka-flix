import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { getSeriesList, type SeriesSummary } from '../api/client';
import { SeriesCard } from '../components/SeriesCard';

export function HomePage() {
  const [series, setSeries] = useState<SeriesSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const featuredSeries = series[0] ?? null;
  const continueWatching = series.filter((item) => item.stats.completion_percent > 0 && item.stats.completion_percent < 100);

  useEffect(() => {
    getSeriesList()
      .then(setSeries)
      .catch((requestError) => {
        setError(requestError instanceof Error ? requestError.message : 'Could not load series');
      })
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <section className="stack-lg">
      <div
        className="hero-card hero-card--featured"
        style={featuredSeries?.poster_url ? { backgroundImage: `linear-gradient(90deg, rgba(7, 8, 15, 0.9) 0%, rgba(7, 8, 15, 0.72) 45%, rgba(7, 8, 15, 0.18) 100%), url(${featuredSeries.poster_url})` } : undefined}
      >
        <div className="hero-card__content">
          <p className="eyebrow">My comfort collection</p>
          <h1>This is my little world of familiar stories.</h1>
          <p>
            The shows I always come back to, ready for quiet nights, favorite scenes, and one-more-episode decisions.
          </p>
          <div className="hero-card__actions">
            {featuredSeries ? (
              <Link className="primary-button" to={`/series/${featuredSeries.slug}`}>
                Start my next rewatch
              </Link>
            ) : null}
            <span className="hero-chip">Only mine</span>
            <span className="hero-chip">Resume anytime</span>
            <span className="hero-chip">Made with love</span>
          </div>
        </div>
      </div>

      {continueWatching.length > 0 ? (
        <section className="shelf">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Keep watching</p>
              <h2>Right where my last rewatch stopped.</h2>
            </div>
          </div>
          <div className="series-grid series-grid--compact">
            {continueWatching.map((item) => (
              <SeriesCard key={item.id} series={item} />
            ))}
          </div>
        </section>
      ) : null}

      <section className="shelf">
        <div className="section-heading">
          <div>
            <p className="eyebrow">My library</p>
            <h2>The stories I always choose again.</h2>
          </div>
          <p className="section-heading__copy">No endless searching. Just the series that already feel like home to me.</p>
        </div>

        {isLoading ? <div className="panel">Loading my favorites...</div> : null}
        {error ? <div className="panel panel--error">{error}</div> : null}

        {!isLoading && !error ? (
          <div className="series-grid">
            {series.map((item) => (
              <SeriesCard key={item.id} series={item} />
            ))}
          </div>
        ) : null}
      </section>
    </section>
  );
}
