import { getStats } from "@/lib/data";
import { CATEGORY_CONFIG, ENTRY_TYPE_JA } from "@/lib/constants";

function BarChart({
  data,
  labels,
  colors,
  maxWidth = 100,
}: {
  data: Record<string, number>;
  labels?: Record<string, string>;
  colors?: Record<string, string>;
  maxWidth?: number;
}) {
  const entries = Object.entries(data).sort(([, a], [, b]) => b - a);
  const max = Math.max(...entries.map(([, v]) => v), 1);

  return (
    <div className="space-y-2">
      {entries.map(([key, value]) => (
        <div key={key} className="flex items-center gap-3">
          <span className="text-xs text-text-muted w-28 text-right shrink-0 truncate">
            {labels?.[key] || key}
          </span>
          <div className="flex-1 h-5 bg-bg-surface rounded overflow-hidden">
            <div
              className="h-full rounded transition-all"
              style={{
                width: `${(value / max) * maxWidth}%`,
                backgroundColor:
                  colors?.[key] || "var(--accent)",
              }}
            />
          </div>
          <span className="text-xs font-medium text-text w-8 text-right">
            {value}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function DashboardPage() {
  const stats = getStats();

  const categoryLabels = Object.fromEntries(
    Object.entries(CATEGORY_CONFIG).map(([k, v]) => [k, v.ja])
  );
  const categoryColors = Object.fromEntries(
    Object.entries(CATEGORY_CONFIG).map(([k, v]) => [k, v.color])
  );

  const trlLabels: Record<string, string> = {};
  for (let i = 1; i <= 9; i++) trlLabels[String(i)] = `TRL ${i}`;

  const trlColors: Record<string, string> = {};
  for (let i = 1; i <= 3; i++) trlColors[String(i)] = "#EF5350";
  for (let i = 4; i <= 6; i++) trlColors[String(i)] = "#FFA726";
  for (let i = 7; i <= 9; i++) trlColors[String(i)] = "#66BB6A";

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-light text-text mb-1 tracking-wide">Dashboard</h1>
      <p className="text-xs text-text-muted mb-8">データベースの概況</p>

      {/* KPI cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        {[
          { label: "Entries", value: stats.total_entries },
          { label: "Organizations", value: stats.total_organizations },
          { label: "Categories", value: 10 },
          { label: "Challenges", value: stats.total_challenges },
        ].map((kpi) => (
          <div
            key={kpi.label}
            className="bg-bg-card border border-border rounded-lg p-5 text-center"
          >
            <p className="text-3xl font-light mb-1 text-accent">
              {kpi.value}
            </p>
            <p className="text-xs text-text-muted tracking-wider uppercase">{kpi.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-bg-card border border-border rounded-lg p-5">
          <h2 className="text-xs font-medium text-text-muted mb-4 tracking-wider uppercase">
            By Category
          </h2>
          <BarChart
            data={stats.by_category}
            labels={categoryLabels}
            colors={categoryColors}
          />
        </div>

        <div className="bg-bg-card border border-border rounded-lg p-5">
          <h2 className="text-xs font-medium text-text-muted mb-4 tracking-wider uppercase">
            By Organization
          </h2>
          <BarChart data={stats.by_source_org} />
        </div>

        <div className="bg-bg-card border border-border rounded-lg p-5">
          <h2 className="text-xs font-medium text-text-muted mb-4 tracking-wider uppercase">
            TRL Distribution
          </h2>
          <BarChart
            data={stats.by_trl}
            labels={trlLabels}
            colors={trlColors}
          />
        </div>

        <div className="bg-bg-card border border-border rounded-lg p-5">
          <h2 className="text-xs font-medium text-text-muted mb-4 tracking-wider uppercase">
            By Type
          </h2>
          <BarChart
            data={stats.by_entry_type}
            labels={ENTRY_TYPE_JA as Record<string, string>}
          />
        </div>

        <div className="bg-bg-card border border-border rounded-lg p-5">
          <h2 className="text-xs font-medium text-text-muted mb-4 tracking-wider uppercase">
            By Timeline
          </h2>
          <BarChart data={stats.by_timeline} />
        </div>

        <div className="bg-bg-card border border-border rounded-lg p-5">
          <h2 className="text-xs font-medium text-text-muted mb-4 tracking-wider uppercase">
            By Country
          </h2>
          <BarChart data={stats.by_country} />
        </div>
      </div>
    </div>
  );
}
