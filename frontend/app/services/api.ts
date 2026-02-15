/**
 * API client helpers for communicating with the FastAPI backend.
 *
 * Keeping fetch wrappers here avoids repeating URLs and options in components.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

export type DailyTask = {
  id: number;
  child_id: number;
  pillar: 'Cognitive' | 'Physical' | 'Language' | 'Character' | 'Creativity';
  title: string;
  description: string;
  duration_minutes: number;
  difficulty_level: 'easy' | 'medium' | 'hard';
  completed: boolean;
  completion_timestamp?: string | null;
  date_assigned: string;
};

export type SaveCheckinPayload = {
  child_id: number;
  joy_score: number;
  parent_notes: string;
};

/** Fetch today's generated daily plan tasks for one child profile. */
export async function fetchDailyPlan(childId: number): Promise<DailyTask[]> {
  const response = await fetch(`${API_BASE_URL}/daily-plan/${childId}`, {
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error('Failed to fetch daily plan');
  }

  return response.json();
}

/** Toggle completion status for a single daily task. */
export async function completeTask(taskId: number, completed: boolean): Promise<DailyTask> {
  const response = await fetch(`${API_BASE_URL}/tasks/complete_task`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task_id: taskId, completed }),
  });

  if (!response.ok) {
    throw new Error('Failed to update task status');
  }

  return response.json();
}

/**
 * Save joy score + notes for the day.
 *
 * Expected backend endpoint (to implement server-side): POST /daily-plan/{child_id}/checkin
 */
export async function saveDailyCheckin(payload: SaveCheckinPayload): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/daily-plan/${payload.child_id}/checkin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      joy_score: payload.joy_score,
      parent_notes: payload.parent_notes,
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to save joy score and parent notes');
  }
}
