import { v4 as uuid } from 'uuid';
const KEY = 'lectio:session_id';

export function getSessionId(): string {
  if (typeof window === 'undefined') return '';
  let id = localStorage.getItem(KEY);
  if (!id) { id = uuid(); localStorage.setItem(KEY, id); }
  return id;
}

export function rotateSessionId(): string {
  const id = uuid();
  if (typeof window !== 'undefined') localStorage.setItem(KEY, id);
  return id;
}
