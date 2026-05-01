import Link from "next/link";
import Image from "next/image";
import { CATEGORY_CONFIG, CATEGORY_IMAGES } from "@/lib/constants";
import type { Category, Stats } from "@/lib/types";

export default function CategoryGrid({ stats }: { stats: Stats }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
      {Object.entries(CATEGORY_CONFIG).map(([key, config]) => {
        const count = stats.by_category[key] || 0;
        const img = CATEGORY_IMAGES[key as Category];
        return (
          <Link
            key={key}
            href={`/categories/${key}/`}
            className="relative rounded-lg overflow-hidden no-underline group h-[160px] flex flex-col justify-end"
          >
            {/* Photo background */}
            <Image
              src={img.url}
              alt={img.alt}
              fill
              className="object-cover group-hover:scale-105 transition-transform duration-500"
              sizes="(max-width: 768px) 50vw, 20vw"
            />
            {/* Gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent" />
            {/* Color accent line */}
            <div
              className="absolute top-0 left-0 right-0 h-[3px]"
              style={{ backgroundColor: config.color }}
            />
            {/* Content */}
            <div className="relative z-10 p-3">
              <span className="text-sm font-medium text-white block mb-0.5">
                {config.ja}
              </span>
              <span className="text-[10px] text-white/50 tracking-wider uppercase">
                {count} entries
              </span>
            </div>
          </Link>
        );
      })}
    </div>
  );
}
