<script lang="ts">
  import { onMount } from 'svelte';
  import {
    listTemplates,
    getSignatureStatus,
    type TemplateSpec,
    type SignatureStatus
  } from '@timesheet/api-client';
  import SignatureUploader from '$lib/components/signature/SignatureUploader.svelte';

  let templates = $state<TemplateSpec[]>([]);
  let selectedTemplate = $state<TemplateSpec | null>(null);
  let sigStatus = $state<SignatureStatus>({ employee: false, team_lead: false });
  let loading = $state(true);
  let notice = $state('');

  async function refresh() {
    try {
      loading = true;
      templates = await listTemplates();
      if (templates.length > 0 && !selectedTemplate) {
        selectedTemplate = templates[0];
      }
      sigStatus = await getSignatureStatus();
    } catch {
      // ignore
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    refresh();
  });
</script>

<div class="space-y-6">
  <!-- Page Header -->
  <div class="flex items-center justify-between border-b border-slate-200 pb-4">
    <div>
      <h2 class="text-lg font-bold text-slate-900">Profil & Tanda Tangan</h2>
      <p class="text-xs text-slate-500">
        Kelola identitas diri dan berkas gambar tanda tangan untuk footer timesheet.
      </p>
    </div>
  </div>

  {#if notice}
    <div class="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-900">
      {notice}
    </div>
  {/if}

  {#if loading}
    <p class="py-8 text-center text-xs text-slate-400">Memuat profil...</p>
  {:else}
    <!-- Section 1: Identitas Pengguna Aktif -->
    <section class="rounded-xl border border-slate-200 bg-white p-5 shadow-xs">
      <h3 class="text-sm font-bold text-slate-900">Identitas Karyawan & Team Lead</h3>
      <p class="mt-0.5 text-xs text-slate-500">
        Data ini diambil dari template aktif dan dicantumkan pada header sel A9, B12, C12, D12, E12, serta footer Excel.
      </p>

      {#if selectedTemplate}
        <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 text-xs">
          <div class="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <span class="text-slate-500">Nama Karyawan:</span>
            <strong class="mt-1 block text-slate-900">{selectedTemplate.employee_name}</strong>
          </div>

          <div class="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <span class="text-slate-500">Jabatan (Title):</span>
            <strong class="mt-1 block text-slate-900">{selectedTemplate.title}</strong>
          </div>

          <div class="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <span class="text-slate-500">Perusahaan Karyawan:</span>
            <strong class="mt-1 block text-slate-900">{selectedTemplate.company_name}</strong>
          </div>

          <div class="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <span class="text-slate-500">Perusahaan Klien (Company):</span>
            <strong class="mt-1 block text-slate-900">{selectedTemplate.client}</strong>
          </div>

          <div class="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <span class="text-slate-500">Departemen:</span>
            <strong class="mt-1 block text-slate-900">{selectedTemplate.department}</strong>
          </div>

          <div class="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <span class="text-slate-500">Team Lead:</span>
            <strong class="mt-1 block text-slate-900">{selectedTemplate.team_lead_name}</strong>
          </div>
        </div>
      {/if}
    </section>

    <!-- Section 2: Unggah Tanda Tangan -->
    <section class="space-y-4">
      <div>
        <h3 class="text-sm font-bold text-slate-900">Unggah Berkas Tanda Tangan</h3>
        <p class="mt-0.5 text-xs text-slate-500">
          Gunakan format PNG atau JPG dengan latar belakang transparan (maks. 1 MB). Tanda tangan akan dirender pada footer sheet Excel.
        </p>
      </div>

      <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
        <SignatureUploader
          role="employee"
          label="Tanda Tangan Karyawan (Employee)"
          name={selectedTemplate?.employee_name || 'Aria Nur Jamal'}
          hasSignature={sigStatus.employee}
          onStatusChange={refresh}
        />

        <SignatureUploader
          role="team_lead"
          label="Tanda Tangan Team Lead"
          name={selectedTemplate?.team_lead_name || 'Kevin Saputra'}
          hasSignature={sigStatus.team_lead}
          onStatusChange={refresh}
        />
      </div>
    </section>
  {/if}
</div>
