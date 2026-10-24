<script lang="ts">
  interface Props {
    employeeName: string;
    teamLeadName: string;
    employeeHasSig?: boolean;
    teamLeadHasSig?: boolean;
  }

  let {
    employeeName,
    teamLeadName,
    employeeHasSig = false,
    teamLeadHasSig = false
  }: Props = $props();
</script>

<div class="rounded-lg border border-slate-200 bg-white p-4 shadow-xs">
  <div class="mb-3 flex items-center justify-between">
    <span class="text-xs font-bold uppercase tracking-wider text-slate-500">Pratinjau Blok Tanda Tangan Footer Excel</span>
    <span class="text-[11px] text-slate-400">Dirender otomatis pada kolom B (Employee) dan kolom F (Team Lead)</span>
  </div>

  <div class="grid grid-cols-2 gap-8 text-center text-xs">
    <!-- Employee Box -->
    <div class="flex flex-col items-center justify-between rounded border border-slate-200 bg-slate-50/50 p-3">
      <span class="font-bold text-slate-800">Employee</span>
      <div class="my-3 flex h-16 w-36 items-center justify-center rounded border border-dashed border-slate-300 bg-white p-1">
        {#if employeeHasSig}
          <span class="font-mono text-xs text-emerald-600">✍ [Tanda Tangan Tersemat]</span>
        {:else}
          <span class="text-[11px] text-slate-400">(Tanda tangan belum diunggah)</span>
        {/if}
      </div>
      <span class="font-semibold text-slate-900 underline">{employeeName || 'Aria Nur Jamal'}</span>
    </div>

    <!-- Team Lead Box -->
    <div class="flex flex-col items-center justify-between rounded border border-slate-200 bg-slate-50/50 p-3">
      <span class="font-bold text-slate-800">Team Lead</span>
      <div class="my-3 flex h-16 w-36 items-center justify-center rounded border border-dashed border-slate-300 bg-white p-1">
        {#if teamLeadHasSig}
          <span class="font-mono text-xs text-emerald-600">✍ [Tanda Tangan Tersemat]</span>
        {:else}
          <span class="text-[11px] text-slate-400">(Tanda tangan belum diunggah)</span>
        {/if}
      </div>
      <span class="font-semibold text-slate-900 underline">{teamLeadName || 'Kevin Saputra'}</span>
    </div>
  </div>
</div>
