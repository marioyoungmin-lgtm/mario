'use client';

import { useState } from 'react';

/**
 * Parent notes panel for encouragement, reminders, or praise.
 */
export default function ParentNotes() {
  const [notes, setNotes] = useState('Great effort this week—keep building your morning routine!');

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="mb-2 text-sm font-semibold text-slate-700">Parent Notes</h3>
      <textarea
        value={notes}
        onChange={(event) => setNotes(event.target.value)}
        rows={4}
        className="w-full rounded-md border border-slate-300 p-2 text-sm focus:border-indigo-400 focus:outline-none"
      />
      <p className="mt-2 text-xs text-slate-500">These notes can be synced with the daily plan endpoint.</p>
    </section>
  );
}
