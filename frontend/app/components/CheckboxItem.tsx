'use client';

/** Reusable checkbox row for a single checklist task item. */

type CheckboxItemProps = {
  label: string;
  checked: boolean;
  onToggle: () => void;
};

export default function CheckboxItem({ label, checked, onToggle }: CheckboxItemProps) {
  return (
    <label className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white p-3 shadow-sm">
      <input
        type="checkbox"
        checked={checked}
        onChange={onToggle}
        className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
      />
      <span className={`text-sm ${checked ? 'text-slate-400 line-through' : 'text-slate-800'}`}>{label}</span>
    </label>
  );
}
