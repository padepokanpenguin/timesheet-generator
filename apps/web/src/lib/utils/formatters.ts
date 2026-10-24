import type { StoryEntry } from '@timesheet/api-client';

const MONTH_NAMES_ID = [
  'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
];

const MONTH_NAMES_EN = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

const DAY_NAMES_ID = ['Min', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab'];
const DAY_NAMES_EN = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

export function getMonthName(month: number, lang: 'id' | 'en' = 'id'): string {
  const list = lang === 'en' ? MONTH_NAMES_EN : MONTH_NAMES_ID;
  return list[month - 1] ?? '';
}

export function formatDateDisplay(dateStr: string, lang: 'id' | 'en' = 'id'): string {
  if (!dateStr) return '';
  const [y, m, d] = dateStr.split('-').map(Number);
  if (!y || !m || !d) return dateStr;
  const monthShort = getMonthName(m, lang).slice(0, 3);
  return `${d} ${monthShort} ${y}`;
}

export function getDayName(dateStr: string, lang: 'id' | 'en' = 'id'): string {
  if (!dateStr) return '';
  const d = new Date(dateStr + 'T00:00:00');
  const dayIndex = d.getDay();
  return lang === 'en' ? DAY_NAMES_EN[dayIndex] : DAY_NAMES_ID[dayIndex];
}

export function formatPeriod(year: number, month: number, lang: 'id' | 'en' = 'id'): string {
  const lastDay = new Date(year, month, 0).getDate();
  const monthName = getMonthName(month, lang);
  return `1 ${monthName} ${year} - ${lastDay} ${monthName} ${year}`;
}

export function formatInformationActivity(stories: StoryEntry[], freeText?: string | null): string {
  const blocks: string[] = [];
  for (const s of stories) {
    let head = s.title ? `${s.key}: ${s.title}` : s.key;
    if (s.epic) {
      head = `[${s.epic}] ${head}`;
    }
    if (s.percent !== null && s.percent !== undefined) {
      head += ` (${s.percent}%)`;
    }
    const act = (s.activities || []).map((a) => ` - ${a}`).join('');
    blocks.push(head + act);
  }
  if (freeText && freeText.trim()) {
    blocks.push(freeText.trim());
  }
  return blocks.join('\n');
}
