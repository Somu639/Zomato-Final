"use client";

import { useCallback, useEffect, useState } from "react";
import {
  ApiError,
  fetchLocations,
  fetchMetadata,
  postRecommendations,
} from "@/lib/api/client";
import type { MetadataResponse, RecommendationResponse } from "@/lib/api/types";
import Alert from "./Alert";
import PreferenceForm, { FormValues } from "./PreferenceForm";
import RecommendationList from "./RecommendationList";

export default function RecommendPage() {
  const [locations, setLocations] = useState<string[]>([]);
  const [metadata, setMetadata] = useState<MetadataResponse | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [banner, setBanner] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([fetchLocations(), fetchMetadata()])
      .then(([locRes, metaRes]) => {
        setLocations(locRes.locations);
        setMetadata(metaRes);
        setLoadError(null);
      })
      .catch((err: unknown) => {
        const message =
          err instanceof ApiError
            ? err.message
            : "Could not connect to the API. Run `zm api` after `zm load-data`.";
        setLoadError(message);
      });
  }, []);

  const handleSubmit = useCallback(async (values: FormValues) => {
    setLoading(true);
    setFieldErrors({});
    setResult(null);
    setBanner(null);

    const cuisines = values.cuisines
      .split(",")
      .map((c) => c.trim())
      .filter(Boolean);

    const body: Parameters<typeof postRecommendations>[0] = {
      location: values.location,
      cuisines,
      min_rating: parseFloat(values.min_rating) || 0,
      additional: values.additional || null,
      area: values.area.trim() || null,
    };

    if (values.use_inr) {
      const inr = parseInt(values.budget_inr, 10);
      if (!inr || inr < 100) {
        setFieldErrors({ budget_inr: "Enter a valid amount (₹100–₹50,000)" });
        setLoading(false);
        return;
      }
      body.budget_inr = inr;
    } else {
      body.budget = values.budget;
    }

    try {
      const response = await postRecommendations(body);
      setResult(response);
      if (response.warning) setBanner(response.warning);
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 404) {
          setFieldErrors({ _form: err.message });
        } else {
          setFieldErrors(
            Object.keys(err.errors).length
              ? err.errors
              : { _form: err.message },
          );
        }
      } else {
        setFieldErrors({ _form: "Something went wrong. Please try again." });
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const dataReady = locations.length > 0;

  return (
    <div className="page">
      <header className="page__header">
        <h1>ZM Restaurant Recommendations</h1>
        <p className="page__subtitle">
          Next.js UI · structured filters and Groq explanations
        </p>
      </header>

      {loadError && <Alert variant="error">{loadError}</Alert>}
      {!dataReady && !loadError && (
        <Alert variant="warning">
          Loading… Run <code>zm load-data</code> then <code>zm api</code>.
        </Alert>
      )}
      {banner && <Alert variant="warning">{banner}</Alert>}

      <div className="page__layout">
        <section className="page__panel">
          <h2>Your preferences</h2>
          <PreferenceForm
            locations={locations}
            budgets={metadata?.budgets ?? ["low", "medium", "high"]}
            exampleCuisines={metadata?.example_cuisines ?? []}
            budgetInrBands={metadata?.budget_inr_bands}
            disabled={!dataReady}
            loading={loading}
            errors={fieldErrors}
            onSubmit={handleSubmit}
          />
        </section>

        <section className="page__panel">
          <h2>Recommendations</h2>
          {loading && <p className="loading">Searching and ranking…</p>}
          {result && (
            <RecommendationList
              items={result.recommendations}
              summary={result.summary}
              source={result.source}
              cached={result.cached}
            />
          )}
          {!loading && !result && (
            <p className="empty">Submit the form to see ranked restaurants.</p>
          )}
        </section>
      </div>
    </div>
  );
}
