<script lang="ts">
  import { onMount } from 'svelte';
  import {
    listTemplates,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    simulateFormula,
    type TemplateSpec,
    type TemplateSpecInput,
    type FormulaSimulateResponse
  } from '@timesheet/api-client';

  let templates = $state<TemplateSpec[]>([]);
  let selectedId = $state<string>('');
  let loading = $state(true);
  let error = $state('');
  let notice = $state('');

  // Template Form State
  let formId = $state('');
  let formName = $state('');
  let formLanguage = $state<'id' | 'en'>('id');
  let formCompanyName = $state('');
  let formClient = $state('');
  let formDepartment = $state('');
  let formTitle = $state('');
  let formEmployeeName = $state('');
  let formTeamLeadName = $state('');
  let formWorkStart = $state('08:30');
  let formWorkEnd = $state('17:30');
  let formBreakMinutes = $state(60);
  let formShowAllDays = $state(true);
  let formTimezone = $state('Asia/Jakarta');
  let formHolidayCountry = $state('ID');
  let formExtraHolidays = $state<string[]>([]);
  let newHolidayInput = $state('');

  // Formula Parameters
  let formHoursPerManday = $state(8.0);
  let formStoryPointToManday = $state(1.0);
  let formMaxProgressBeforeDone = $state(95);
  let formRoundingStep = $state(5);
  let formMinDailyPortion = $state(5);
  let formSegmentationMode = $state<'random' | 'manual'>('random');
  let formCarryOver = $state(true);

  // Live Formula Simulator State
  let simEstimate = $state(4.0);
  let simDays = $state(3);
  let simDone = $state(false);
  let simStartPercent = $state(0);
  let simResult = $state<FormulaSimulateResponse | null>(null);
  let isSimulating = $state(false);

  let isNewTemplate = $state(false);

  async function loadTemplates() {
    try {
      loading = true;
      templates = await listTemplates();
      if (templates.length > 0 && !selectedId) {
        selectTemplate(templates[0]);
      }
    } catch (e) {
      error = (e as Error).message;
    } finally {
      loading = false;
    }
  }

  function selectTemplate(t: TemplateSpec) {
    selectedId = t.id;
    isNewTemplate = false;
    formId = t.id;
    formName = t.name;
    formLanguage = t.language;
    formCompanyName = t.company_name;
    formClient = t.client;
    formDepartment = t.department;
    formTitle = t.title;
    formEmployeeName = t.employee_name;
    formTeamLeadName = t.team_lead_name;
    formWorkStart = t.work_start;
    formWorkEnd = t.work_end;
    formBreakMinutes = t.break_minutes;
    formShowAllDays = t.show_all_days;
    formTimezone = t.timezone;
    formHolidayCountry = t.holiday_country;
    formExtraHolidays = [...(t.extra_holidays || [])];

    // Formula
    formHoursPerManday = t.formula.hours_per_manday;
    formStoryPointToManday = t.formula.story_point_to_manday;
    formMaxProgressBeforeDone = t.formula.max_progress_before_done;
    formRoundingStep = t.formula.rounding_step;
    formMinDailyPortion = t.formula.min_daily_portion;
    formSegmentationMode = t.formula.segmentation_mode;
    formCarryOver = t.formula.carry_over_between_months;

    runSimulation();
  }

  function startNewTemplate() {
    isNewTemplate = true;
    selectedId = '';
    formId = `template-${Date.now().toString().slice(-4)}`;
    formName = 'Template Baru';
    formLanguage = 'id';
    formCompanyName = 'PT. Baru Makmur';
    formClient = 'Klien Baru';
    formDepartment = 'IT Engineering';
    formTitle = 'Software Engineer';
    formEmployeeName = 'Nama Karyawan';
    formTeamLeadName = 'Nama Team Lead';
    formWorkStart = '08:30';
    formWorkEnd = '17:30';
    formBreakMinutes = 60;
    formShowAllDays = true;
    formTimezone = 'Asia/Jakarta';
    formHolidayCountry = 'ID';
    formExtraHolidays = [];
    runSimulation();
  }

  async function handleSaveTemplate() {
    error = '';
    notice = '';

    const payload: TemplateSpecInput = {
      id: formId,
      name: formName,
      language: formLanguage,
      company_name: formCompanyName,
      client: formClient,
      department: formDepartment,
      title: formTitle,
      employee_name: formEmployeeName,
      team_lead_name: formTeamLeadName,
      work_start: formWorkStart,
      work_end: formWorkEnd,
      break_minutes: formBreakMinutes,
      show_all_days: formShowAllDays,
      timezone: formTimezone,
      holiday_country: formHolidayCountry,
      extra_holidays: formExtraHolidays,
      file_name_pattern: 'TimeSheet_{name}_{year}.xlsx',
      formula: {
        hours_per_manday: formHoursPerManday,
        story_point_to_manday: formStoryPointToManday,
        max_progress_before_done: formMaxProgressBeforeDone,
        rounding_step: formRoundingStep,
        min_daily_portion: formMinDailyPortion,
        segmentation_mode: formSegmentationMode,
        carry_over_between_months: formCarryOver
      }
    };

    try {
      if (isNewTemplate) {
        const created = await createTemplate(payload);
        notice = `Template '${created.name}' berhasil dibuat!`;
      } else {
        const updated = await updateTemplate(formId, payload);
        notice = `Template '${updated.name}' berhasil diperbarui!`;
      }
      await loadTemplates();
      selectedId = formId;
      isNewTemplate = false;
    } catch (e) {
      error = (e as Error).message;
    }
  }

  async function handleDeleteTemplate() {
    if (!selectedId) return;
    if (!confirm(`Hapus template '${formName}'?`)) return;

    try {
      await deleteTemplate(selectedId);
      notice = `Template berhasil dihapus.`;
      selectedId = '';
      await loadTemplates();
    } catch (e) {
      error = (e as Error).message;
    }
  }

  function addExtraHoliday() {
    if (newHolidayInput && !formExtraHolidays.includes(newHolidayInput)) {
      formExtraHolidays.push(newHolidayInput);
      newHolidayInput = '';
    }
  }

  function removeExtraHoliday(dateStr: string) {
    formExtraHolidays = formExtraHolidays.filter((d) => d !== dateStr);
  }

  async function runSimulation() {
    try {
      isSimulating = true;
      simResult = await simulateFormula({
        formula: {
          hours_per_manday: formHoursPerManday,
          story_point_to_manday: formStoryPointToManday,
          max_progress_before_done: formMaxProgressBeforeDone,
          rounding_step: formRoundingStep,
          min_daily_portion: formMinDailyPortion,
          segmentation_mode: formSegmentationMode,
          carry_over_between_months: formCarryOver
        },
        estimate_mandays: simEstimate,
        active_days: simDays,
        done: simDone,
        start_percent: simStartPercent,
        seed: 'sim-seed'
      });
    } catch {
      simResult = null;
    } finally {
      isSimulating = false;
    }
  }

  onMount(() => {
    loadTemplates();
  });
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between border-b border-slate-200 pb-4">
    <div>
      <h2 class="text-lg font-bold text-slate-900">Pengaturan Template & Formula Admin</h2>
      <p class="text-xs text-slate-500">
        Konfigurasi header timesheet, jam kerja, cuti bersama, dan formula persentase per perusahaan.
      </p>
    </div>
    <button
      type="button"
      onclick={startNewTemplate}
      class="rounded-lg bg-primary-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-xs hover:bg-primary-700"
    >
      + Buat Template Baru
    </button>
  </div>

  {#if error}
    <div class="rounded-lg border border-red-200 bg-red-50 p-3 text-xs text-red-900">
      ⚠ {error}
    </div>
  {/if}

  {#if notice}
    <div class="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-900">
      ✓ {notice}
    </div>
  {/if}

  <div class="grid grid-cols-1 gap-6 lg:grid-cols-4">
    <!-- Sidebar: Template List -->
    <div class="space-y-2 lg:col-span-1">
      <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500">Daftar Template</h3>
      <div class="divide-y divide-slate-100 rounded-xl border border-slate-200 bg-white shadow-xs">
        {#each templates as t}
          <button
            type="button"
            onclick={() => selectTemplate(t)}
            class="flex w-full cursor-pointer flex-col p-3 text-left transition hover:bg-slate-50 {selectedId === t.id && !isNewTemplate ? 'bg-primary-50 text-primary-900 font-semibold' : 'text-slate-800'}"
          >
            <span class="text-xs">{t.name}</span>
            <span class="text-[11px] text-slate-400">{t.company_name} · [{t.language.toUpperCase()}]</span>
          </button>
        {/each}
      </div>
    </div>

    <!-- Main Editor Form -->
    <div class="space-y-6 lg:col-span-3">
      <!-- Seksi 1: Identitas & Header Perusahaan -->
      <section class="rounded-xl border border-slate-200 bg-white p-5 shadow-xs">
        <h3 class="text-sm font-bold text-slate-900">Seksi 1: Identitas & Header Perusahaan</h3>
        <p class="mt-0.5 text-xs text-slate-500">
          Parameter ini dimasukkan ke baris header A9 dan B11..F12 pada lembar Excel.
        </p>

        <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 text-xs">
          <div>
            <label for="form-template-id" class="block font-medium text-slate-700">ID Template (Kunci Unik):</label>
            <input
              id="form-template-id"
              type="text"
              bind:value={formId}
              disabled={!isNewTemplate}
              class="mt-1 w-full rounded border border-slate-300 p-2 text-xs disabled:bg-slate-100"
            />
          </div>

          <div>
            <label for="form-template-name" class="block font-medium text-slate-700">Nama Tampilan Template:</label>
            <input
              id="form-template-name"
              type="text"
              bind:value={formName}
              class="mt-1 w-full rounded border border-slate-300 p-2 text-xs"
            />
          </div>

          <div>
            <label for="form-company-name" class="block font-medium text-slate-700">Nama Perusahaan Karyawan (A9):</label>
            <input
              id="form-company-name"
              type="text"
              bind:value={formCompanyName}
              class="mt-1 w-full rounded border border-slate-300 p-2 text-xs"
            />
          </div>

          <div>
            <label for="form-client-name" class="block font-medium text-slate-700">Perusahaan Klien (Kolom D):</label>
            <input
              id="form-client-name"
              type="text"
              bind:value={formClient}
              class="mt-1 w-full rounded border border-slate-300 p-2 text-xs"
            />
          </div>

          <div>
            <label for="form-dept" class="block font-medium text-slate-700">Departemen (Kolom E):</label>
            <input
              id="form-dept"
              type="text"
              bind:value={formDepartment}
              class="mt-1 w-full rounded border border-slate-300 p-2 text-xs"
            />
          </div>

          <div>
            <label for="form-title" class="block font-medium text-slate-700">Jabatan / Title (Kolom A:B):</label>
            <input
              id="form-title"
              type="text"
              bind:value={formTitle}
              class="mt-1 w-full rounded border border-slate-300 p-2 text-xs"
            />
          </div>

          <div>
            <label for="form-emp-name" class="block font-medium text-slate-700">Nama Karyawan (Kolom C & Footer B):</label>
            <input
              id="form-emp-name"
              type="text"
              bind:value={formEmployeeName}
              class="mt-1 w-full rounded border border-slate-300 p-2 text-xs"
            />
          </div>

          <div>
            <label for="form-tl-name" class="block font-medium text-slate-700">Nama Team Lead (Footer F):</label>
            <input
              id="form-tl-name"
              type="text"
              bind:value={formTeamLeadName}
              class="mt-1 w-full rounded border border-slate-300 p-2 text-xs"
            />
          </div>

          <div>
            <label for="form-lang-select" class="block font-medium text-slate-700">Bahasa Output Template:</label>
            <select
              id="form-lang-select"
              bind:value={formLanguage}
              class="mt-1 w-full rounded border border-slate-300 p-2 text-xs"
            >
              <option value="id">Bahasa Indonesia (Januari..Desember, Periode, CUTI)</option>
              <option value="en">English (January..December, Period, LEAVE)</option>
            </select>
          </div>

          <div>
            <label for="form-show-days-select" class="block font-medium text-slate-700">Tampilan Hari Default:</label>
            <select
              id="form-show-days-select"
              bind:value={formShowAllDays}
              class="mt-1 w-full rounded border border-slate-300 p-2 text-xs"
            >
              <option value={true}>Semua Hari Kalender (1..31, Akhir pekan merah)</option>
              <option value={false}>Hanya Hari Kerja (Id dinomori ulang)</option>
            </select>
          </div>
        </div>
      </section>

      <!-- Seksi 2: Jam Kerja & Kalender Libur Tambahan -->
      <section class="rounded-xl border border-slate-200 bg-white p-5 shadow-xs">
        <h3 class="text-sm font-bold text-slate-900">Seksi 2: Jam Kerja & Kalender Libur (extra_holidays)</h3>
        <p class="mt-0.5 text-xs text-slate-500">
          Atur jam masuk, jam keluar, durasi istirahat, dan daftar cuti bersama / libur kustom.
        </p>

        <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3 text-xs">
          <div>
            <label for="form-work-start" class="block font-medium text-slate-700">Jam Masuk Default:</label>
            <input
              id="form-work-start"
              type="text"
              bind:value={formWorkStart}
              class="mt-1 w-full rounded border border-slate-300 p-2 font-mono text-xs"
              placeholder="08:30"
            />
          </div>

          <div>
            <label for="form-work-end" class="block font-medium text-slate-700">Jam Pulang Default:</label>
            <input
              id="form-work-end"
              type="text"
              bind:value={formWorkEnd}
              class="mt-1 w-full rounded border border-slate-300 p-2 font-mono text-xs"
              placeholder="17:30"
            />
          </div>

          <div>
            <label for="form-break-mins" class="block font-medium text-slate-700">Istirahat (Menit):</label>
            <input
              id="form-break-mins"
              type="number"
              bind:value={formBreakMinutes}
              class="mt-1 w-full rounded border border-slate-300 p-2 font-mono text-xs"
            />
          </div>
        </div>

        <!-- Extra Holidays Editor -->
        <div class="mt-4 border-t border-slate-100 pt-4 text-xs">
          <label for="new-holiday-input" class="block font-medium text-slate-700">Libur Tambahan / Cuti Bersama (extra_holidays):</label>
          <div class="mt-2 flex gap-2">
            <input
              id="new-holiday-input"
              type="date"
              bind:value={newHolidayInput}
              class="rounded border border-slate-300 p-1.5 text-xs"
            />
            <button
              type="button"
              onclick={addExtraHoliday}
              class="rounded bg-slate-800 px-3 py-1.5 font-medium text-white hover:bg-slate-900"
            >
              + Tambah Tanggal Libur
            </button>
          </div>

          <div class="mt-3 flex flex-wrap gap-2">
            {#each formExtraHolidays as hDate}
              <span class="inline-flex items-center gap-1.5 rounded bg-red-50 px-2.5 py-1 text-xs font-semibold text-red-700">
                {hDate}
                <button
                  type="button"
                  onclick={() => removeExtraHoliday(hDate)}
                  class="text-red-500 hover:text-red-800"
                >
                  ✕
                </button>
              </span>
            {/each}
          </div>
        </div>
      </section>

      <!-- Seksi 3: Parameter Formula Progres & Live Simulator -->
      <section class="rounded-xl border border-slate-200 bg-white p-5 shadow-xs">
        <h3 class="text-sm font-bold text-slate-900">Seksi 3: Parameter Formula Progres (PRD 5.4.3)</h3>
        <p class="mt-0.5 text-xs text-slate-500">
          Formula pembagian persentase harian kumulatif per Story.
        </p>

        <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3 text-xs">
          <div>
            <label for="form-hours-manday" class="block font-medium text-slate-700">1 Manday = Jam:</label>
            <input
              id="form-hours-manday"
              type="number"
              bind:value={formHoursPerManday}
              onchange={runSimulation}
              class="mt-1 w-full rounded border border-slate-300 p-2 font-mono text-xs"
            />
          </div>

          <div>
            <label for="form-sp-manday" class="block font-medium text-slate-700">1 Story Point = Manday:</label>
            <input
              id="form-sp-manday"
              type="number"
              bind:value={formStoryPointToManday}
              onchange={runSimulation}
              class="mt-1 w-full rounded border border-slate-300 p-2 font-mono text-xs"
            />
          </div>

          <div>
            <label for="form-max-progress" class="block font-medium text-slate-700">Batas Sebelum Done (%):</label>
            <input
              id="form-max-progress"
              type="number"
              bind:value={formMaxProgressBeforeDone}
              onchange={runSimulation}
              class="mt-1 w-full rounded border border-slate-300 p-2 font-mono text-xs"
            />
          </div>

          <div>
            <label for="form-rounding-step" class="block font-medium text-slate-700">Pembulatan Kelipatan (%):</label>
            <input
              id="form-rounding-step"
              type="number"
              bind:value={formRoundingStep}
              onchange={runSimulation}
              class="mt-1 w-full rounded border border-slate-300 p-2 font-mono text-xs"
            />
          </div>

          <div>
            <label for="form-min-portion" class="block font-medium text-slate-700">Porsi Harian Minimum (%):</label>
            <input
              id="form-min-portion"
              type="number"
              bind:value={formMinDailyPortion}
              onchange={runSimulation}
              class="mt-1 w-full rounded border border-slate-300 p-2 font-mono text-xs"
            />
          </div>
        </div>

        <!-- Live Formula Simulator Box -->
        <div class="mt-6 rounded-lg border border-blue-200 bg-blue-50/50 p-4 text-xs">
          <div class="flex items-center justify-between">
            <h4 class="font-bold text-blue-900">🔬 Simulasi Formula Langsung</h4>
            <span class="text-[11px] text-blue-700">Uji skenario pembagian progres secara instan</span>
          </div>

          <div class="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <div>
              <label for="sim-est-input" class="block text-slate-600">Estimasi (md):</label>
              <input
                id="sim-est-input"
                type="number"
                step="0.5"
                bind:value={simEstimate}
                onchange={runSimulation}
                class="mt-1 w-full rounded border border-slate-300 bg-white p-1.5 font-mono text-xs"
              />
            </div>
            <div>
              <label for="sim-days-input" class="block text-slate-600">Hari Aktif:</label>
              <input
                id="sim-days-input"
                type="number"
                min="1"
                max="22"
                bind:value={simDays}
                onchange={runSimulation}
                class="mt-1 w-full rounded border border-slate-300 bg-white p-1.5 font-mono text-xs"
              />
            </div>
            <div>
              <label for="sim-start-input" class="block text-slate-600">Progres Awal (%):</label>
              <input
                id="sim-start-input"
                type="number"
                min="0"
                max="100"
                bind:value={simStartPercent}
                onchange={runSimulation}
                class="mt-1 w-full rounded border border-slate-300 bg-white p-1.5 font-mono text-xs"
              />
            </div>
            <div class="flex flex-col justify-end">
              <label class="inline-flex cursor-pointer items-center gap-1.5 pb-2">
                <input
                  type="checkbox"
                  bind:checked={simDone}
                  onchange={runSimulation}
                  class="accent-primary-600"
                />
                <span class="font-medium text-slate-800">Status Done (100%)</span>
              </label>
            </div>
          </div>

          {#if simResult}
            <div class="mt-4 rounded border border-blue-200 bg-white p-3">
              <div class="flex items-center justify-between">
                <span class="font-medium text-slate-700">
                  Target Total Progres: <strong class="font-mono text-primary-700">{simResult.total_progress}%</strong>
                </span>
                <span class="text-[11px] text-slate-400">
                  {isSimulating ? 'Menghitung...' : 'Kombinasi acak terkunci'}
                </span>
              </div>
              <div class="mt-2 flex items-center gap-2">
                <span class="text-slate-500">Hasil harian:</span>
                {#each simResult.daily_percentages as pct, i}
                  <span class="rounded bg-slate-100 px-2 py-0.5 font-mono font-semibold text-slate-900">
                    Hari {i + 1}: {pct}%
                  </span>
                {/each}
              </div>
            </div>
          {/if}
        </div>
      </section>

      <!-- Action Buttons -->
      <div class="flex items-center justify-between pt-2">
        {#if !isNewTemplate && templates.length > 1}
          <button
            type="button"
            onclick={handleDeleteTemplate}
            class="rounded-lg border border-red-300 px-4 py-2 text-xs font-medium text-red-600 hover:bg-red-50"
          >
            Hapus Template Ini
          </button>
        {:else}
          <div></div>
        {/if}

        <button
          type="button"
          onclick={handleSaveTemplate}
          class="rounded-lg bg-primary-600 px-6 py-2 text-xs font-semibold text-white shadow-xs hover:bg-primary-700"
        >
          {isNewTemplate ? 'Simpan Template Baru' : 'Simpan Perubahan Template'}
        </button>
      </div>
    </div>
  </div>
</div>
