'use client';

import { useEffect, useMemo, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

type WeeklyProgressPoint = {
  day: string;
  completion: number;
};

type PillarDistributionPoint = {
  pillar: 'Cognitive' | 'Physical' | 'Language' | 'Character' | 'Creativity';
  value: number;
};

type DifficultyTrendPoint = {
  date: string;
  difficulty_score: number;
};

type TodayCompletionResponse = {
  completion: number;
};

const COLORS = ['#4f46e5', '#10b981', '#0ea5e9', '#f59e0b', '#d946ef'];

/**
 * Dashboard charts for LifeOS 0-21 using backend analytics endpoints.
 *
 * Endpoints used:
 * - GET /weekly-progress
 * - GET /pillar-distribution
 * - GET /difficulty-trend
 */
export default function DashboardCharts() {
  const [todayCompletion, setTodayCompletion] = useState<number>(0);
  const [weeklyData, setWeeklyData] = useState<WeeklyProgressPoint[]>([]);
  const [pillarData, setPillarData] = useState<PillarDistributionPoint[]>([]);
  const [difficultyData, setDifficultyData] = useState<DifficultyTrendPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [weeklyRes, pillarRes, difficultyRes] = await Promise.all([
          fetch(`${API_BASE_URL}/weekly-progress`, { cache: 'no-store' }),
          fetch(`${API_BASE_URL}/pillar-distribution`, { cache: 'no-store' }),
          fetch(`${API_BASE_URL}/difficulty-trend`, { cache: 'no-store' }),
        ]);

        if (!weeklyRes.ok || !pillarRes.ok || !difficultyRes.ok) {
          throw new Error('Failed to fetch dashboard analytics');
        }

        const weeklyJson = (await weeklyRes.json()) as {
          today: TodayCompletionResponse;
          weekly: WeeklyProgressPoint[];
        };
        const pillarJson = (await pillarRes.json()) as PillarDistributionPoint[];
        const difficultyJson = (await difficultyRes.json()) as DifficultyTrendPoint[];

        setTodayCompletion(weeklyJson.today?.completion ?? 0);
        setWeeklyData(weeklyJson.weekly ?? []);
        setPillarData(pillarJson ?? []);
        setDifficultyData(difficultyJson ?? []);
      } catch (fetchError) {
        setError(fetchError instanceof Error ? fetchError.message : 'Unable to load charts');
      } finally {
        setLoading(false);
      }
    };

    void loadDashboardData();
  }, []);

  const circleData = useMemo(
    () => [
      { name: 'Completed', value: todayCompletion },
      { name: 'Remaining', value: Math.max(0, 100 - todayCompletion) },
    ],
    [todayCompletion],
  );

  return (
    <section className="space-y-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:p-6">
      <header className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Dashboard Analytics</h2>
        {loading ? <span className="text-xs text-slate-500">Loading...</span> : null}
      </header>

      {error ? (
        <p className="rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-2">
        {/* 1) Circle progress for today's completion */}
        <article className="rounded-xl border border-slate-100 bg-slate-50 p-4">
          <h3 className="mb-3 text-sm font-semibold text-slate-700">Today&apos;s Completion</h3>
          <div className="relative h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={circleData}
                  dataKey="value"
                  innerRadius={70}
                  outerRadius={95}
                  startAngle={90}
                  endAngle={-270}
                  paddingAngle={2}
                >
                  <Cell fill="#10b981" />
                  <Cell fill="#e2e8f0" />
                </Pie>
                <Tooltip formatter={(value: number) => `${value}%`} />
              </PieChart>
            </ResponsiveContainer>
            <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <p className="text-3xl font-bold text-slate-900">{todayCompletion}%</p>
                <p className="text-xs text-slate-500">completed</p>
              </div>
            </div>
          </div>
        </article>

        {/* 2) Bar chart for weekly task completion */}
        <article className="rounded-xl border border-slate-100 bg-slate-50 p-4">
          <h3 className="mb-3 text-sm font-semibold text-slate-700">Weekly Task Completion</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="day" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} unit="%" />
                <Tooltip formatter={(value: number) => `${value}%`} />
                <Bar dataKey="completion" radius={[8, 8, 0, 0]} fill="#4f46e5" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>

        {/* 3) Radar chart showing balance across pillars */}
        <article className="rounded-xl border border-slate-100 bg-slate-50 p-4">
          <h3 className="mb-3 text-sm font-semibold text-slate-700">Pillar Balance</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={pillarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="pillar" tick={{ fontSize: 12 }} />
                <Radar
                  name="Completion"
                  dataKey="value"
                  stroke="#0ea5e9"
                  fill="#0ea5e9"
                  fillOpacity={0.35}
                />
                <Tooltip formatter={(value: number) => `${value}%`} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </article>

        {/* 4) Line chart showing difficulty trend */}
        <article className="rounded-xl border border-slate-100 bg-slate-50 p-4">
          <h3 className="mb-3 text-sm font-semibold text-slate-700">Difficulty Progression</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={difficultyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 5]} tick={{ fontSize: 12 }} />
                <Tooltip formatter={(value: number) => value.toFixed(2)} />
                <Line
                  type="monotone"
                  dataKey="difficulty_score"
                  stroke="#f59e0b"
                  strokeWidth={3}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </article>
      </div>

      {/* Small legend for pillar colors used across dashboard themes */}
      <div className="flex flex-wrap gap-2 text-xs text-slate-600">
        {['Cognitive', 'Physical', 'Language', 'Character', 'Creativity'].map((pillar, index) => (
          <span key={pillar} className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-1">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: COLORS[index] }} />
            {pillar}
          </span>
        ))}
      </div>
    </section>
  );
}
