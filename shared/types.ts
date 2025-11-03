/**
 * Shared TypeScript types used across frontend and backend
 */

export interface Area {
  id: string;
  name: string;
  type: 'metro' | 'county';
  state: string;
  state_name: string;
  created_at: string;
}

export interface Rent {
  area_id: string;
  studio_rent: number | null;
  one_bedroom_rent: number | null;
  two_bedroom_rent: number | null;
  three_bedroom_rent: number | null;
  four_bedroom_rent: number | null;
}

export interface AreaWithRent extends Area, Rent {}

export interface PivotRow {
  state?: string;
  type?: string;
  count: number;
  avg_studio?: number;
  avg_one_br?: number;
  avg_two_br?: number;
  avg_three_br?: number;
  avg_four_br?: number;
  min_two_br?: number;
  max_two_br?: number;
}

export interface StatsResponse {
  total_areas: number;
  two_bedroom: {
    min: number;
    max: number;
    average: number;
    median: number;
  };
  by_type: {
    metros: number;
    counties: number;
  };
  by_state: Record<string, number>;
}

export interface PivotResponse {
  data: PivotRow[];
  count: number;
  query: {
    group_by: string[];
    filters?: Record<string, string>;
  };
}

export interface DrilldownResponse {
  data: AreaWithRent[];
  count: number;
  filters: {
    state?: string;
    type?: string;
    search?: string;
  };
}
