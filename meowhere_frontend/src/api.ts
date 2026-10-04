import type {
  AuthSession,
  Report,
  ReportCreatePayload,
  ReportMatch,
} from './types';
import type {Species, ReportStatus} from './types';
const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
const STORAGE_KEY = 'meowhere_auth_session';

export function getStoredSession(): AuthSession | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as AuthSession) : null;
  } catch {
    return null;
  }
}

export function saveSession(session: AuthSession): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

export function clearSession(): void {
  localStorage.removeItem(STORAGE_KEY);
}

export function resolvePhotoUrl(photoUrl?: string | null): string | null {
  if (!photoUrl) return null;
  if (photoUrl.startsWith('http://') || photoUrl.startsWith('https://')) {
    return photoUrl;
  }
  return `${API_BASE}${photoUrl.startsWith('/') ? '' : '/'}${photoUrl}`;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const session = getStoredSession();
  const headers = new Headers(init.headers || {});

  if (!(init.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (session?.access_token) {
    headers.set('Authorization', `Bearer ${session.access_token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const detail =
      (data && (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail))) ||
      `Błąd HTTP ${response.status}`;
    throw new Error(detail);
  }
  return data as T;
}

export async function loginResident(email: string, password: string): Promise<AuthSession> {
  const res = await request<any>('/api/auth/resident/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  const session: AuthSession = {
    access_token: res.access_token,
    role: 'resident',
    user_id: res.user?.id ?? res.user_id ?? 0,
    display_name: res.user?.full_name || email,
    identifier: res.user?.email || email,
  };
  saveSession(session);
  return session;
}

export async function registerResident(payload: {
  email: string;
  password: string;
  full_name: string;
  phone_number?: string;
}): Promise<AuthSession> {
  const res = await request<any>('/api/auth/resident/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  if (res.access_token) {
    const session: AuthSession = {
      access_token: res.access_token,
      role: 'resident',
      user_id: res.user?.id ?? res.user_id ?? 0,
      display_name: res.user?.full_name || payload.full_name,
      identifier: payload.email,
    };
    saveSession(session);
    return session;
  }
  return loginResident(payload.email, payload.password);
}

export async function loginMunicipal(
  badge_number: string,
  password: string
): Promise<AuthSession> {
  const res = await request<any>('/api/auth/municipal/login', {
    method: 'POST',
    body: JSON.stringify({ badge_number, password }),
  });
  const session: AuthSession = {
    access_token: res.access_token,
    role: 'municipal',
    user_id: res.municipal_user?.id ?? res.user?.id ?? res.user_id ?? 0,
    display_name:
      res.municipal_user?.full_name || res.user?.full_name || `Patrol ${badge_number}`,
    identifier: badge_number,
  };
  saveSession(session);
  return session;
}

export interface ReportsQuery {
  species?: Species | '';
  status?: ReportStatus | '';
  lat?: number;
  lon?: number;
  radius_km?: number;
  limit?: number;
}

export async function fetchReports(params: ReportsQuery = {}): Promise<Report[]> {
  const qs = new URLSearchParams();
  if (params.species) qs.set('species', params.species);
  if (params.status) qs.set('status', params.status);
  if (params.lat !== undefined && params.lon !== undefined && params.radius_km !== undefined) {
    qs.set('lat', String(params.lat));
    qs.set('lon', String(params.lon));
    qs.set('radius_km', String(params.radius_km));
  }
  if (params.limit) qs.set('limit', String(params.limit));

  const suffix = qs.toString() ? `?${qs.toString()}` : '';
  return request<Report[]>(`/api/reports/${suffix}`);
}

export async function fetchMyReports(): Promise<Report[]> {
  return request<Report[]>('/api/reports/mine');
}

export async function fetchReportById(id: number): Promise<Report> {
  return request<Report>(`/api/reports/${id}`);
}

export async function fetchReportMatches(id: number): Promise<ReportMatch[]> {
  return request<ReportMatch[]>(`/api/reports/${id}/matches`);
}

export async function createReport(payload: ReportCreatePayload): Promise<Report> {
  return request<Report>('/api/reports/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function resolveReportById(id: number): Promise<Report> {
  return request<Report>(`/api/reports/${id}/resolve`, {
    method: 'PATCH',
  });
}

export async function deleteReportById(id: number): Promise<void> {
  return request<void>(`/api/reports/${id}`, {
    method: 'DELETE',
  });
}

export async function uploadPhoto(file: File): Promise<string> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await request<{ photo_url: string }>('/api/uploads/', {
    method: 'POST',
    body: formData,
  });
  return res.photo_url;
}