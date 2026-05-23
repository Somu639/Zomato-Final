import type {
  ErrorResponse,
  LocationsResponse,
  MetadataResponse,
  RecommendationRequest,
  RecommendationResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export class ApiError extends Error {
  status: number;
  errors: Record<string, string>;

  constructor(
    status: number,
    message: string,
    errors: Record<string, string> = {},
  ) {
    super(message);
    this.status = status;
    this.errors = errors;
  }
}

async function parseJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (!text) {
    throw new ApiError(response.status, "Empty response from server");
  }
  return JSON.parse(text) as T;
}

export async function fetchLocations(): Promise<LocationsResponse> {
  const response = await fetch(`${API_BASE}/api/v1/locations`, {
    cache: "no-store",
  });
  if (!response.ok) {
    const body = await parseJson<ErrorResponse>(response).catch(() => null);
    throw new ApiError(
      response.status,
      body?.message ?? "Failed to load locations",
      body?.errors,
    );
  }
  return parseJson<LocationsResponse>(response);
}

export async function fetchMetadata(): Promise<MetadataResponse> {
  const response = await fetch(`${API_BASE}/api/v1/metadata`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new ApiError(response.status, "Failed to load metadata");
  }
  return parseJson<MetadataResponse>(response);
}

export async function postRecommendations(
  body: RecommendationRequest,
): Promise<RecommendationResponse> {
  const response = await fetch(`${API_BASE}/api/v1/recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });

  if (!response.ok) {
    const err = await parseJson<ErrorResponse>(response).catch(() => ({
      ok: false as const,
      message: "Request failed",
      errors: {},
    }));
    throw new ApiError(response.status, err.message, err.errors);
  }

  return parseJson<RecommendationResponse>(response);
}
