<script lang="ts">
  import type { TimesheetDraft, TemplateSpec, StoryEntry } from '@timesheet/api-client';
  import { formatDateDisplay, getDayName } from '$lib/utils/formatters';
  import { validateManualPercentages } from '$lib/utils/qualityChecker';

  interface Props {
    storyKey: string | null;
    draft: TimesheetDraft;
    template: TemplateSpec;
    manualPercentages?: Record<string, Record<string, number>>;
    manualEstimates?: Record<string, number>;
    manualEpics?: Record<string, string>;
    onClose?: () => void;
    onUpdateManualPercentages?: (map: Record<string, number>) => void;
    onUpdateEstimate?: (val: number) => void;
    onUpdateEpic?: (val: string) => void;
    onReseed?: () => void;
  }

  let {
    storyKey,
    draft,
    template,
    manualPercentages = {},
    manualEstimates = {},
    manualEpics = {},
    onClose = () => {},
    onUpdateManualPercentages = () => {},
    onUpdateEstimate = () => {},
    onUpdateEpic = () => {},
    onReseed = () => {}
  }: Props = $props();

  let activeTab = $state<'random' | 'manual'>('random');

  // Find all active days and story occurrences for this storyKey
  let activeDays = $derived.by(() => {
    if (!storyKey) return [];
    const days: { date: string; percent: number | null; epic: string | null; title: string; activities: string[] }[] = [];
    for (const r of draft.rows) {
      if (r.kind !== 'work') continue;
      const s = r.stories.find((item: StoryEntry) => item.key === storyKey);
      if (s) {
        days.push({
          date: r.date,
          percent: s.percent ?? null,
          epic: s.epic,
          title: s.title,
          activities: s.activities
        });
      }
    }
    return days;
  });

  let storyTitle = $derived(activeDays[0]?.title || storyKey || '');
  let currentEpic = $derived(
    storyKey ? manualEpics[storyKey] || activeDays[0]?.epic || '' : ''
  );
  let currentEstimate = $derived(
    storyKey && manualEstimates[storyKey] !== undefined ? manualEstimates[storyKey] : 4.0
  );

  let storyState = $derived(
    storyKey && draft.story_end_state ? draft.story_end_state[storyKey] : null
  );
  let startPercent = $derived(storyState ? storyState.previous_percent : 0);

  // Local state for manual percentage inputs
  let manualInputs = $state<Record<string, number>>({});

  $effect(() => {
    if (storyKey) {
      const existing = manualPercentages[storyKey] || {};
      const initial: Record<string, number> = {};
      for (const d of activeDays) {
        initial[d.date] = existing[d.date] ?? d.percent ?? 0;
      }
      manualInputs = initial;
    }
  });

  let targetEndPercent = $derived.by(() => {
    const lastDay = activeDays[activeDays.length - 1];
    return lastDay ? (lastDay.percent ?? 100) : 100;
  });

  let manualValidationError = $derived.by(() => {
    if (activeTab !== 'manual') return null;
    const dateList = activeDays.map((d) => d.date);
    return validateManualPercentages(dateList, manualInputs, startPercent, targetEndPercent);
  });

  function handleSaveManual() {
    if (storyKey && !manualValidationError) {
      onUpdateManualPercentages(manualInputs);
    }
  }
</script>

