<script lang="ts">
  import { onMount } from 'svelte';
  import {
    generateTimesheet,
    listTemplates,
    previewTimesheet,
    getSignatureStatus,
    type DayRow,
    type TemplateSpec,
    type TimesheetDraft,
    type SignatureStatus
  } from '@timesheet/api-client';
  import { formatPeriod } from '$lib/utils/formatters';
  import { computeTimesheetSummary } from '$lib/utils/qualityChecker';
  import SummaryStrip from '$lib/components/timesheet/SummaryStrip.svelte';
  import TimesheetGrid from '$lib/components/timesheet/TimesheetGrid.svelte';
  import StoryProgressDrawer from '$lib/components/timesheet/StoryProgressDrawer.svelte';
  import LeaveAndManualEntryModal from '$lib/components/modals/LeaveAndManualEntryModal.svelte';
  import SignatureFooterPreview from '$lib/components/signature/SignatureFooterPreview.svelte';

  const today = new Date();
  let year = $state(today.getFullYear());
  let month = $state(today.getMonth() + 1);
  let templateId = $state('default-id');
  let templates = $state<TemplateSpec[]>([]);
  let draft = $state<TimesheetDraft | null>(null);

  let seed = $state(0);
  let showAllDays = $state(true);
  let rawStringMode = $state(false);
  let excelPreviewMode = $state(false);

  let loading = $state(false);
  let loadingStep = $state('');
  let error = $state('');
  let notice = $state('');

  // Modals & Drawers state
  let selectedStoryKey = $state<string | null>(null);
  let isLeaveModalOpen = $state(false);
  let showExportConfirmModal = $state(false);

  // Manual overrides state
  let manualPercentages = $state<Record<string, Record<string, number>>>({});
  let manualEstimates = $state<Record<string, number>>({});
  let manualEpics = $state<Record<string, string>>({});
  let nonTicketEntries = $state<Record<string, string>>({});
  let customHours = $state<Record<string, { time_in?: string; time_out?: string; working_hours?: number }>>({});
  let leaveDates = $state<string[]>([]);

  // Signature status
  let sigStatus = $state<SignatureStatus>({ employee: false, team_lead: false });

  let selectedTemplate = $derived(
    templates.find((t) => t.id === templateId) || templates[0] || {
      id: 'default-id',
      name: 'Default (Bahasa Indonesia)',
      language: 'id',
      company_name: 'PT. PASTI MAKMUR ABADI',
      client: 'Siloam Hospital',
      department: 'IT',
      title: 'Fullstack Developer',
      employee_name: 'Aria Nur Jamal',
      team_lead_name: 'Kevin Saputra',
      work_start: '08:30',
      work_end: '17:30',
      break_minutes: 60,
      show_all_days: true,
      timezone: 'Asia/Jakarta',
      holiday_country: 'ID',
      extra_holidays: [],
      file_name_pattern: 'TimeSheet_{name}_{year}.xlsx',
      formula: {
        hours_per_manday: 8,
        story_point_to_manday: 1,
        max_progress_before_done: 95,
        rounding_step: 5,
        min_daily_portion: 5,
        segmentation_mode: 'random',
        carry_over_between_months: true
      }
    }
  );

  let summary = $derived(computeTimesheetSummary(draft));

  onMount(async () => {
    try {
      templates = await listTemplates();
      sigStatus = await getSignatureStatus().catch(() => ({ employee: false, team_lead: false }));
      // Tarik preview otomatis saat awal buka
      await fetchDraft();
    } catch (e) {
      error = (e as Error).message;
    }
  });

  async function fetchDraft(reroll = false) {
    loading = true;
    error = '';
    notice = '';
    if (reroll) {
      seed += 1;
    }

    try {
      loadingStep = '1. Mengambil daftar sub-task dan story dari Jira Cloud...';
      await new Promise((r) => setTimeout(r, 200));

      loadingStep = '2. Memuat Epic, changelog WIB, dan menghitung persentase...';

      draft = await previewTimesheet({
        year,
        month,
        template_id: templateId,
        leave_dates: leaveDates,
        manual_percent: manualPercentages,
        reroll_seed: seed,
        show_all_days: showAllDays,
        non_ticket_entries: nonTicketEntries,
        manual_estimates: manualEstimates,
        manual_epics: manualEpics,
        custom_hours: customHours
      });

      // Sinkronkan daftar cuti yang ada di draft
      if (draft) {
        leaveDates = draft.rows.filter((r) => r.kind === 'leave').map((r) => r.date);
      }
      notice = reroll
        ? 'Persentase acak berhasil dihitung ulang!'
        : `Pratinjau timesheet periode ${formatPeriod(year, month, selectedTemplate.language)} berhasil dimuat.`;
    } catch (e) {
      error = (e as Error).message;
    } finally {
      loading = false;
      loadingStep = '';
    }
  }

  function handleAddLeaves(newDates: string[]) {
    const set = new Set([...leaveDates, ...newDates]);
    leaveDates = Array.from(set);
    fetchDraft();
  }

  function handleRemoveLeave(dateStr: string) {
    leaveDates = leaveDates.filter((d) => d !== dateStr);
    fetchDraft();
  }

  function handleAddNonTicket(dateStr: string, text: string) {
    nonTicketEntries[dateStr] = text;
    fetchDraft();
  }

  function handleUpdateEpic(dateStr: string, storyKey: string, val: string) {
    manualEpics[storyKey] = val;
    if (draft) {
      for (const row of draft.rows) {
        for (const s of row.stories) {
          if (s.key === storyKey) {
            s.epic = val;
          }
        }
      }
    }
  }

  function handleUpdateActivity(dateStr: string, storyKey: string, actIdx: number, val: string) {
    if (!draft) return;
    const row = draft.rows.find((r) => r.date === dateStr);
    const story = row?.stories.find((s) => s.key === storyKey);
    if (story && story.activities[actIdx] !== undefined) {
      story.activities[actIdx] = val;
    }
  }

  function handleAddActivity(dateStr: string, storyKey: string, val: string) {
    if (!draft) return;
    const row = draft.rows.find((r) => r.date === dateStr);
    const story = row?.stories.find((s) => s.key === storyKey);
    if (story) {
      story.activities.push(val);
    }
  }

  function handleRemoveActivity(dateStr: string, storyKey: string, actIdx: number) {
    if (!draft) return;
    const row = draft.rows.find((r) => r.date === dateStr);
    const story = row?.stories.find((s) => s.key === storyKey);
    if (story && story.activities[actIdx] !== undefined) {
      story.activities.splice(actIdx, 1);
    }
  }

  function handleUpdateCustomHours(
    dateStr: string,
    hours: { time_in?: string; time_out?: string; working_hours?: number }
  ) {
    customHours[dateStr] = {
      ...(customHours[dateStr] || {}),
      ...hours
    };
    if (draft) {
      const row = draft.rows.find((r) => r.date === dateStr);
      if (row) {
        if (hours.time_in !== undefined) row.time_in = hours.time_in;
        if (hours.time_out !== undefined) row.time_out = hours.time_out;
        if (hours.working_hours !== undefined) row.working_hours = hours.working_hours;
      }
    }
  }

  function handleSaveManualPercentages(map: Record<string, number>) {
    if (selectedStoryKey) {
      manualPercentages[selectedStoryKey] = map;
      selectedStoryKey = null;
      fetchDraft();
    }
  }

  function handleUpdateEstimate(val: number) {
    if (selectedStoryKey) {
      manualEstimates[selectedStoryKey] = val;
      fetchDraft();
    }
  }

  function handleReseedAll() {
    manualPercentages = {};
    fetchDraft(true);
  }

  function handleReseedStory() {
    if (selectedStoryKey) {
      const copy = { ...manualPercentages };
      delete copy[selectedStoryKey];
      manualPercentages = copy;
      fetchDraft(true);
    }
  }

  async function executeDownload() {
    if (!draft) return;
    try {
      notice = 'Menghasilkan berkas .xlsx dengan layout identik template...';
      await generateTimesheet(draft);
      notice = 'Berkas .xlsx berhasil diunduh!';
      showExportConfirmModal = false;
    } catch (e) {
      error = (e as Error).message;
    }
  }

  function handleGenerateClick() {
    if (summary.blockersCount > 0) return;
    if (summary.warningsCount > 0) {
      showExportConfirmModal = true;
    } else {
      executeDownload();
    }
  }
