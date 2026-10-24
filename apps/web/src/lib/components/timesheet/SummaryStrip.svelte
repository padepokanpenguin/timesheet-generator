<script lang="ts">
  interface SummaryData {
    workdaysCount: number;
    totalHours: number;
    activeStoriesCount: number;
    totalSubtasks: number;
    blockersCount: number;
    warningsCount: number;
    leaveCount: number;
    blockerMessages: string[];
    warningMessages: string[];
  }

  interface Props {
    summary: SummaryData;
    onSelectFilter?: (filter: 'all' | 'blockers' | 'warnings' | 'leaves') => void;
  }

  let {
    summary,
    onSelectFilter = () => {}
  }: Props = $props();

  let showBlockerList = $state(false);
  let showWarningList = $state(false);
</script>

<div class="flex flex-col gap-2 rounded-lg border border-slate-200 bg-white p-3 shadow-xs">
  <div class="flex flex-wrap items-center gap-2 text-xs">
    <span class="inline-flex items-center gap-1.5 rounded-md bg-slate-100 px-2.5 py-1 font-medium text-slate-700">
      <span class="h-2 w-2 rounded-full bg-slate-400"></span>
      Hari Kerja: <strong class="font-semibold text-slate-900">{summary.workdaysCount} hari</strong>
      <span class="text-slate-400">({summary.totalHours} jam)</span>
    </span>

    <span class="inline-flex items-center gap-1.5 rounded-md bg-slate-100 px-2.5 py-1 font-medium text-slate-700">
      <span class="h-2 w-2 rounded-full bg-primary-500"></span>
      Story Aktif: <strong class="font-semibold text-slate-900">{summary.activeStoriesCount} Story</strong>
      <span class="text-slate-400">({summary.totalSubtasks} sub-task)</span>
    </span>

    <button
      type="button"
      onclick={() => {
        showBlockerList = !showBlockerList;
        if (showBlockerList) showWarningList = false;
        onSelectFilter(showBlockerList ? 'blockers' : 'all');
      }}
      class="inline-flex cursor-pointer items-center gap-1.5 rounded-md border px-2.5 py-1 font-medium transition {summary.blockersCount > 0 ? 'border-red-200 bg-red-50 text-red-700 hover:bg-red-100' : 'border-slate-200 bg-slate-50 text-slate-600'}"
    >
      <span class="h-2 w-2 rounded-full {summary.blockersCount > 0 ? 'bg-red-600' : 'bg-slate-300'}"></span>
      Blocker: <strong class="font-semibold">{summary.blockersCount}</strong>
      {#if summary.blockersCount > 0}
        <span class="text-[10px] font-normal underline">(perlu tindakan)</span>
      {/if}
    </button>

    <button
      type="button"
      onclick={() => {
        showWarningList = !showWarningList;
        if (showWarningList) showBlockerList = false;
        onSelectFilter(showWarningList ? 'warnings' : 'all');
      }}
      class="inline-flex cursor-pointer items-center gap-1.5 rounded-md border px-2.5 py-1 font-medium transition {summary.warningsCount > 0 ? 'border-amber-200 bg-amber-50 text-amber-800 hover:bg-amber-100' : 'border-slate-200 bg-slate-50 text-slate-600'}"
    >
      <span class="h-2 w-2 rounded-full {summary.warningsCount > 0 ? 'bg-amber-500' : 'bg-slate-300'}"></span>
      Peringatan: <strong class="font-semibold">{summary.warningsCount}</strong>
    </button>

    {#if summary.leaveCount > 0}
      <button
        type="button"
        onclick={() => onSelectFilter('leaves')}
        class="inline-flex cursor-pointer items-center gap-1.5 rounded-md bg-excel-redSurface px-2.5 py-1 font-medium text-excel-redText hover:bg-red-200"
      >
        <span class="h-2 w-2 rounded-full bg-excel-redBorder"></span>
        Cuti: <strong class="font-semibold">{summary.leaveCount} hari</strong>
      </button>
    {/if}
  </div>

  {#if showBlockerList && summary.blockerMessages.length > 0}
    <div class="mt-2 rounded border border-red-200 bg-red-50/70 p-2.5 text-xs text-red-900">
      <div class="mb-1.5 flex items-center justify-between font-semibold">
        <span>Masalah Kritis (Blocker) — Wajib diselesaikan sebelum generate .xlsx:</span>
        <button
          type="button"
          onclick={() => (showBlockerList = false)}
          class="text-red-600 hover:text-red-800"
        >
          Tutup ✕
        </button>
      </div>
      <ul class="list-disc space-y-1 pl-4">
        {#each summary.blockerMessages as msg}
          <li>{msg}</li>
        {/each}
      </ul>
    </div>
  {/if}

  {#if showWarningList && summary.warningMessages.length > 0}
    <div class="mt-2 rounded border border-amber-200 bg-amber-50/70 p-2.5 text-xs text-amber-900">
      <div class="mb-1.5 flex items-center justify-between font-semibold">
        <span>Daftar Peringatan Kualitas:</span>
        <button
          type="button"
          onclick={() => (showWarningList = false)}
          class="text-amber-700 hover:text-amber-900"
        >
          Tutup ✕
        </button>
      </div>
      <ul class="list-disc space-y-1 pl-4">
        {#each summary.warningMessages as msg}
          <li>{msg}</li>
        {/each}
      </ul>
    </div>
  {/if}
</div>