{#if storyKey}
  <!-- Backdrop -->
  <button
    type="button"
    class="fixed inset-0 z-40 bg-slate-900/30 backdrop-blur-2xs transition-opacity"
    onclick={() => onClose()}
    aria-label="Tutup drawer"
  ></button>

  <!-- Slide-over drawer -->
  <div
    class="fixed inset-y-0 right-0 z-50 flex w-full max-w-[480px] flex-col border-l border-slate-200 bg-white shadow-2xl"
    role="dialog"
    aria-modal="true"
    aria-labelledby="drawer-title"
  >
    <!-- Header -->
    <div class="flex items-start justify-between border-b border-slate-200 px-6 py-4">
      <div>
        <div class="flex items-center gap-2">
          <span class="rounded bg-primary-100 px-2 py-0.5 font-mono text-xs font-semibold text-primary-800">
            {storyKey}
          </span>
          {#if currentEpic}
            <span class="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-700">
              [{currentEpic}]
            </span>
          {:else}
            <span class="rounded bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-800">
              [Epic Belum Diisi]
            </span>
          {/if}
        </div>
        <h3 id="drawer-title" class="mt-1.5 text-base font-semibold text-slate-900">
          {storyTitle}
        </h3>
      </div>
      <button
        type="button"
        onclick={() => onClose()}
        class="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
        title="Tutup (Escape)"
      >
        ✕
      </button>
    </div>

    <!-- Content scrollable -->
    <div class="flex-1 space-y-6 overflow-y-auto p-6">
      <!-- Story Meta & Estimates -->
      <div class="rounded-lg border border-slate-200 bg-slate-50 p-4">
        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-500">Estimasi & Progres Kumulatif</h4>
        <div class="mt-3 grid grid-cols-2 gap-3 text-xs">
          <div>
            <label class="block font-medium text-slate-700" for="drawer-estimate-input">Estimasi (Mandays):</label>
            <div class="mt-1 flex items-center gap-1.5">
              <input
                id="drawer-estimate-input"
                type="number"
                step="0.5"
                min="0.5"
                value={currentEstimate}
                onchange={(e) => onUpdateEstimate(parseFloat(e.currentTarget.value) || 1.0)}
                class="w-20 rounded border border-slate-300 bg-white px-2 py-1 font-mono text-xs text-slate-900 focus:border-primary-500 focus:outline-hidden"
              />
              <span class="text-slate-500">md ({Math.round(currentEstimate * 8)} jam)</span>
            </div>
          </div>
          <div>
            <span class="block font-medium text-slate-700">Hari Aktif Bulan Ini:</span>
            <span class="mt-1 block font-mono text-xs font-semibold text-slate-900">
              {activeDays.length} hari ({activeDays.length * 8} jam)
            </span>
          </div>
        </div>

        <div class="mt-3 grid grid-cols-2 gap-3 border-t border-slate-200 pt-3 text-xs">
          <div>
            <span class="block text-slate-500">Progres Awal Bulan Ini:</span>
            <span class="font-mono font-semibold text-slate-800">{startPercent}%</span>
            {#if startPercent > 0}
              <span class="block text-[11px] text-primary-600">↳ Lanjutan bulan lalu</span>
            {/if}
          </div>
          <div>
            <span class="block text-slate-500">Target Akhir Bulan:</span>
            <span class="font-mono font-semibold text-primary-700">{targetEndPercent}%</span>
          </div>
        </div>
      </div>

      <!-- Mode Segmentasi Harian -->
      <div>
        <div class="flex border-b border-slate-200 text-xs font-medium">
          <button
            type="button"
            onclick={() => (activeTab = 'random')}
            class="border-b-2 px-4 py-2 {activeTab === 'random' ? 'border-primary-600 text-primary-700' : 'border-transparent text-slate-500 hover:text-slate-800'}"
          >
            Tab A: Acak Terkunci (Default)
          </button>
          <button
            type="button"
            onclick={() => (activeTab = 'manual')}
            class="border-b-2 px-4 py-2 {activeTab === 'manual' ? 'border-primary-600 text-primary-700' : 'border-transparent text-slate-500 hover:text-slate-800'}"
          >
            Tab B: Input Manual per Hari
          </button>
        </div>

        <!-- Tab A: Random Locked -->
        {#if activeTab === 'random'}
          <div class="mt-4 space-y-4 text-xs">
            <div class="flex items-center justify-between rounded-md bg-blue-50 p-3 text-blue-900">
              <div>
                <p class="font-semibold">Distribusi Acak Terkunci Aktif</p>
                <p class="mt-0.5 text-[11px] text-blue-700">
                  Persentase otomatis dibagi ke seluruh hari aktif (kelipatan 5%, porsi min. 5%).
                </p>
              </div>
              <button
                type="button"
                onclick={() => onReseed()}
                class="rounded bg-primary-600 px-2.5 py-1.5 font-medium text-white shadow-xs hover:bg-primary-700"
              >
                🎲 Acak Ulang
              </button>
            </div>

            <div class="divide-y divide-slate-100 rounded-lg border border-slate-200 bg-white">
              {#each activeDays as d}
                <div class="flex items-center justify-between p-2.5 text-xs">
                  <div class="flex items-center gap-2">
                    <span class="w-12 font-medium text-slate-600">{getDayName(d.date)},</span>
                    <span class="font-mono text-slate-800">{formatDateDisplay(d.date)}</span>
                  </div>
                  <span class="rounded bg-slate-100 px-2 py-0.5 font-mono font-semibold text-slate-900">
                    {d.percent ?? 0}%
                  </span>
                </div>
              {/each}
            </div>
          </div>
        {/if}

        <!-- Tab B: Manual Daily Input -->
        {#if activeTab === 'manual'}
          <div class="mt-4 space-y-4 text-xs">
            <p class="text-slate-600">
              Masukkan nilai persentase kumulatif untuk masing-masing hari aktif. Nilai harus naik setiap hari dan hari terakhir harus tepat <strong class="text-primary-700">{targetEndPercent}%</strong>.
            </p>

            {#if manualValidationError}
              <div class="rounded border border-red-200 bg-red-50 p-2.5 text-red-800">
                ⚠ {manualValidationError}
              </div>
            {/if}

            <div class="divide-y divide-slate-100 rounded-lg border border-slate-200 bg-white">
              {#each activeDays as d}
                <div class="flex items-center justify-between gap-3 p-2.5">
                  <div class="flex items-center gap-2">
                    <span class="w-10 font-medium text-slate-500">{getDayName(d.date)}</span>
                    <span class="font-mono text-slate-700">{formatDateDisplay(d.date)}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <input
                      type="range"
                      min={startPercent}
                      max="100"
                      step={template.formula.rounding_step || 5}
                      bind:value={manualInputs[d.date]}
                      class="h-1.5 w-24 accent-primary-600"
                    />
                    <div class="flex items-center">
                      <input
                        type="number"
                        min="0"
                        max="100"
                        step={template.formula.rounding_step || 5}
                        bind:value={manualInputs[d.date]}
                        class="w-16 rounded border border-slate-300 px-2 py-1 text-right font-mono text-xs text-slate-900 focus:border-primary-500 focus:outline-hidden"
                      />
                      <span class="ml-1 text-slate-400">%</span>
                    </div>
                  </div>
                </div>
              {/each}
            </div>

            <div class="flex justify-end pt-2">
              <button
                type="button"
                disabled={!!manualValidationError}
                onclick={handleSaveManual}
                class="rounded bg-primary-600 px-4 py-2 font-medium text-white shadow-xs hover:bg-primary-700 disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                Terapkan Persentase Manual
              </button>
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}
