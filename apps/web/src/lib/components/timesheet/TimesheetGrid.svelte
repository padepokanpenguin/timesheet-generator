<script lang="ts">
  import type { DayRow, TemplateSpec, StoryEntry } from '@timesheet/api-client';
  import { formatDateDisplay, getDayName, formatInformationActivity } from '$lib/utils/formatters';
  import ActivityBlockItem from './ActivityBlockItem.svelte';

  interface Props {
    rows: DayRow[];
    template: TemplateSpec;
    excelPreviewMode?: boolean;
    rawStringMode?: boolean;
    onOpenStoryProgress?: (storyKey: string) => void;
    onUpdateStoryEpic?: (date: string, storyKey: string, val: string) => void;
    onUpdateActivity?: (date: string, storyKey: string, index: number, val: string) => void;
    onAddActivity?: (date: string, storyKey: string, val: string) => void;
    onRemoveActivity?: (date: string, storyKey: string, index: number) => void;
    onUpdateCustomHours?: (date: string, hours: { time_in?: string; time_out?: string; working_hours?: number }) => void;
    onRemoveLeave?: (date: string) => void;
    onAddLeaveClick?: (date: string) => void;
  }

  let {
    rows,
    template,
    excelPreviewMode = false,
    rawStringMode = false,
    onOpenStoryProgress = () => {},
    onUpdateStoryEpic = () => {},
    onUpdateActivity = () => {},
    onAddActivity = () => {},
    onRemoveActivity = () => {},
    onUpdateCustomHours = () => {},
    onRemoveLeave = () => {},
    onAddLeaveClick = () => {}
  }: Props = $props();

  let lang = $derived(template.language || 'id');

  function calculateAutoHours(timeIn?: string | null, timeOut?: string | null): number {
    if (!timeIn || !timeOut) return 8.0;
    const [hIn, mIn] = timeIn.split(':').map(Number);
    const [hOut, mOut] = timeOut.split(':').map(Number);
    if (isNaN(hIn) || isNaN(mIn) || isNaN(hOut) || isNaN(mOut)) return 8.0;
    const minutes = (hOut * 60 + mOut) - (hIn * 60 + mIn) - (template.break_minutes || 60);
    return Math.max(0, Math.round((minutes / 60) * 100) / 100);
  }
</script>

