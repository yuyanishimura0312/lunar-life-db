import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "月面生活リサーチDB | Lunar Life Research Database",
  description:
    "月面生活の課題と技術を世界の研究から集めたデータベース。JAXA Space Life on the Moonをベースに構築。",
};

const NAV_ITEMS = [
  { href: "/", label: "ホーム" },
  { href: "/entries/", label: "エントリ一覧" },
  { href: "/dashboard/", label: "ダッシュボード" },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja" className="h-full">
      <body className="min-h-full flex flex-col">
        <header className="border-b border-border bg-bg-card">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2 no-underline">
              <span
                className="text-lg font-bold tracking-wide"
                style={{ color: "var(--accent)" }}
              >
                LUNAR LIFE DB
              </span>
            </Link>
            <nav className="flex gap-6 text-sm">
              {NAV_ITEMS.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="text-text-muted hover:text-accent transition-colors no-underline"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>

        <main className="flex-1">{children}</main>

        <footer className="border-t border-border bg-bg-card mt-12">
          <div className="max-w-6xl mx-auto px-4 py-6 text-center text-sm text-text-muted">
            <p>
              月面生活リサーチDB &mdash; JAXA &ldquo;Space Life on the
              Moon&rdquo; をベースに構築
            </p>
            <p className="mt-1">NPO法人ミラツク / MIRA TUKU</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
