import Link from "next/link";
import { CATEGORY_CONFIG } from "@/lib/constants";
import type { Stats } from "@/lib/types";

const CATEGORY_ICONS: Record<string, string> = {
  food: "M12 2C13.1 2 14 2.9 14 4V8H16V4C16 2.9 16.9 2 18 2S20 2.9 20 4V12H21V14H20V22H18V14H14V22H12V14H4V12H12V4C12 2.9 11.1 2 10 2",
  water: "M12 2C12 2 5 9 5 14C5 17.9 8.1 21 12 21S19 17.9 19 14C19 9 12 2 12 2Z",
  hygiene: "M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z",
  medical: "M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM17 13H13V17H11V13H7V11H11V7H13V11H17V13Z",
  exercise: "M20.57 14.86L22 13.43L20.57 12L17 15.57L8.43 7L12 3.43L10.57 2L9.14 3.43L7.71 2L5.57 4.14L4.14 2.71L2.71 4.14L4.14 5.57L2 7.71L3.43 9.14L2 10.57L3.43 12L7 8.43L15.57 17L12 20.57L13.43 22L14.86 20.57L16.29 22L18.43 19.86L19.86 21.29L21.29 19.86L19.86 18.43L22 16.29L20.57 14.86Z",
  clothing: "M16 21H8C7.45 21 7 20.55 7 20V12L3 8L5 6L8 9H16L19 6L21 8L17 12V20C17 20.55 16.55 21 16 21Z",
  communication: "M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z",
  entertainment: "M21 6H17.8L18.8 4.2L17.2 3.2L15.6 6H8.4L6.8 3.2L5.2 4.2L6.2 6H3C1.9 6 1 6.9 1 8V20C1 21.1 1.9 22 3 22H21C22.1 22 23 21.1 23 20V8C23 6.9 22.1 6 21 6Z",
  sleep_habitat: "M12 3C7.03 3 3 7.03 3 12S7.03 21 12 21S21 16.97 21 12S16.97 3 12 3ZM12 19C8.13 19 5 15.87 5 12S8.13 5 12 5V19Z",
  work_environment: "M22.7 19L13.6 9.9C14.5 7.6 14 4.9 12.1 3C10.1 1 7.1 0.6 4.7 1.7L9 6L6 9L1.6 4.7C0.4 7.1 0.9 10.1 2.9 12.1C4.8 14 7.5 14.5 9.8 13.6L18.9 22.7C19.3 23.1 19.9 23.1 20.3 22.7L22.6 20.4C23.1 19.9 23.1 19.3 22.7 19Z",
};

export default function CategoryGrid({ stats }: { stats: Stats }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
      {Object.entries(CATEGORY_CONFIG).map(([key, config]) => {
        const count = stats.by_category[key] || 0;
        return (
          <Link
            key={key}
            href={`/categories/${key}/`}
            className="flex flex-col items-center gap-2 p-4 rounded-lg border border-border bg-bg-card hover:shadow-md transition-shadow no-underline group"
          >
            <div
              className="w-10 h-10 rounded-full flex items-center justify-center"
              style={{ backgroundColor: config.color + "20" }}
            >
              <svg
                viewBox="0 0 24 24"
                className="w-5 h-5"
                fill={config.color}
              >
                <path d={CATEGORY_ICONS[key]} />
              </svg>
            </div>
            <span className="text-sm font-medium text-text group-hover:text-accent transition-colors">
              {config.ja}
            </span>
            <span className="text-xs text-text-muted">{count}件</span>
          </Link>
        );
      })}
    </div>
  );
}
