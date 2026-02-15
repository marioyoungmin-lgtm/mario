'use client';

import { useEffect, useMemo, useState } from 'react';

import { completeTask, fetchDailyPlan, saveDailyCheckin, type DailyTask } from '../services/api';

type DailyChecklistProps = {
  childId?: number;
};

const PILLAR_COLORS: Record<DailyTask['pillar'], string> = {
  Cognitive: 'bg-indigo-100 text-indigo-700',
  Physical: 'bg-emerald-100 text-emerald-700',
  Language: 'bg-sky-100 text-sky-700',
  Character: 'bg-amber-100 text-amber-700',
  Creativity: 'bg-fuchsia-100 text-fuchsia-700',
};

/**
 * Daily checklist page section for LifeOS 0-21.
 *
 * Features:
 * - Fetches daily tasks from backend
 * - Lets users complete tasks with animated transitions
 * - Collects Joy Score + Parent Notes and submits through API
 */
export default function DailyChecklist({ childId = 1 }: DailyChecklistProps) {
  const [tasks, setTasks] = useState<DailyTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [joyScore, setJoyScore] = useState(3);
  const [parentNotes, setParentNotes] = useState('');
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      try {
        setLoading(true);
        const dailyTasks = await fetchDailyPlan(childId);
        setTasks(dailyTasks);
        setError(null);
      } catch (fetchError) {
        setError(fetchError instanceof Error ? fetchError.message : 'Unable to load daily tasks');
      } finally {
        setLoading(false);
      }
    };

    void run();
  }, [childId]);

  const completionPercentage = useMemo(() => {
    if (!tasks.length) return 0;
    const done = tasks.filter((task) => task.completed).length;
    return Math.round((done / tasks.length) * 100);
  }, [tasks]);

  const onToggleTask = async (taskId: number, completed: boolean) => {
    const previous = tasks;

    // Optimistic UI update for snappy interactions.
    setTasks((current) =>
      current.map((task) => (task.id === taskId ? { ...task, completed } : task)),
    );

    try {
      const updated = await completeTask(taskId, completed);
      setTasks((current) => current.map((task) => (task.id === updated.id ? updated : task)));
    } catch {
      // Revert if backend call fails.
      setTasks(previous);
      setError('Could not update task status. Please try again.');
    }
  };

  const onSubmit = async () => {
    try {
      setSaving(true);
      setSaveMessage(null);
      setError(null);
      await saveDailyCheckin({
        child_id: childId,
        joy_score: joyScore,
        parent_notes: parentNotes,
      });
      setSaveMessage('Saved joy score and notes successfully.');
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Failed to save check-in');
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:p-6">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Daily Checklist</h2>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
          {completionPercentage}% complete
        </span>
      </div>

      {loading && <p className="text-sm text-slate-500">Loading tasks...</p>}
      {error && <p className="mb-3 rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>}

      <div className="space-y-3">
        {tasks.map((task) => (
          <label
            key={task.id}
            className={`group flex items-center gap-3 rounded-xl border p-3 transition-all duration-300 ${
              task.completed
                ? 'border-emerald-200 bg-emerald-50/60 scale-[0.99]'
                : 'border-slate-200 bg-white hover:border-slate-300'
            }`}
          >
            <input
              type="checkbox"
              checked={task.completed}
              onChange={(event) => void onToggleTask(task.id, event.target.checked)}
              className="h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
            />

            <div className="flex min-w-0 flex-1 items-center justify-between gap-2">
              <div className="min-w-0">
                <p
                  className={`truncate text-sm font-medium transition-all duration-300 ${
                    task.completed ? 'text-slate-400 line-through' : 'text-slate-800'
                  }`}
                >
                  {task.title}
                </p>
                <p className="truncate text-xs text-slate-500">{task.description}</p>
              </div>

              <div className="flex shrink-0 items-center gap-2">
                <span
                  className={`rounded-full px-2.5 py-1 text-[11px] font-semibold ${PILLAR_COLORS[task.pillar]}`}
                >
                  {task.pillar}
                </span>
                <span className="text-xs text-slate-500">{task.duration_minutes} min</span>
              </div>
            </div>
          </label>
        ))}
      </div>

      <div className="mt-6 space-y-5 border-t border-slate-100 pt-5">
        <div>
          <div className="mb-2 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-700">Joy Score</h3>
            <span className="text-sm font-medium text-indigo-600">{joyScore}/5</span>
          </div>
          <input
            type="range"
            min={1}
            max={5}
            step={1}
            value={joyScore}
            onChange={(event) => setJoyScore(Number(event.target.value))}
            className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-slate-200"
          />
        </div>

        <div>
          <h3 className="mb-2 text-sm font-semibold text-slate-700">Parent Notes</h3>
          <textarea
            value={parentNotes}
            onChange={(event) => setParentNotes(event.target.value)}
            rows={4}
            placeholder="Share wins, reminders, or encouragement..."
            className="w-full rounded-xl border border-slate-300 p-3 text-sm text-slate-700 outline-none transition focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
          />
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => void onSubmit()}
            disabled={saving}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-indigo-300"
          >
            {saving ? 'Saving...' : 'Save Daily Check-in'}
          </button>
          {saveMessage && <p className="text-sm text-emerald-600">{saveMessage}</p>}
        </div>
      </div>
    </section>
  );
}
