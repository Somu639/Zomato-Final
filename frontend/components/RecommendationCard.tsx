import type { RecommendationItem } from "@/lib/api/types";

interface RecommendationCardProps {
  item: RecommendationItem;
}

export default function RecommendationCard({ item }: RecommendationCardProps) {
  const rating =
    item.rating !== null && item.rating !== undefined
      ? item.rating.toFixed(1)
      : "N/A";

  return (
    <article className="card">
      <header className="card__header">
        <span className="card__rank">#{item.rank}</span>
        <h3 className="card__title">{item.name}</h3>
      </header>
      <dl className="card__meta">
        <div>
          <dt>Cuisine</dt>
          <dd>{item.cuisines.join(", ")}</dd>
        </div>
        <div>
          <dt>Rating</dt>
          <dd>{rating}</dd>
        </div>
        <div>
          <dt>Cost</dt>
          <dd>{item.estimated_cost}</dd>
        </div>
      </dl>
      <p className="card__explanation">{item.explanation}</p>
    </article>
  );
}
