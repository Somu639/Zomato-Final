"use client";

import { useCallback, useState } from "react";
import { ApiError, postRecommendations } from "@/lib/api/client";
import type { RecommendationResponse } from "@/lib/api/types";
import { useApiBootstrap } from "@/hooks/useApiBootstrap";
import Alert from "./Alert";
import PreferenceForm, { FormValues } from "./PreferenceForm";
import RecommendationList from "./RecommendationList";

export default function RecommendPage() {
  const {
    locations,
    metadata,
    bootstrapping,
    dataLoading,
    loadError,
    dataReady,
  } = useApiBootstrap();

  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [banner, setBanner] = useState<string | null>(null);

  const handleSubmit = useCallback(async (values: FormValues) => {
    setLoading(true);
    setFieldErrors({});
    setResult(null);
    setBanner(null);

    const cuisines = values.cuisines
      .split(",")
      .map((c) => c.trim())
      .filter(Boolean);

    if (!cuisines.length) {
      setFieldErrors({ cuisines: "Enter at least one cuisine." });
      setLoading(false);
      return;
    }

    const body: Parameters<typeof postRecommendations>[0] = {
      location: values.location,
      cuisines,
      min_rating: parseFloat(values.min_rating) || 0,
      additional: values.additional.trim() || null,
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

  return (
    <div className="page">
      <header className="page__header">
        <p className="page__eyebrow">Zomato-inspired discovery</p>
        <h1>ZM Restaurant Recommendations</h1>
        <p className="page__subtitle">
          Tell us your location, budget, cuisine, and minimum rating — we filter
          real restaurant data and rank matches with AI explanations.
        </p>
      </header>

      {loadError && <Alert variant="error">{loadError}</Alert>}
      {bootstrapping && !loadError && (
        <Alert variant="info">Connecting to the recommendation API…</Alert>
      )}
      {dataLoading && !loadError && (
        <Alert variant="warning">
          Restaurant data is loading on the server (first deploy may take 1–3
          minutes). This page will update automatically.
        </Alert>
      )}
      {!dataReady && !loadError && !bootstrapping && !dataLoading && (
        <Alert variant="warning">
          No cities available yet. Ensure the Railway API has finished loading
          data, then refresh.
        </Alert>
      )}
      {banner && <Alert variant="warning">{banner}</Alert>}

      <div className="page__layout">
        <section className="page__panel" aria-labelledby="prefs-heading">
          <h2 id="prefs-heading">Your preferences</h2>
          <PreferenceForm
            locations={locations}
            budgets={metadata?.budgets ?? ["low", "medium", "high"]}
            exampleCuisines={metadata?.example_cuisines ?? []}
            budgetInrBands={metadata?.budget_inr_bands}
            disabled={!dataReady || bootstrapping}
            loading={loading}
            errors={fieldErrors}
            onSubmit={handleSubmit}
          />
        </section>

        <section className="page__panel" aria-labelledby="results-heading">
          <h2 id="results-heading">Recommendations</h2>
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
            <p className="empty">
              Submit your preferences to see top picks with name, cuisine,
              rating, estimated cost, and an AI explanation for each.
            </p>
          )}
        </section>
      </div>

      <footer className="page__footer">
        <p>
          Powered by structured filters + Groq · API on Railway · UI on Vercel
        </p>
      </footer>
    </div>
  );
}
