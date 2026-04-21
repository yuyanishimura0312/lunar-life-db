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
          <div className="flex-1 h-6 bg-gray-100 rounded overflow-hidden">
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
  for (let i = 1; i <= 3; i++) trlColors[String(i)] = "#DC8766";
  for (let i = 4; i <= 6; i++) trlColors[String(i)] = "#F0A671";
  for (let i = 7; i <= 9; i++) trlColors[String(i)] = "#7A4033";

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-text mb-8">ダッシュボード</h1>

      {/* KPI cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        {[
          { label: "エントリ数", value: stats.total_entries },
          { label: "組織数", value: stats.total_organizations },
          { label: "カテゴリ", value: 10 },
          { label: "課題数", value: stats.total_challenges },
        ].map((kpi) => (
          <div
            key={kpi.label}
            className="bg-bg-card border border-border rounded-lg p-5 text-center"
          >
            <p
              className="text-3xl font-bold mb-1"
              style={{ color: "var(--accent)" }}
            >
              {kpi.value}
            </p>
            <p className="text-sm text-text-muted">{kpi.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* By category */}
        <div className="bg-bg-card border border-border rounded-lg p-5">
          <h2 className="text-sm font-medium text-text-muted mb-4">
            カテゴリ別エントリ数
          </h2>
          <BarChart
            data={stats.by_category}
            labels={categoryLabels}
            colors={categoryColors}
          />
        </div>

        {/* By source org */}
        <div className="bg-bg-card border border-border rounded-lg p-5">
          <h2 className="text-sm font-medium text-text-muted mb-4">
            組織別エントリ数
          </h2>
          <BarChart data={stats.by_source_org} />
        </div>

        {/* By TRL */}
        <div className="bg-bg-card border border-border rounded-lg p-5">
          <h2 className="text-sm font-medium text-text-muted mb-4">
            技術成熟度 (TRL) 分布
          </h2>
          <BarChart
            data={stats.by_trl}
            labels={trlLabels}
            colors={trlColors}
          />
        </div>

        {/* By entry type */}
        <div className="bg-bg-card border border-border rounded-lg p-5">
          <h2 className="text-sm font-medium text-text-muted mb-4">
            エントリタイプ別
          </h2>
          <BarChart
            data={stats.by_entry_type}
            labels={ENTRY_TYPE_JA as Record<string, string>}
          />
        </div>

        {/* By timeline */}
        <div className="bg-bg-card border border-border rounded-lg p-5">
          <h2 className="text-sm font-medium text-text-muted mb-4">
            タイムライン別
          </h2>
          <BarChart data={stats.by_timeline} />
        </div>

        {/* By country */}
        <div className="bg-bg-card border border-border rounded-lg p-5">
          <h2 className="text-sm font-medium text-text-muted mb-4">
            国・地域別
          </h2>
          <BarChart data={stats.by_country} />
        </div>
      </div>
    </div>
  );
}
