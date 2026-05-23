import type { RecommendationItem } from "@/lib/api/types";
import RecommendationCard from "./RecommendationCard";

interface RecommendationListProps {
  items: RecommendationItem[];
  summary?: string | null;
  source?: string;
  cached?: boolean;
}

export default function RecommendationList({
  items,
  summary,
  source,
  cached,
}: RecommendationListProps) {
  if (!items.length) return null;

  const sourceLabel =
    source === "groq"
      ? "Groq AI"
      : source === "fallback"
        ? "Rule-based"
        : source;

  return (
    <section className="results">
      {summary && <p className="results__summary">{summary}</p>}
      <p className="results__source">
        Ranked by {sourceLabel}
        {cached ? " · served from cache" : ""}
      </p>
      <div className="results__grid">
        {items.map((item) => (
          <RecommendationCard key={item.restaurant_id} item={item} />
        ))}
      </div>
    </section>
  );
}
