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


const DEMO_TASKS: DailyTask[] = [
  {
    id: 1001,
    child_id: 1,
    pillar: 'Cognitive',
    title: 'Math Puzzle Sprint',
    description: 'Solve 5 logic problems with a 15-minute timer.',
    duration_minutes: 15,
    difficulty_level: 'medium',
    completed: true,
    completion_timestamp: null,
    date_assigned: new Date().toISOString().slice(0, 10),
  },
  {
    id: 1002,
    child_id: 1,
    pillar: 'Physical',
    title: 'Movement Circuit',
    description: 'Complete 3 rounds of jump, squat, and stretch.',
    duration_minutes: 20,
    difficulty_level: 'easy',
    completed: false,
    completion_timestamp: null,
    date_assigned: new Date().toISOString().slice(0, 10),
  },
  {
    id: 1003,
    child_id: 1,
    pillar: 'Language',
    title: 'Story Retell',
    description: 'Read a short story and summarize it in 5 sentences.',
    duration_minutes: 25,
    difficulty_level: 'medium',
    completed: false,
    completion_timestamp: null,
    date_assigned: new Date().toISOString().slice(0, 10),
  },
  {
    id: 1004,
    child_id: 1,
    pillar: 'Character',
    title: 'Gratitude Reflection',
    description: 'Write down 3 things you are thankful for today.',
    duration_minutes: 10,
    difficulty_level: 'easy',
    completed: true,
    completion_timestamp: null,
    date_assigned: new Date().toISOString().slice(0, 10),
  },
  {
    id: 1005,
    child_id: 1,
    pillar: 'Creativity',
    title: 'Sketch Challenge',
    description: 'Draw your future city in under 20 minutes.',
    duration_minutes: 20,
    difficulty_level: 'hard',
    completed: false,
    completion_timestamp: null,
    date_assigned: new Date().toISOString().slice(0, 10),
  },
];

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
      } catch {
        // Keep the design visible even if backend is unavailable in demo environments.
        setTasks(DEMO_TASKS);
        setError('Live backend unavailable. Showing demo data for executive preview.');
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

    // Demo rows are client-only and should not call the backend.
    if (taskId >= 1000) {
      setTasks((current) =>
        current.map((task) => (task.id === taskId ? { ...task, completed } : task)),
      );
      return;
    }

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

      // Demo mode: acknowledge save locally when sample data is shown.
      if (tasks.some((task) => task.id >= 1000)) {
        setSaveMessage('Demo check-in saved locally. Connect backend to persist.');
        return;
      }

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
