import type { TimesheetDraft } from '@timesheet/api-client';

export const KNOWN_TYPOS: Record<string, string> = {
  '100$': 'seharusnya (100%)',
  ednpoint: 'endpoint',
  pacakge: 'package',
  dependecy: 'dependency',
  integation: 'integration',
  implemenation: 'implementation'
};

export function detectTyposInText(text: string): { word: string; suggestion: string }[] {
  if (!text) return [];
  const lower = text.toLowerCase();
  const results: { word: string; suggestion: string }[] = [];
  for (const [typo, suggestion] of Object.entries(KNOWN_TYPOS)) {
    if (lower.includes(typo)) {
      results.push({ word: typo, suggestion });
    }
  }
  return results;
}

export function validateManualPercentages(
  days: string[],
  values: Record<string, number>,
  startPercent: number,
  targetEnd: number | null
): string | null {
  if (days.length === 0) return null;
  let prev = startPercent;
  for (let i = 0; i < days.length; i++) {
    const day = days[i];
    const val = values[day];
    if (val === undefined || isNaN(val)) {
      return `Nilai persentase pada tanggal ${day} belum terisi`;
    }
    if (val < 0 || val > 100) {
      return `Persentase pada ${day} harus berada di antara 0% dan 100%`;
    }
    if (val < prev) {
      return `Persentase pada ${day} (${val}%) tidak boleh lebih kecil dari hari sebelumnya (${prev}%)`;
    }
    prev = val;
  }
  if (targetEnd !== null && prev !== targetEnd) {
    return `Persentase hari terakhir (${prev}%) harus tepat sama dengan target progres (${targetEnd}%)`;
  }
  return null;
}

export function computeTimesheetSummary(draft: TimesheetDraft | null) {
  if (!draft) {
    return {
      workdaysCount: 0,
      totalHours: 0,
      activeStoriesCount: 0,
      totalSubtasks: 0,
      blockersCount: 0,
      warningsCount: 0,
      leaveCount: 0,
      blockerMessages: [] as string[],
      warningMessages: [] as string[]
    };
  }

  const storiesSet = new Set<string>();
  let totalSubtasks = 0;
  let workdaysCount = 0;
  let totalHours = 0;
  let leaveCount = 0;

  const blockerMessages: string[] = [...(draft.blockers || [])];
  const warningMessages: string[] = [...(draft.warnings || [])];

  for (const row of draft.rows) {
    if (row.kind === 'work') {
      workdaysCount++;
      if (row.working_hours) {
        totalHours += row.working_hours;
      }
      for (const s of row.stories) {
        storiesSet.add(s.key);
        totalSubtasks += (s.activities || []).length;
        if (!s.epic) {
          const msg = `${s.key}: Story tanpa Epic ([Label] wajib diisi)`;
          if (!blockerMessages.includes(msg)) blockerMessages.push(msg);
        }
      }
    } else if (row.kind === 'leave') {
      leaveCount++;
    }

    if (row.blockers) {
      for (const b of row.blockers) {
        if (!blockerMessages.includes(b)) blockerMessages.push(b);
      }
    }
    if (row.warnings) {
      for (const w of row.warnings) {
        if (!warningMessages.includes(w)) warningMessages.push(w);
      }
    }
  }

  return {
    workdaysCount,
    totalHours: Math.round(totalHours * 100) / 100,
    activeStoriesCount: storiesSet.size,
    totalSubtasks,
    blockersCount: blockerMessages.length,
    warningsCount: warningMessages.length,
    leaveCount,
    blockerMessages,
    warningMessages
  };
}
