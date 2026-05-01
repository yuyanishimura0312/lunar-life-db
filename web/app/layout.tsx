import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Space Life on the Moon | 月面生活リサーチDB",
  description:
    "月面生活の課題と技術を世界の研究から集めたデータベース。JAXA Space Life on the Moonをベースに構築。",
};

const NAV_ITEMS = [
  { href: "/", label: "Home" },
  { href: "/entries/", label: "Entries" },
  { href: "/dashboard/", label: "Dashboard" },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja" className="h-full">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-full flex flex-col">
        <header className="border-b border-border bg-bg-card/80 backdrop-blur-sm sticky top-0 z-50">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3 no-underline">
              <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center">
                <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="var(--accent)" strokeWidth="1.5">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 2a15 15 0 0 1 4 10 15 15 0 0 1-4 10 15 15 0 0 1-4-10A15 15 0 0 1 12 2z" />
                </svg>
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-bold tracking-widest text-text uppercase">
                  Space Life on the Moon
                </span>
                <span className="text-[10px] text-text-muted tracking-wide">
                  Lunar Life Research Database
                </span>
              </div>
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
          <div className="max-w-6xl mx-auto px-4 py-8 text-center text-sm text-text-muted">
            <p className="mb-1 tracking-wide">
              Space Life on the Moon &mdash; Lunar Life Research Database
            </p>
            <p className="text-xs">
              Based on JAXA &ldquo;Space Life on the Moon&rdquo; &middot; NPO MIRA TUKU
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
