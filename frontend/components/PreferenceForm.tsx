"use client";

import { FormEvent, useState } from "react";
import Alert from "./Alert";
import type { BudgetInrBands } from "@/lib/api/types";

export interface FormValues {
  location: string;
  budget: string;
  budget_inr: string;
  use_inr: boolean;
  cuisines: string;
  min_rating: string;
  additional: string;
  area: string;
}

interface PreferenceFormProps {
  locations: string[];
  budgets: string[];
  exampleCuisines: string[];
  budgetInrBands?: BudgetInrBands;
  disabled?: boolean;
  loading?: boolean;
  errors?: Record<string, string>;
  onSubmit: (values: FormValues) => void;
}

const defaultValues: FormValues = {
  location: "",
  budget: "medium",
  budget_inr: "2000",
  use_inr: true,
  cuisines: "",
  min_rating: "4.0",
  additional: "",
  area: "",
};

export default function PreferenceForm({
  locations,
  budgets,
  exampleCuisines,
  budgetInrBands,
  disabled,
  loading,
  errors = {},
  onSubmit,
}: PreferenceFormProps) {
  const [values, setValues] = useState<FormValues>(defaultValues);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    onSubmit(values);
  };

  const set = (field: keyof FormValues, value: string | boolean) => {
    setValues((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <form className="form" onSubmit={handleSubmit}>
      <div className="form__field">
        <label htmlFor="location">City</label>
        <select
          id="location"
          value={values.location}
          onChange={(e) => set("location", e.target.value)}
          disabled={disabled || loading}
          required
        >
          <option value="">Select a city</option>
          {locations.map((loc) => (
            <option key={loc} value={loc}>
              {loc}
            </option>
          ))}
        </select>
        {errors.location && <p className="form__error">{errors.location}</p>}
      </div>

      <div className="form__field">
        <label htmlFor="area">Area (optional)</label>
        <input
          id="area"
          type="text"
          placeholder="e.g. Bellandur"
          value={values.area}
          onChange={(e) => set("area", e.target.value)}
          disabled={disabled || loading}
        />
      </div>

      <div className="form__field">
        <label>
          <input
            type="checkbox"
            checked={values.use_inr}
            onChange={(e) => set("use_inr", e.target.checked)}
            disabled={disabled || loading}
          />{" "}
          Budget in ₹ (for two)
        </label>
        {values.use_inr ? (
          <>
            <input
              id="budget_inr"
              type="number"
              min={100}
              max={50000}
              step={100}
              value={values.budget_inr}
              onChange={(e) => set("budget_inr", e.target.value)}
              disabled={disabled || loading}
            />
            {budgetInrBands && (
              <p className="form__hint">{budgetInrBands.description}</p>
            )}
          </>
        ) : (
          <select
            id="budget"
            value={values.budget}
            onChange={(e) => set("budget", e.target.value)}
            disabled={disabled || loading}
          >
            {budgets.map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>
        )}
        {errors.budget && <p className="form__error">{errors.budget}</p>}
        {errors.budget_inr && (
          <p className="form__error">{errors.budget_inr}</p>
        )}
      </div>

      <div className="form__field">
        <label htmlFor="cuisines">Cuisines</label>
        <input
          id="cuisines"
          type="text"
          placeholder={exampleCuisines.join(", ")}
          value={values.cuisines}
          onChange={(e) => set("cuisines", e.target.value)}
          disabled={disabled || loading}
          required
        />
        <p className="form__hint">Comma-separated</p>
        {errors.cuisines && <p className="form__error">{errors.cuisines}</p>}
      </div>

      <div className="form__field">
        <label htmlFor="min_rating">Minimum rating</label>
        <input
          id="min_rating"
          type="number"
          min={0}
          max={5}
          step={0.1}
          value={values.min_rating}
          onChange={(e) => set("min_rating", e.target.value)}
          disabled={disabled || loading}
        />
        {errors.min_rating && (
          <p className="form__error">{errors.min_rating}</p>
        )}
      </div>

      <div className="form__field">
        <label htmlFor="additional">Additional preferences</label>
        <textarea
          id="additional"
          rows={3}
          placeholder="e.g. family-friendly, quick service, outdoor seating, dietary needs"
          value={values.additional}
          onChange={(e) => set("additional", e.target.value)}
          disabled={disabled || loading}
        />
        <p className="form__hint">
          Optional — area hints, ambiance, or budget for two in notes
        </p>
      </div>

      {errors._form && <Alert variant="error">{errors._form}</Alert>}

      <button
        type="submit"
        className="btn btn--primary"
        disabled={disabled || loading || !values.location}
      >
        {loading ? "Finding restaurants…" : "Get recommendations"}
      </button>
    </form>
  );
}
