<script lang="ts">
  interface Props {
    isOpen: boolean;
    month: number;
    year: number;
    existingLeaves?: string[];
    onClose?: () => void;
    onAddLeaves?: (dates: string[]) => void;
    onRemoveLeave?: (date: string) => void;
    onAddNonTicket?: (date: string, text: string) => void;
  }

  let {
    isOpen = false,
    month,
    year,
    existingLeaves = [],
    onClose = () => {},
    onAddLeaves = () => {},
    onRemoveLeave = () => {},
    onAddNonTicket = () => {}
  }: Props = $props();

  let activeTab = $state<'leave' | 'non-ticket'>('leave');

  // Leave form state
  let leaveMode = $state<'single' | 'range'>('single');
  let singleDate = $state('');
  let startDate = $state('');
  let endDate = $state('');

  // Non-ticket form state
  let nonTicketDate = $state('');
  let nonTicketText = $state('');

  $effect(() => {
    if (isOpen) {
      const defaultDay = `${year}-${String(month).padStart(2, '0')}-05`;
      if (!singleDate) singleDate = defaultDay;
      if (!startDate) startDate = defaultDay;
      if (!endDate) endDate = `${year}-${String(month).padStart(2, '0')}-09`;
      if (!nonTicketDate) nonTicketDate = defaultDay;
    }
  });

  function handleSaveLeave() {
    if (leaveMode === 'single') {
      if (singleDate) {
        onAddLeaves([singleDate]);
        onClose();
      }
    } else {
      if (startDate && endDate && startDate <= endDate) {
        const dates: string[] = [];
        const current = new Date(startDate + 'T00:00:00');
        const end = new Date(endDate + 'T00:00:00');
        while (current <= end) {
          const y = current.getFullYear();
          const m = String(current.getMonth() + 1).padStart(2, '0');
          const d = String(current.getDate()).padStart(2, '0');
          dates.push(`${y}-${m}-${d}`);
          current.setDate(current.getDate() + 1);
        }
        onAddLeaves(dates);
        onClose();
      }
    }
  }

  function handleSaveNonTicket() {
    if (nonTicketDate && nonTicketText.trim()) {
      onAddNonTicket(nonTicketDate, nonTicketText.trim());
      nonTicketText = '';
      onClose();
    }
  }
</script>

