'use client';

import { useState } from 'react';

/**
 * Slider used to track daily joy score (0-10).
 */
export default function JoyScoreSlider() {
  const [score, setScore] = useState(5);

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="mb-2 text-sm font-semibold text-slate-700">Daily Joy Score</h3>
      <input
        type="range"
        min={0}
        max={10}
        value={score}
        onChange={(event) => setScore(Number(event.target.value))}
        className="w-full"
      />
      <p className="mt-2 text-xs text-slate-600">Current score: {score}/10</p>
    </section>
  );
}
