export type Intent = 'scripture_qa' | 'theology' | 'image_gen' | 'contradiction' | 'general_chat' | 'refuse';
export type Denomination = 'catholic' | 'protestant' | 'orthodox' | 'unknown';
export type Tradition = 'auto' | 'catholic' | 'protestant' | 'orthodox';

export type ChatRequest = { session_id: string; message: string };

export type ChatResponse = {
  session_id: string;
  response: string;
  image_b64: string | null;
  image_mime_type?: string;
  intent: Intent;
  denomination: Denomination;
  toxicity_ok: boolean;
  cross_references?: CrossReference[];
  reading_plan?: { current: string; next: string };
  alternatives?: { label: string; prompt: string }[];
  citations?: Citation[];
};

export type Citation = { reference: string; translation: string; verified: boolean; verse_text?: string };
export type CrossReference = { reference: string; translation: string; gloss: string; verified: boolean };
export type HistoryResponse = { session_id: string; messages: { role: 'user' | 'assistant'; content: string }[] };
export type Health = { status: 'ok' | 'degraded' | 'down' };

export type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  time: string;
  meta?: Partial<ChatResponse>;
};
