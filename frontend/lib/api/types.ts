export interface RecommendationRequest {
  location: string;
  budget?: string;
  budget_inr?: number | null;
  cuisines: string[] | string;
  min_rating: number;
  additional?: string | null;
  area?: string | null;
}

export interface FilterStats {
  location_count: number;
  after_rating: number;
  after_cuisine: number;
  after_budget: number;
  after_top_k: number;
}

export interface Preferences {
  location: string;
  budget: string;
  cuisines: string[];
  min_rating: number;
  additional?: string | null;
  area?: string | null;
  budget_inr?: number | null;
}

export interface RecommendationItem {
  restaurant_id: string;
  rank: number;
  name: string;
  cuisines: string[];
  rating: number | null;
  estimated_cost: string;
  explanation: string;
}

export interface RecommendationResponse {
  ok: true;
  source: string;
  warning: string | null;
  summary: string | null;
  preferences: Preferences;
  filter_stats: FilterStats;
  recommendations: RecommendationItem[];
  cached?: boolean;
}

export interface ErrorResponse {
  ok: false;
  message: string;
  errors: Record<string, string>;
}

export interface LocationsResponse {
  locations: string[];
}

export interface BudgetInrBands {
  low_max: number;
  medium_max: number;
  description: string;
}

export interface MetadataResponse {
  budgets: string[];
  example_cuisines: string[];
  display_top_n: number;
  budget_inr_bands: BudgetInrBands;
}
