// src/types.ts
export interface Report {
  id: number
  title: string
  description: string
  species: string
  status: string
  photo_url: string
  contact_phone: string
  latitude: number
  longitude: number
  created_at: string
  coat_color?: string
  breed?: string
  sex?: string
}

export interface CreateReportInput {
  title: string
  description: string
  coat_color: string
  breed: string
  sex: string
  species: string
  status: string
  photo_url: string
  contact_phone: string
  latitude: number
  longitude: number
}