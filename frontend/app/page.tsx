import DailyChecklist from './components/DailyChecklist';

/**
 * Main LifeOS 0-21 page.
 *
 * Renders the daily checklist experience with task completion,
 * joy score tracking, and parent notes submission.
 */
export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-50 p-6 md:p-10">
      <div className="mx-auto max-w-4xl space-y-6">
        <header>
          <h1 className="text-3xl font-bold text-slate-900">LifeOS 0-21</h1>
          <p className="mt-1 text-sm text-slate-600">
            Complete daily growth tasks, track joy, and keep parent notes in one place.
          </p>
        </header>

        <DailyChecklist childId={1} />
      </div>
    </main>
  );
}
