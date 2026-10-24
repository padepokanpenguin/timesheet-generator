<script lang="ts">
  import { uploadSignature, deleteSignature } from '@timesheet/api-client';

  interface Props {
    role: 'employee' | 'team_lead';
    label: string;
    name: string;
    hasSignature?: boolean;
    onStatusChange?: () => void;
  }

  let {
    role,
    label,
    name,
    hasSignature = false,
    onStatusChange = () => {}
  }: Props = $props();

  let fileInput: HTMLInputElement;
  let isUploading = $state(false);
  let errorMessage = $state('');
  let previewUrl = $state<string | null>(null);

  async function handleFileSelected(e: Event) {
    const input = e.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    errorMessage = '';

    // Validasi format
    if (!['image/png', 'image/jpeg', 'image/jpg'].includes(file.type)) {
      errorMessage = 'Format berkas harus PNG atau JPG.';
      input.value = '';
      return;
    }

    // Validasi ukuran <= 1 MB
    if (file.size > 1_000_000) {
      errorMessage = 'Ukuran berkas melebihi batas 1 MB.';
      input.value = '';
      return;
    }

    // Buat pratinjau lokal
    previewUrl = URL.createObjectURL(file);

    try {
      isUploading = true;
      await uploadSignature(role, file);
      onStatusChange();
    } catch (err) {
      errorMessage = err instanceof Error ? err.message : 'Gagal mengunggah tanda tangan.';
      previewUrl = null;
    } finally {
      isUploading = false;
      input.value = '';
    }
  }

  async function handleDelete() {
    try {
      isUploading = true;
      await deleteSignature(role);
      previewUrl = null;
      onStatusChange();
    } catch (err) {
      errorMessage = err instanceof Error ? err.message : 'Gagal menghapus tanda tangan.';
    } finally {
      isUploading = false;
    }
  }
</script>

<div class="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-5 shadow-xs">
  <div class="flex items-center justify-between">
    <div>
      <span class="text-xs font-semibold uppercase tracking-wider text-slate-500">{label}</span>
      <h4 class="text-sm font-semibold text-slate-900">{name}</h4>
    </div>
    {#if hasSignature}
      <span class="inline-flex items-center gap-1 rounded bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700">
        <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
        Tanda Tangan Tersedia
      </span>
    {:else}
      <span class="inline-flex items-center gap-1 rounded bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-700">
        <span class="h-1.5 w-1.5 rounded-full bg-amber-500"></span>
        Belum Diunggah
      </span>
    {/if}
  </div>

  <!-- Pratinjau Tanda Tangan dengan Latar Transparan (Checkerboard) -->
  <div class="relative flex h-32 items-center justify-center rounded-lg border border-slate-200 bg-checkerboard p-3 text-center">
    {#if previewUrl}
      <img src={previewUrl} alt="Pratinjau Tanda Tangan" class="max-h-full max-w-full object-contain" />
    {:else if hasSignature}
      <div class="flex flex-col items-center justify-center text-xs text-slate-600">
        <span class="rounded bg-white/90 px-2 py-1 font-mono shadow-2xs">
          ✍ Berkas tanda tangan tersimpan di server
        </span>
      </div>
    {:else}
      <div class="flex flex-col items-center justify-center text-xs text-slate-400">
        <span>Seret atau unggah gambar tanda tangan PNG/JPG transparan</span>
        <span class="text-[11px]">(Maks. 1 MB)</span>
      </div>
    {/if}
  </div>

  {#if errorMessage}
    <p class="text-xs text-red-600">⚠ {errorMessage}</p>
  {/if}

  <!-- Tombol Aksi -->
  <div class="flex items-center justify-between pt-1 text-xs">
    <input
      type="file"
      accept="image/png,image/jpeg"
      bind:this={fileInput}
      onchange={handleFileSelected}
      class="hidden"
    />
    <button
      type="button"
      onclick={() => fileInput.click()}
      disabled={isUploading}
      class="rounded-lg bg-primary-600 px-3.5 py-2 font-medium text-white shadow-xs hover:bg-primary-700 disabled:bg-slate-300"
    >
      {isUploading ? 'Mengunggah...' : hasSignature ? 'Ganti Tanda Tangan' : 'Unggah Tanda Tangan'}
    </button>

    {#if hasSignature}
      <button
        type="button"
        onclick={handleDelete}
        disabled={isUploading}
        class="text-red-600 hover:text-red-800 hover:underline"
      >
        Hapus
      </button>
    {/if}
  </div>
</div>