<div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xs {excelPreviewMode ? 'font-excel' : ''}">
  <div class="overflow-x-auto">
    <table class="w-full border-collapse text-left text-xs">
      <!-- Excel / Table Header -->
      <thead>
        <tr class="{excelPreviewMode ? 'bg-excel-header text-white' : 'bg-slate-900 text-slate-100'} text-center font-medium">
          <th class="w-14 border-r border-slate-700 py-2.5 px-2 font-mono">Id</th>
          <th class="w-28 border-r border-slate-700 py-2.5 px-2 font-mono">Date</th>
          <th class="w-24 border-r border-slate-700 py-2.5 px-2 font-mono">Time In</th>
          <th class="w-24 border-r border-slate-700 py-2.5 px-2 font-mono">Time Out</th>
          <th class="w-24 border-r border-slate-700 py-2.5 px-2 font-mono">Working Hour</th>
          <th class="min-w-[480px] py-2.5 px-4 text-left">Information Activity</th>
        </tr>
      </thead>

      <tbody class="divide-y divide-slate-200">
        {#each rows as row, index}
          {@const isWeekend = row.kind === 'weekend'}
          {@const isHoliday = row.kind === 'holiday'}
          {@const isLeave = row.kind === 'leave'}
          {@const isWork = row.kind === 'work'}
          {@const hasBlocker = (row.blockers && row.blockers.length > 0) || row.stories.some((s: StoryEntry) => !s.epic)}
          {@const hasWarning = (row.warnings && row.warnings.length > 0) || (isWork && row.stories.length === 0)}

          <tr
            class="transition-colors {isLeave || isWeekend || isHoliday
              ? 'bg-excel-redSurface/60 hover:bg-excel-redSurface/80'
              : hasBlocker
              ? 'bg-red-50/50 hover:bg-red-50/70'
              : hasWarning
              ? 'bg-amber-50/30 hover:bg-amber-50/60'
              : 'hover:bg-slate-50/80'} {hasBlocker ? 'border-l-4 border-l-red-600' : hasWarning && isWork ? 'border-l-4 border-l-amber-500' : ''}"
          >
            <!-- Col A: Id -->
            <td class="border-r border-slate-200 py-2 px-2 text-center font-mono text-slate-500">
              {index + 1}
            </td>

            <!-- Col B: Date -->
            <td class="border-r border-slate-200 py-2 px-2 text-center font-mono text-slate-700">
              <div class="flex items-center justify-center gap-1.5">
                <span class="rounded bg-slate-100 px-1 text-[10px] font-medium {isWeekend ? 'text-red-600' : 'text-slate-500'}">
                  {getDayName(row.date, lang)}
                </span>
                <span>{formatDateDisplay(row.date, lang)}</span>
              </div>
            </td>

            <!-- Col C..F: Leave State (Colspan 4) -->
            {#if isLeave}
              <td colspan="4" class="py-2.5 px-4 text-center">
                <div class="flex items-center justify-center gap-3 font-bold tracking-widest text-excel-redText">
                  <span>{lang === 'en' ? 'LEAVE' : 'CUTI'}</span>
                  <button
                    type="button"
                    onclick={() => onRemoveLeave(row.date)}
                    class="rounded bg-white/70 px-2 py-0.5 text-[11px] font-normal text-red-700 shadow-2xs hover:bg-white hover:text-red-900"
                    title="Batalkan cuti tanggal ini"
                  >
                    ✕ Hapus Cuti
                  </button>
                </div>
              </td>
            {:else if isWeekend || isHoliday}
              <!-- Weekend or Holiday -->
              <td colspan="4" class="py-2 px-4 text-center">
                <span class="text-xs font-semibold tracking-wide text-excel-redText">
                  {isWeekend ? (lang === 'en' ? 'Weekend' : 'Akhir Pekan') : (lang === 'en' ? 'Public Holiday' : 'Libur Nasional')}
                </span>
              </td>
            {:else}
              <!-- Workday Normal -->
              <!-- Col C: Time In -->
              <td class="border-r border-slate-200 py-2 px-1 text-center font-mono">
                <input
                  type="text"
                  value={row.time_in || template.work_start}
                  onchange={(e) => {
                    const val = e.currentTarget.value;
                    const calculated = calculateAutoHours(val, row.time_out || template.work_end);
                    onUpdateCustomHours(row.date, { time_in: val, working_hours: calculated });
                  }}
                  class="w-16 rounded border border-transparent py-0.5 text-center font-mono text-xs text-slate-800 hover:border-slate-300 focus:border-primary-500 focus:bg-white focus:outline-hidden"
                />
              </td>

              <!-- Col D: Time Out -->
              <td class="border-r border-slate-200 py-2 px-1 text-center font-mono">
                <input
                  type="text"
                  value={row.time_out || template.work_end}
                  onchange={(e) => {
                    const val = e.currentTarget.value;
                    const calculated = calculateAutoHours(row.time_in || template.work_start, val);
                    onUpdateCustomHours(row.date, { time_out: val, working_hours: calculated });
                  }}
                  class="w-16 rounded border border-transparent py-0.5 text-center font-mono text-xs text-slate-800 hover:border-slate-300 focus:border-primary-500 focus:bg-white focus:outline-hidden"
                />
              </td>

              <!-- Col E: Working Hour -->
              <td class="border-r border-slate-200 py-2 px-1 text-center font-mono">
                <input
                  type="number"
                  step="0.5"
                  value={row.working_hours ?? calculateAutoHours(row.time_in, row.time_out)}
                  onchange={(e) => {
                    const val = parseFloat(e.currentTarget.value) || 0;
                    onUpdateCustomHours(row.date, { working_hours: val });
                  }}
                  class="w-14 rounded border border-transparent py-0.5 text-center font-mono text-xs text-slate-800 hover:border-slate-300 focus:border-primary-500 focus:bg-white focus:outline-hidden"
                />
              </td>

              <!-- Col F: Information Activity -->
              <td class="py-2.5 px-4">
                {#if rawStringMode}
                  <!-- Raw Excel String View Mode -->
                  <div class="font-mono text-xs text-slate-900 whitespace-pre-wrap">
                    {formatInformationActivity(row.stories, row.free_text) || '(Kosong)'}
                  </div>
                {:else}
                  <!-- Structured Interactive View Mode -->
                  <div class="space-y-2">
                    {#if row.stories.length === 0}
                      <div class="flex items-center justify-between rounded border border-amber-200 bg-amber-50/60 p-2 text-xs text-amber-900">
                        <div class="flex items-center gap-1.5">
                          <span>⚠</span>
                          <span class="font-medium">Perlu dicek: Tidak ada aktivitas tiket Jira pada hari kerja ini.</span>
                        </div>
                        <div class="flex gap-2">
                          <button
                            type="button"
                            onclick={() => onAddLeaveClick(row.date)}
                            class="rounded bg-white px-2 py-0.5 text-[11px] font-semibold text-red-700 shadow-2xs hover:bg-red-50"
                          >
                            + Tandai Cuti
                          </button>
                        </div>
                      </div>
                    {/if}

                    {#each row.stories as story}
                      <ActivityBlockItem
                        {story}
                        onOpenProgress={() => onOpenStoryProgress(story.key)}
                        onUpdateEpic={(val: string) => onUpdateStoryEpic(row.date, story.key, val)}
                        onUpdateActivity={(actIdx: number, val: string) => onUpdateActivity(row.date, story.key, actIdx, val)}
                        onAddActivity={(val: string) => onAddActivity(row.date, story.key, val)}
                        onRemoveActivity={(actIdx: number) => onRemoveActivity(row.date, story.key, actIdx)}
                      />
                    {/each}

                    {#if row.free_text}
                      <div class="flex items-center gap-2 rounded bg-slate-100 px-2 py-1 text-xs text-slate-700">
                        <span class="font-semibold text-slate-500">[Non-Tiket]:</span>
                        <span>{row.free_text}</span>
                      </div>
                    {/if}
                  </div>
                {/if}
              </td>
            {/if}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>
