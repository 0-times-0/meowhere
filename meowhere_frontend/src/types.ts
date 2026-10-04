export type Species = 'cat' | 'dog' | 'other';
export type ReportStatus = 'lost' | 'found_patrol' | 'resolved';
export type AnimalSex = 'male' | 'female' | 'unknown';
export type UserRole = 'resident' | 'municipal';

export interface Report {
  id: number;
  title: string;
  description?: string | null;
  coat_color?: string | null;
  breed?: string | null;
  sex?: AnimalSex | null;
  shelter_name?: string | null;
  species: Species;
  status: ReportStatus;
  photo_url?: string | null;
  contact_phone?: string | null;
  user_id?: number | null;
  municipal_user_id?: number | null;
  latitude: number;
  longitude: number;
  created_at: string;
}

export interface ReportCreatePayload {
  title: string;
  description?: string;
  coat_color?: string;
  breed?: string;
  sex?: AnimalSex;
  shelter_name?: string;
  species: Species;
  photo_url?: string;
  contact_phone?: string;
  latitude: number;
  longitude: number;
}

export interface ReportMatch {
  report_id: number;
  title: string;
  species: Species;
  status: ReportStatus;
  coat_color?: string | null;
  breed?: string | null;
  shelter_name?: string | null;
  photo_url?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  distance_km?: number | null;
  similarity_score: number;
  reasons: string[];
}

export interface AuthSession {
  access_token: string;
  role: UserRole;
  user_id: number;
  display_name: string;
  identifier: string;
}