{#if isOpen}
  <!-- Backdrop -->
  <button
    type="button"
    class="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-2xs transition-opacity"
    onclick={() => onClose()}
    aria-label="Tutup modal"
  ></button>

  <!-- Modal Dialog -->
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-4"
    role="dialog"
    aria-modal="true"
    aria-labelledby="modal-title"
  >
    <div class="w-full max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-2xl">
      <!-- Modal Header -->
      <div class="flex items-center justify-between border-b border-slate-200 pb-3">
        <h3 id="modal-title" class="text-base font-semibold text-slate-900">
          Kelola Cuti & Entri Non-Tiket
        </h3>
        <button
          type="button"
          onclick={() => onClose()}
          class="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
        >
          ✕
        </button>
      </div>

      <!-- Tabs -->
      <div class="mt-4 flex border-b border-slate-200 text-xs font-medium">
        <button
          type="button"
          onclick={() => (activeTab = 'leave')}
          class="border-b-2 px-4 py-2 {activeTab === 'leave' ? 'border-primary-600 text-primary-700' : 'border-transparent text-slate-500 hover:text-slate-800'}"
        >
          1. Tambah / Kelola Cuti
        </button>
        <button
          type="button"
          onclick={() => (activeTab = 'non-ticket')}
          class="border-b-2 px-4 py-2 {activeTab === 'non-ticket' ? 'border-primary-600 text-primary-700' : 'border-transparent text-slate-500 hover:text-slate-800'}"
        >
          2. Entri Non-Tiket
        </button>
      </div>

      <!-- Tab 1: Cuti -->
      {#if activeTab === 'leave'}
        <div class="mt-4 space-y-4 text-xs">
          <div>
            <span class="block font-medium text-slate-700">Tipe Input Cuti:</span>
            <div class="mt-1 flex gap-4">
              <label class="inline-flex cursor-pointer items-center gap-1.5">
                <input type="radio" bind:group={leaveMode} value="single" class="accent-primary-600" />
                <span>Satu Tanggal</span>
              </label>
              <label class="inline-flex cursor-pointer items-center gap-1.5">
                <input type="radio" bind:group={leaveMode} value="range" class="accent-primary-600" />
                <span>Rentang Tanggal</span>
              </label>
            </div>
          </div>

          {#if leaveMode === 'single'}
            <div>
              <label for="single-date-input" class="block font-medium text-slate-700">Pilih Tanggal Cuti:</label>
              <input
                id="single-date-input"
                type="date"
                bind:value={singleDate}
                class="mt-1 w-full rounded border border-slate-300 px-3 py-1.5 text-xs text-slate-800 focus:border-primary-500 focus:outline-hidden"
              />
            </div>
          {:else}
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label for="range-start-date" class="block font-medium text-slate-700">Dari Tanggal:</label>
                <input
                  id="range-start-date"
                  type="date"
                  bind:value={startDate}
                  class="mt-1 w-full rounded border border-slate-300 px-3 py-1.5 text-xs text-slate-800 focus:border-primary-500 focus:outline-hidden"
                />
              </div>
              <div>
                <label for="range-end-date" class="block font-medium text-slate-700">Sampai Tanggal:</label>
                <input
                  id="range-end-date"
                  type="date"
                  bind:value={endDate}
                  class="mt-1 w-full rounded border border-slate-300 px-3 py-1.5 text-xs text-slate-800 focus:border-primary-500 focus:outline-hidden"
                />
              </div>
            </div>
          {/if}

          <!-- Daftar Cuti Terdaftar -->
          {#if existingLeaves.length > 0}
            <div class="border-t border-slate-100 pt-3">
              <span class="block font-medium text-slate-700">Cuti Terdaftar Bulan Ini ({existingLeaves.length} hari):</span>
              <div class="mt-1.5 flex flex-wrap gap-1.5">
                {#each existingLeaves as lDate}
                  <span class="inline-flex items-center gap-1 rounded bg-excel-redSurface px-2 py-0.5 text-[11px] font-semibold text-excel-redText">
                    {lDate}
                    <button
                      type="button"
                      onclick={() => onRemoveLeave(lDate)}
                      class="text-red-500 hover:text-red-700"
                      title="Hapus cuti"
                    >
                      ✕
                    </button>
                  </span>
                {/each}
              </div>
            </div>
          {/if}

          <div class="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onclick={() => onClose()}
              class="rounded border border-slate-300 px-3 py-1.5 text-slate-600 hover:bg-slate-50"
            >
              Batal
            </button>
            <button
              type="button"
              onclick={handleSaveLeave}
              class="rounded bg-primary-600 px-4 py-1.5 font-medium text-white shadow-xs hover:bg-primary-700"
            >
              Simpan Cuti
            </button>
          </div>
        </div>
      {/if}

      <!-- Tab 2: Entri Non-Tiket -->
      {#if activeTab === 'non-ticket'}
        <div class="mt-4 space-y-4 text-xs">
          <div>
            <label for="non-ticket-date" class="block font-medium text-slate-700">Tanggal Kerja:</label>
            <input
              id="non-ticket-date"
              type="date"
              bind:value={nonTicketDate}
              class="mt-1 w-full rounded border border-slate-300 px-3 py-1.5 text-xs text-slate-800 focus:border-primary-500 focus:outline-hidden"
            />
          </div>

          <div>
            <label for="non-ticket-desc" class="block font-medium text-slate-700">Deskripsi Aktivitas Non-Tiket:</label>
            <textarea
              id="non-ticket-desc"
              rows="3"
              bind:value={nonTicketText}
              placeholder="Contoh: penyediaan data untuk kebutuhan UAT tim QA..."
              class="mt-1 w-full rounded border border-slate-300 p-2 text-xs text-slate-800 focus:border-primary-500 focus:outline-hidden"
            ></textarea>
            <p class="mt-1 text-[11px] text-slate-500">
              Entri ini akan diletakkan di akhir sel Information Activity pada tanggal terpilih tanpa kode tiket.
            </p>
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onclick={() => onClose()}
              class="rounded border border-slate-300 px-3 py-1.5 text-slate-600 hover:bg-slate-50"
            >
              Batal
            </button>
            <button
              type="button"
              disabled={!nonTicketText.trim()}
              onclick={handleSaveNonTicket}
              class="rounded bg-primary-600 px-4 py-1.5 font-medium text-white shadow-xs hover:bg-primary-700 disabled:bg-slate-300"
            >
              Tambahkan ke Timesheet
            </button>
          </div>
        </div>
      {/if}
    </div>
  </div>
{/if}
