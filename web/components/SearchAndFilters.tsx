"use client";

import { useState, useMemo } from "react";
import type { Entry, Category, EntryType } from "@/lib/types";
import { CATEGORY_CONFIG, ENTRY_TYPE_JA } from "@/lib/constants";
import EntryCard from "./EntryCard";

interface Props {
  entries: Entry[];
  initialCategory?: Category;
}

export default function SearchAndFilters({
  entries,
  initialCategory,
}: Props) {
  const [query, setQuery] = useState("");
  const [selectedCategories, setSelectedCategories] = useState<Set<Category>>(
    initialCategory ? new Set([initialCategory]) : new Set()
  );
  const [selectedOrgs, setSelectedOrgs] = useState<Set<string>>(new Set());
  const [selectedTypes, setSelectedTypes] = useState<Set<EntryType>>(
    new Set()
  );
  const [trlMin, setTrlMin] = useState(0);
  const [sortBy, setSortBy] = useState<"category" | "trl" | "year">(
    "category"
  );
  const [showFilters, setShowFilters] = useState(false);

  const orgs = useMemo(() => {
    const s = new Set<string>();
    entries.forEach((e) => e.source_org && s.add(e.source_org));
    return [...s].sort();
  }, [entries]);

  const filtered = useMemo(() => {
    let result = entries;

    if (query) {
      const q = query.toLowerCase();
      result = result.filter(
        (e) =>
          e.title.toLowerCase().includes(q) ||
          e.title_en?.toLowerCase().includes(q) ||
          e.summary?.toLowerCase().includes(q) ||
          e.keywords_ja?.toLowerCase().includes(q) ||
          e.keywords_en?.toLowerCase().includes(q) ||
          e.source_org?.toLowerCase().includes(q) ||
          e.tags?.some((t) => t.toLowerCase().includes(q))
      );
    }

    if (selectedCategories.size > 0) {
      result = result.filter((e) => selectedCategories.has(e.category));
    }

    if (selectedOrgs.size > 0) {
      result = result.filter(
        (e) => e.source_org && selectedOrgs.has(e.source_org)
      );
    }

    if (selectedTypes.size > 0) {
      result = result.filter((e) => selectedTypes.has(e.entry_type));
    }

    if (trlMin > 0) {
      result = result.filter((e) => e.trl && e.trl >= trlMin);
    }

    // Sort
    result = [...result].sort((a, b) => {
      if (sortBy === "trl") return (b.trl || 0) - (a.trl || 0);
      if (sortBy === "year")
        return (b.source_year || 0) - (a.source_year || 0);
      return a.category.localeCompare(b.category);
    });

    return result;
  }, [entries, query, selectedCategories, selectedOrgs, selectedTypes, trlMin, sortBy]);

  const toggleSet = <T,>(set: Set<T>, item: T, setter: (s: Set<T>) => void) => {
    const next = new Set(set);
    next.has(item) ? next.delete(item) : next.add(item);
    setter(next);
  };

  return (
    <div>
      {/* Search bar */}
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search entries..."
          className="flex-1 px-4 py-2 border border-border rounded-lg bg-bg-card text-text placeholder:text-text-muted/50 focus:outline-none focus:ring-1 focus:ring-accent/50 focus:border-accent/50"
        />
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`px-4 py-2 border rounded-lg text-sm transition-colors ${
            showFilters
              ? "border-accent/50 bg-accent/10 text-accent"
              : "border-border bg-bg-card text-text-muted hover:border-accent/30"
          }`}
        >
          Filters {showFilters ? "−" : "+"}
        </button>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
          className="px-3 py-2 border border-border rounded-lg bg-bg-card text-sm text-text"
        >
          <option value="category">Category</option>
          <option value="trl">TRL (high)</option>
          <option value="year">Year (new)</option>
        </select>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="border border-border rounded-lg p-4 mb-4 bg-bg-card space-y-4">
          {/* Categories */}
          <div>
            <p className="text-xs font-medium text-text-muted mb-2">
              Category
            </p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(CATEGORY_CONFIG).map(([key, config]) => (
                <button
                  key={key}
                  onClick={() =>
                    toggleSet(
                      selectedCategories,
                      key as Category,
                      setSelectedCategories
                    )
                  }
                  className="px-3 py-1 rounded-full text-xs border transition-colors"
                  style={{
                    backgroundColor: selectedCategories.has(key as Category)
                      ? config.color
                      : "transparent",
                    color: selectedCategories.has(key as Category)
                      ? "white"
                      : config.color,
                    borderColor: selectedCategories.has(key as Category)
                      ? config.color
                      : config.color + "60",
                  }}
                >
                  {config.ja}
                </button>
              ))}
            </div>
          </div>

          {/* Entry types */}
          <div>
            <p className="text-xs font-medium text-text-muted mb-2">Type</p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(ENTRY_TYPE_JA).map(([key, label]) => (
                <button
                  key={key}
                  onClick={() =>
                    toggleSet(
                      selectedTypes,
                      key as EntryType,
                      setSelectedTypes
                    )
                  }
                  className={`px-3 py-1 rounded-full text-xs border transition-colors ${
                    selectedTypes.has(key as EntryType)
                      ? "bg-accent text-white border-accent"
                      : "bg-transparent text-text-muted border-border hover:border-accent/30"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Organizations */}
          <div>
            <p className="text-xs font-medium text-text-muted mb-2">Organization</p>
            <div className="flex flex-wrap gap-2">
              {orgs.map((org) => (
                <button
                  key={org}
                  onClick={() =>
                    toggleSet(selectedOrgs, org, setSelectedOrgs)
                  }
                  className={`px-3 py-1 rounded-full text-xs border transition-colors ${
                    selectedOrgs.has(org)
                      ? "bg-accent text-white border-accent"
                      : "bg-transparent text-text-muted border-border hover:border-accent/30"
                  }`}
                >
                  {org}
                </button>
              ))}
            </div>
          </div>

          {/* TRL filter */}
          <div>
            <p className="text-xs font-medium text-text-muted mb-2">
              Min TRL: {trlMin || "Any"}
            </p>
            <input
              type="range"
              min="0"
              max="9"
              value={trlMin}
              onChange={(e) => setTrlMin(Number(e.target.value))}
              className="w-full accent-accent"
            />
          </div>

          {/* Reset */}
          <button
            onClick={() => {
              setSelectedCategories(new Set());
              setSelectedOrgs(new Set());
              setSelectedTypes(new Set());
              setTrlMin(0);
              setQuery("");
            }}
            className="text-xs text-accent hover:underline"
          >
            Reset filters
          </button>
        </div>
      )}

      {/* Results count */}
      <p className="text-sm text-text-muted mb-4">
        {filtered.length} entries
      </p>

      {/* Results grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((entry) => (
          <EntryCard key={entry.id} entry={entry} />
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-16 text-text-muted">
          <p>No matching entries found</p>
        </div>
      )}
    </div>
  );
}
