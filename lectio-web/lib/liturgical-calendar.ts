export type LiturgicalHint = { label: string; daysUntil: number | null };

function easterDate(year: number): Date {
  const a = year % 19, b = Math.floor(year / 100), c = year % 100;
  const d = Math.floor(b / 4), e = b % 4, f = Math.floor((b + 8) / 25);
  const g = Math.floor((b - f + 1) / 3), h = (19 * a + b - d - g + 15) % 30;
  const i = Math.floor(c / 4), k = c % 4;
  const l = (32 + 2 * e + 2 * i - h - k) % 7;
  const m = Math.floor((a + 11 * h + 22 * l) / 451);
  const month = Math.floor((h + l - 7 * m + 114) / 31);
  const day = ((h + l - 7 * m + 114) % 31) + 1;
  return new Date(year, month - 1, day);
}

export function getLiturgicalHint(now = new Date()): LiturgicalHint {
  const year = now.getFullYear();
  const easter = easterDate(year);
  const holyWeekStart = new Date(easter); holyWeekStart.setDate(easter.getDate() - 7);
  const christmas = new Date(year, 11, 25);
  const advent = new Date(year, 11, 25); advent.setDate(25 - ((christmas.getDay() + 28) % 7));
  const pentecost = new Date(easter); pentecost.setDate(easter.getDate() + 49);
  const lentStart = new Date(easter); lentStart.setDate(easter.getDate() - 46);

  const feasts = [
    { name: 'Holy Week', date: holyWeekStart },
    { name: 'Easter', date: easter },
    { name: 'Pentecost', date: pentecost },
    { name: 'Advent', date: advent },
    { name: 'Christmas', date: christmas },
    { name: 'Lent', date: lentStart },
  ];

  const nowMs = now.getTime();
  const upcoming = feasts
    .map(f => ({ ...f, diff: Math.ceil((f.date.getTime() - nowMs) / 86400000) }))
    .filter(f => f.diff > 0 && f.diff <= 40)
    .sort((a, b) => a.diff - b.diff);

  if (upcoming.length === 0) return { label: 'ordinary time', daysUntil: null };
  const next = upcoming[0];
  return { label: `${next.diff} day${next.diff === 1 ? '' : 's'} before ${next.name}`, daysUntil: next.diff };
}
