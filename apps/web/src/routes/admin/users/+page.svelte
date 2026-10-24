<script lang="ts">
  import { onMount } from 'svelte';
  import {
    adminListUsers,
    adminCreateUser,
    adminUpdateUser,
    adminDeleteUser,
    getAuthMe,
    listTemplates,
    type UserPublic,
    type UserAccountCreate,
    type TemplateSpec
  } from '@timesheet/api-client';

  let currentUser = $state<UserPublic | null>(null);
  let users = $state<UserPublic[]>([]);
  let templates = $state<TemplateSpec[]>([]);
  let loading = $state(true);
  let error = $state('');
  let notice = $state('');

  let showModal = $state(false);
  let isEditing = $state(false);
  let editingId = $state('');

  // Form State
  let formUsername = $state('');
  let formEmail = $state('');
  let formDisplayName = $state('');
  let formPassword = $state('');
  let formRole = $state<'developer' | 'team_lead' | 'admin'>('developer');
  let formTemplateId = $state('default-id');
  let formJiraSiteUrl = $state('https://perusahaan.atlassian.net');
  let formJiraApiToken = $state('');

  async function loadData() {
    try {
      loading = true;
      error = '';
      currentUser = await getAuthMe().catch(() => null);
      if (!currentUser || currentUser.role !== 'admin') {
        error = 'Halaman ini khusus untuk Admin. Silakan login sebagai Admin.';
        return;
      }
      users = await adminListUsers();
      templates = await listTemplates();
    } catch (e) {
      error = (e as Error).message;
    } finally {
      loading = false;
    }
  }

  function openCreateModal() {
    isEditing = false;
    editingId = '';
    formUsername = '';
    formEmail = '';
    formDisplayName = '';
    formPassword = '';
    formRole = 'developer';
    formTemplateId = templates[0]?.id || 'default-id';
    formJiraSiteUrl = 'https://perusahaan.atlassian.net';
    formJiraApiToken = '';
    showModal = true;
  }

  function openEditModal(u: UserPublic) {
    isEditing = true;
    editingId = u.id;
    formUsername = u.username;
    formEmail = u.email;
    formDisplayName = u.display_name;
    formPassword = '';
    formRole = u.role;
    formTemplateId = u.template_id;
    formJiraSiteUrl = u.jira_site_url;
    formJiraApiToken = '';
    showModal = true;
  }

  async function handleSaveAccount(e: SubmitEvent) {
    e.preventDefault();
    error = '';
    notice = '';
    try {
      if (isEditing) {
        await adminUpdateUser(editingId, {
          email: formEmail,
          display_name: formDisplayName,
          password: formPassword || undefined,
          role: formRole,
          template_id: formTemplateId,
          jira_site_url: formJiraSiteUrl,
          jira_api_token: formJiraApiToken || undefined
        });
        notice = `Akun '${formDisplayName}' berhasil diperbarui!`;
      } else {
        const payload: UserAccountCreate = {
          username: formUsername,
          email: formEmail,
          display_name: formDisplayName,
          password: formPassword,
          role: formRole,
          template_id: formTemplateId,
          jira_site_url: formJiraSiteUrl,
          jira_api_token: formJiraApiToken
        };
        await adminCreateUser(payload);
        notice = `Akun '${formDisplayName}' berhasil dibuat!`;
      }
      showModal = false;
      await loadData();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Gagal menyimpan akun.';
    }
  }

  async function handleDelete(u: UserPublic) {
    if (!confirm(`Hapus akun '${u.display_name}' (${u.username})?`)) return;
    try {
      await adminDeleteUser(u.id);
      notice = `Akun '${u.display_name}' berhasil dihapus.`;
      await loadData();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Gagal menghapus akun.';
    }
  }

  onMount(() => {
    loadData();
  });
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between border-b border-slate-200 pb-4">
    <div>
      <h2 class="text-lg font-bold text-slate-900">Kelola Akun Pengguna (Khusus Admin)</h2>
      <p class="text-xs text-slate-500">
        Buat dan kelola akun pengguna/developer. Pengguna hanya dapat login menggunakan akun yang didaftarkan di sini.
      </p>
    </div>
    {#if currentUser && currentUser.role === 'admin'}
      <button
        type="button"
        onclick={openCreateModal}
        class="rounded-lg bg-primary-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-xs hover:bg-primary-700"
      >
        + Buat Akun Baru
      </button>
    {/if}
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

  {#if loading}
    <p class="py-12 text-center text-xs text-slate-400">Memuat data pengguna...</p>
  {:else if currentUser && currentUser.role === 'admin'}
    <!-- Tabel Pengguna -->
    <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xs">
      <div class="overflow-x-auto">
        <table class="w-full border-collapse text-left text-xs">
          <thead>
            <tr class="bg-slate-900 text-white font-medium">
              <th class="py-2.5 px-3">Username</th>
              <th class="py-2.5 px-3">Nama Lengkap di Timesheet</th>
              <th class="py-2.5 px-3">Email Akun Jira</th>
              <th class="py-2.5 px-3 text-center">Peran (Role)</th>
              <th class="py-2.5 px-3 text-center">Template ID</th>
              <th class="py-2.5 px-3 text-center">Jira Token</th>
              <th class="py-2.5 px-3 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200">
            {#each users as u}
              <tr class="hover:bg-slate-50 transition-colors">
                <td class="py-3 px-3 font-mono font-semibold text-slate-900">{u.username}</td>
                <td class="py-3 px-3 text-slate-800 font-medium">{u.display_name}</td>
                <td class="py-3 px-3 text-slate-600 font-mono">{u.email}</td>
                <td class="py-3 px-3 text-center">
                  <span class="rounded px-2 py-0.5 text-[10px] font-bold uppercase {u.role === 'admin' ? 'bg-purple-100 text-purple-800' : u.role === 'team_lead' ? 'bg-blue-100 text-blue-800' : 'bg-slate-100 text-slate-700'}">
                    {u.role}
                  </span>
                </td>
                <td class="py-3 px-3 text-center font-mono text-slate-500">{u.template_id}</td>
                <td class="py-3 px-3 text-center">
                  {#if u.has_api_token}
                    <span class="rounded bg-emerald-50 px-2 py-0.5 text-[11px] font-medium text-emerald-700">
                      ✓ Dikonfigurasi
                    </span>
                  {:else}
                    <span class="rounded bg-amber-50 px-2 py-0.5 text-[11px] font-medium text-amber-700">
                      Belum Diisi
                    </span>
                  {/if}
                </td>
                <td class="py-3 px-3 text-right space-x-2">
                  <button
                    type="button"
                    onclick={() => openEditModal(u)}
                    class="text-primary-600 hover:text-primary-800 hover:underline font-medium"
                  >
                    Edit
                  </button>
                  {#if u.id !== 'admin'}
                    <button
                      type="button"
                      onclick={() => handleDelete(u)}
                      class="text-red-600 hover:text-red-800 hover:underline font-medium"
                    >
                      Hapus
                    </button>
                  {/if}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {/if}

  <!-- Modal Buat / Edit Akun -->
  {#if showModal}
    <div
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
    >
      <button
        type="button"
        class="fixed inset-0 bg-slate-900/40 backdrop-blur-2xs"
        onclick={() => (showModal = false)}
        aria-label="Tutup modal"
      ></button>

      <div class="relative z-10 w-full max-w-lg rounded-xl border border-slate-200 bg-white p-6 shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-200 pb-3">
          <h3 class="text-base font-bold text-slate-900">
            {isEditing ? `Edit Akun: ${formDisplayName}` : 'Buat Akun Pengguna Baru'}
          </h3>
          <button
            type="button"
            onclick={() => (showModal = false)}
            class="rounded p-1 text-slate-400 hover:bg-slate-100"
          >
            ✕
          </button>
        </div>

        <form onsubmit={handleSaveAccount} class="mt-4 space-y-3.5 text-xs">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label for="acc-username" class="block font-medium text-slate-700">Username Login:</label>
              <input
                id="acc-username"
                type="text"
                bind:value={formUsername}
                disabled={isEditing}
                required
                class="mt-1 w-full rounded border border-slate-300 p-2 font-mono disabled:bg-slate-100"
                placeholder="misal: aria.jamal"
              />
            </div>
            <div>
              <label for="acc-password" class="block font-medium text-slate-700">
                Password Login {isEditing ? '(Kosongkan jika tidak diubah)' : ':'}
              </label>
              <input
                id="acc-password"
                type="password"
                bind:value={formPassword}
                required={!isEditing}
                class="mt-1 w-full rounded border border-slate-300 p-2"
                placeholder={isEditing ? '••••••••' : 'Password login user'}
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label for="acc-display-name" class="block font-medium text-slate-700">Nama Lengkap (di Timesheet):</label>
              <input
                id="acc-display-name"
                type="text"
                bind:value={formDisplayName}
                required
                class="mt-1 w-full rounded border border-slate-300 p-2"
                placeholder="Contoh: Aria Nur Jamal"
              />
            </div>
            <div>
              <label for="acc-email" class="block font-medium text-slate-700">Email Akun Jira:</label>
              <input
                id="acc-email"
                type="email"
                bind:value={formEmail}
                required
                class="mt-1 w-full rounded border border-slate-300 p-2 font-mono"
                placeholder="nama@perusahaan.com"
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label for="acc-role" class="block font-medium text-slate-700">Peran Akun:</label>
              <select
                id="acc-role"
                bind:value={formRole}
                class="mt-1 w-full rounded border border-slate-300 p-2"
              >
                <option value="developer">Developer / Karyawan</option>
                <option value="team_lead">Team Lead</option>
                <option value="admin">Admin / PMO</option>
              </select>
            </div>
            <div>
              <label for="acc-template" class="block font-medium text-slate-700">Template Perusahaan:</label>
              <select
                id="acc-template"
                bind:value={formTemplateId}
                class="mt-1 w-full rounded border border-slate-300 p-2"
              >
                {#each templates as t}
                  <option value={t.id}>{t.name} ({t.company_name})</option>
                {/each}
              </select>
            </div>
          </div>

          <div>
            <label for="acc-jira-site" class="block font-medium text-slate-700">URL Situs Jira Cloud:</label>
            <input
              id="acc-jira-site"
              type="url"
              bind:value={formJiraSiteUrl}
              required
              class="mt-1 w-full rounded border border-slate-300 p-2 font-mono"
              placeholder="https://perusahaan.atlassian.net"
            />
          </div>

          <div>
            <label for="acc-api-token" class="block font-medium text-slate-700">
              Atlassian API Token Jira User {isEditing ? '(Kosongkan jika tidak diubah)' : ':'}:
            </label>
            <input
              id="acc-api-token"
              type="password"
              bind:value={formJiraApiToken}
              class="mt-1 w-full rounded border border-slate-300 p-2 font-mono"
              placeholder="Token API dari akun Atlassian user"
            />
            <p class="mt-1 text-[11px] text-slate-500">
              Dengan mengisikan API token ini, developer tidak perlu repot menginput API token lagi saat login.
            </p>
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onclick={() => (showModal = false)}
              class="rounded border border-slate-300 px-3.5 py-1.5 text-slate-600 hover:bg-slate-50"
            >
              Batal
            </button>
            <button
              type="submit"
              class="rounded bg-primary-600 px-4 py-1.5 font-medium text-white shadow-xs hover:bg-primary-700"
            >
              {isEditing ? 'Simpan Perubahan' : 'Buat Akun'}
            </button>
          </div>
        </form>
      </div>
    </div>
  {/if}
</div>
