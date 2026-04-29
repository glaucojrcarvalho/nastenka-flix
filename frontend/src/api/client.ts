const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';
const API_ORIGIN = API_BASE_URL.replace(/\/api\/?$/, '');
const TOKEN_STORAGE_KEY = 'nastenka-flix-token';

let authToken = localStorage.getItem(TOKEN_STORAGE_KEY);

export type User = {
  id: number;
  username: string;
  display_name: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type SeriesStats = {
  total_episodes: number;
  watched_episodes: number;
  completion_percent: number;
};

export type SeriesSummary = {
  id: number;
  slug: string;
  title: string;
  synopsis: string;
  poster_url: string | null;
  seasons_count: number;
  stats: SeriesStats;
};

export type EpisodeSummary = {
  id: number;
  series_slug: string;
  season_number: number;
  episode_number: number;
  title: string;
  description: string;
  duration_seconds: number;
  media_url: string;
};

export type EpisodeDetail = EpisodeSummary & {
  thumbnail_url: string | null;
};

export type SeriesDetail = SeriesSummary & {
  episodes: EpisodeSummary[];
};

export type ProgressResponse = {
  episode_id: number;
  position_seconds: number;
  completed: boolean;
};

type RequestOptions = RequestInit & {
  authenticated?: boolean;
};

export function setAuthToken(token: string | null) {
  authToken = token;
  if (token) {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
    return;
  }
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export function getStoredToken() {
  return authToken;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');

  if (options.authenticated !== false && authToken) {
    headers.set('Authorization', `Bearer ${authToken}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(errorBody || `Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export function login(username: string, password: string) {
  return request<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
    authenticated: false,
  });
}

export function getCurrentUser() {
  return request<User>('/auth/me');
}

export function getSeriesList() {
  return request<SeriesSummary[]>('/series/');
}

export function getSeriesDetail(slug: string) {
  return request<SeriesDetail>(`/series/${slug}`);
}

export function getEpisode(id: number) {
  return request<EpisodeDetail>(`/episodes/${id}`);
}

export function getEpisodeProgress(id: number) {
  return request<ProgressResponse>(`/progress/episodes/${id}`);
}

export function updateEpisodeProgress(id: number, positionSeconds: number, completed: boolean) {
  return request<ProgressResponse>(`/progress/episodes/${id}`, {
    method: 'POST',
    body: JSON.stringify({ position_seconds: positionSeconds, completed }),
  });
}

export function resolveMediaUrl(mediaUrl: string) {
  if (mediaUrl.startsWith('http://') || mediaUrl.startsWith('https://')) {
    return mediaUrl;
  }
  return `${API_ORIGIN}${mediaUrl}`;
}
