import DailyChecklist from './components/DailyChecklist';
import DashboardCharts from './components/DashboardCharts';

/**
 * Main LifeOS 0-21 page.
 *
 * Renders an executive-friendly layout with:
 * - Daily checklist and check-in actions
 * - KPI cards for quick scanning
 * - Visual analytics charts
 */
export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-white p-6 md:p-10">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h1 className="text-3xl font-bold text-slate-900">LifeOS 0-21</h1>
          <p className="mt-1 text-sm text-slate-600">
            Executive view of daily growth tasks, joy score trends, and parent insights.
          </p>
        </header>

        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Today's Completion</p>
            <p className="mt-2 text-2xl font-bold text-slate-900">68%</p>
          </article>
          <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Joy Score</p>
            <p className="mt-2 text-2xl font-bold text-indigo-600">4.2 / 5</p>
          </article>
          <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Top Pillar</p>
            <p className="mt-2 text-2xl font-bold text-emerald-600">Character</p>
          </article>
          <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Focus Area</p>
            <p className="mt-2 text-2xl font-bold text-amber-600">Language</p>
          </article>
        </section>

        <div className="grid gap-6 lg:grid-cols-5">
          <div className="lg:col-span-3">
            <DailyChecklist childId={1} />
          </div>
          <div className="lg:col-span-2">
            <DashboardCharts />
          </div>
        </div>
      </div>
    </main>
  );
}