</script>

<div class="space-y-6">
  <!-- 1. Context & Period Bar (Top Controls) -->
  <section class="flex flex-wrap items-end justify-between gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-xs">
    <div class="flex flex-wrap items-end gap-3 text-xs">
      <!-- Template Dropdown -->
      <label class="flex flex-col gap-1 font-medium text-slate-700">
        Template Perusahaan:
        <select
          bind:value={templateId}
          onchange={() => fetchDraft()}
          class="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-900 focus:border-primary-500 focus:outline-hidden"
        >
          {#each templates as t}
            <option value={t.id}>{t.name} ({t.company_name})</option>
          {/each}
        </select>
      </label>

      <!-- Bulan & Tahun -->
      <label class="flex flex-col gap-1 font-medium text-slate-700">
        Bulan:
        <select
          bind:value={month}
          onchange={() => fetchDraft()}
          class="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-900 focus:border-primary-500 focus:outline-hidden"
        >
          <option value={1}>1 - Januari</option>
          <option value={2}>2 - Februari</option>
          <option value={3}>3 - Maret</option>
          <option value={4}>4 - April</option>
          <option value={5}>5 - Mei</option>
          <option value={6}>6 - Juni</option>
          <option value={7}>7 - Juli</option>
          <option value={8}>8 - Agustus</option>
          <option value={9}>9 - September</option>
          <option value={10}>10 - Oktober</option>
          <option value={11}>11 - November</option>
          <option value={12}>12 - Desember</option>
        </select>
      </label>

      <label class="flex flex-col gap-1 font-medium text-slate-700">
        Tahun:
        <input
          type="number"
          bind:value={year}
          onchange={() => fetchDraft()}
          class="w-20 rounded-lg border border-slate-300 bg-white px-3 py-1.5 font-mono text-xs text-slate-900 focus:border-primary-500 focus:outline-hidden"
        />
      </label>

      <!-- Toggle Mode Hari -->
      <div class="flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 p-1">
        <button
          type="button"
          onclick={() => {
            showAllDays = true;
            fetchDraft();
          }}
          class="rounded-md px-2.5 py-1 text-xs font-medium transition {showAllDays ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600 hover:text-slate-900'}"
        >
          Semua Hari (1..31)
        </button>
        <button
          type="button"
          onclick={() => {
            showAllDays = false;
            fetchDraft();
          }}
          class="rounded-md px-2.5 py-1 text-xs font-medium transition {!showAllDays ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600 hover:text-slate-900'}"
        >
          Hanya Hari Kerja
        </button>
      </div>

      <!-- Sync / Refresh Button -->
      <button
        type="button"
        onclick={() => fetchDraft(false)}
        disabled={loading}
        class="inline-flex cursor-pointer items-center gap-1.5 rounded-lg bg-primary-600 px-3.5 py-1.5 font-medium text-white shadow-xs hover:bg-primary-700 disabled:bg-slate-300"
      >
        <span>🔄</span>
        <span>{loading ? 'Menarik Data...' : 'Tarik Data Jira'}</span>
      </button>
    </div>

    <!-- Right Controls: View Toggles -->
    <div class="flex items-center gap-2 text-xs">
      <label class="flex cursor-pointer items-center gap-1.5 text-slate-600 hover:text-slate-900">
        <input type="checkbox" bind:checked={rawStringMode} class="accent-primary-600" />
        <span>Teks Mentah Excel</span>
      </label>
      <label class="flex cursor-pointer items-center gap-1.5 text-slate-600 hover:text-slate-900">
        <input type="checkbox" bind:checked={excelPreviewMode} class="accent-primary-600" />
        <span>Font Arial (Excel)</span>
      </label>
    </div>
  </section>

  <!-- Stepper loading bar saat sync -->
  {#if loading && loadingStep}
    <div class="flex items-center gap-3 rounded-lg border border-blue-200 bg-blue-50 px-4 py-2.5 text-xs text-blue-900">
      <span class="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-primary-600 border-t-transparent"></span>
      <span class="font-medium">{loadingStep}</span>
    </div>
  {/if}

  <!-- Notice and Error Banners -->
  {#if error}
    <div class="flex items-center justify-between rounded-lg border border-red-200 bg-red-50 p-3 text-xs text-red-900">
      <div class="flex items-center gap-2">
        <span>⚠</span>
        <span>{error}</span>
      </div>
      <button type="button" onclick={() => (error = '')} class="text-red-700 hover:text-red-900">✕</button>
    </div>
  {/if}

  {#if notice}
    <div class="flex items-center justify-between rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-900">
      <div class="flex items-center gap-2">
        <span>✓</span>
        <span>{notice}</span>
      </div>
      <button type="button" onclick={() => (notice = '')} class="text-emerald-700 hover:text-emerald-900">✕</button>
    </div>
  {/if}

  <!-- 2. Validation & Summary Strip -->
  {#if draft}
    <SummaryStrip {summary} />
  {/if}

  <!-- 3. Interactive Timesheet Grid -->
  {#if !draft && !loading}
    <div class="flex flex-col items-center justify-center rounded-xl border border-slate-200 bg-white py-16 text-center shadow-xs">
      <span class="text-3xl">📋</span>
      <h3 class="mt-2 text-sm font-semibold text-slate-800">Belum Ada Draf Timesheet</h3>
      <p class="mt-1 max-w-sm text-xs text-slate-500">
        Pilih template dan bulan di atas, lalu klik <strong>Tarik Data Jira</strong> untuk membangun draf otomatis.
      </p>
    </div>
  {:else if draft}
    <div class="space-y-4">
      <div class="flex items-center justify-between text-xs text-slate-500">
        <div>
          <span>Periode: </span>
          <strong class="font-semibold text-slate-800">{formatPeriod(year, month, selectedTemplate.language)}</strong>
          <span class="ml-2">({draft.rows.length} baris ditampilkan)</span>
        </div>
        <div class="flex gap-2">
          <button
            type="button"
            onclick={handleReseedAll}
            class="rounded border border-slate-200 bg-white px-2.5 py-1 text-slate-700 shadow-2xs hover:bg-slate-50"
            title="Hitung ulang kombinasi persentase acak"
          >
            🎲 Acak Ulang Seluruh Persentase
          </button>
        </div>
      </div>

      <!-- Main Table -->
      <TimesheetGrid
        rows={draft.rows}
        template={selectedTemplate}
        {rawStringMode}
        {excelPreviewMode}
        onOpenStoryProgress={(sKey) => (selectedStoryKey = sKey)}
        onUpdateStoryEpic={handleUpdateEpic}
        onUpdateActivity={handleUpdateActivity}
        onAddActivity={handleAddActivity}
        onRemoveActivity={handleRemoveActivity}
        onUpdateCustomHours={handleUpdateCustomHours}
        onRemoveLeave={handleRemoveLeave}
        onAddLeaveClick={(d) => handleAddLeaves([d])}
      />

      <!-- Footer Signature Preview -->
      <SignatureFooterPreview
        employeeName={selectedTemplate.employee_name}
        teamLeadName={selectedTemplate.team_lead_name}
        employeeHasSig={sigStatus.employee}
        teamLeadHasSig={sigStatus.team_lead}
      />
    </div>
  {/if}

  <!-- 4. Sticky Action Bar (Bottom) -->
  <div class="sticky bottom-0 z-20 flex items-center justify-between rounded-xl border border-slate-200 bg-white/95 p-4 shadow-lg backdrop-blur-xs">
    <div class="flex items-center gap-2">
      <button
        type="button"
        onclick={() => (isLeaveModalOpen = true)}
        class="rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs font-medium text-slate-700 shadow-2xs hover:bg-slate-50"
      >
        + Tambah Cuti / Non-Tiket
      </button>
    </div>

    <div class="flex items-center gap-3">
      {#if summary.blockersCount > 0}
        <div class="text-right text-xs text-red-600">
          <span class="font-bold">⚠ Terdapat {summary.blockersCount} masalah blocker.</span>
          <span class="block text-[11px] text-slate-500">Isi Epic label atau estimasi untuk mengaktifkan download.</span>
        </div>
      {:else if summary.warningsCount > 0}
        <div class="text-right text-xs text-amber-700">
          <span>{summary.warningsCount} peringatan terdeteksi (opsional).</span>
        </div>
      {/if}

      <button
        type="button"
        disabled={!draft || summary.blockersCount > 0}
        onclick={handleGenerateClick}
        class="inline-flex cursor-pointer items-center gap-2 rounded-lg bg-primary-600 px-5 py-2 text-xs font-semibold text-white shadow-sm hover:bg-primary-700 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        <span>📊</span>
        <span>Generate .xlsx</span>
      </button>
    </div>
  </div>

  <!-- Story Progress Drawer -->
  {#if selectedStoryKey && draft}
    <StoryProgressDrawer
      storyKey={selectedStoryKey}
      {draft}
      template={selectedTemplate}
      {manualPercentages}
      {manualEstimates}
      {manualEpics}
      onClose={() => (selectedStoryKey = null)}
      onUpdateManualPercentages={handleSaveManualPercentages}
      onUpdateEstimate={handleUpdateEstimate}
      onUpdateEpic={(val) => {
        if (selectedStoryKey) manualEpics[selectedStoryKey] = val;
      }}
      onReseed={handleReseedStory}
    />
  {/if}

  <!-- Leave & Non-Ticket Modal -->
  <LeaveAndManualEntryModal
    isOpen={isLeaveModalOpen}
    {month}
    {year}
    existingLeaves={leaveDates}
    onClose={() => (isLeaveModalOpen = false)}
    onAddLeaves={handleAddLeaves}
    onRemoveLeave={handleRemoveLeave}
    onAddNonTicket={handleAddNonTicket}
  />

  <!-- Export Confirmation Popover/Modal bila ada warning -->
  {#if showExportConfirmModal}
    <div
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
    >
      <button
        type="button"
        class="fixed inset-0 bg-slate-900/40 backdrop-blur-2xs"
        onclick={() => (showExportConfirmModal = false)}
        aria-label="Tutup modal"
      ></button>

      <div class="relative z-10 w-full max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-2xl">
        <h3 class="text-sm font-bold text-slate-900">Konfirmasi Ekspor Timesheet</h3>
        <p class="mt-2 text-xs text-slate-600">
          Terdapat <strong class="text-amber-700">{summary.warningsCount} peringatan</strong> (mis. hari tanpa aktivitas atau kemungkinan typo) yang belum diperiksa.
        </p>
        <p class="mt-1 text-xs text-slate-500">
          Apakah Anda ingin tetap mengunduh berkas .xlsx sekarang?
        </p>

        <div class="mt-5 flex justify-end gap-2 text-xs">
          <button
            type="button"
            onclick={() => (showExportConfirmModal = false)}
            class="rounded border border-slate-300 px-3 py-1.5 text-slate-600 hover:bg-slate-50"
          >
            Periksa Lagi
          </button>
          <button
            type="button"
            onclick={executeDownload}
            class="rounded bg-primary-600 px-4 py-1.5 font-medium text-white shadow-xs hover:bg-primary-700"
          >
            Tetap Generate .xlsx
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>
