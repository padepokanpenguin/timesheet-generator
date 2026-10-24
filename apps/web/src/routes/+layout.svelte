<script lang="ts">
  import '../app.css';
  import { page } from '$app/state';
  import { onMount } from 'svelte';
  import { getJiraStatus, connectJira, type JiraStatus } from '@timesheet/api-client';

  interface Props {
    children: any;
  }
  let { children }: Props = $props();

  let jiraStatus = $state<JiraStatus>({ connected: false, site_url: null, email: null, message: null });
  let isCheckingJira = $state(true);
  let showConnectModal = $state(false);

  // Jira Connect form
  let siteUrl = $state('https://perusahaan.atlassian.net');
  let email = $state('developer@example.com');
  let apiToken = $state('');
  let connectError = $state('');
  let isConnecting = $state(false);

  async function checkStatus() {
    try {
      jiraStatus = await getJiraStatus();
    } catch {
      jiraStatus = { connected: false, site_url: null, email: null, message: 'Gagal terhubung ke API backend' };
    } finally {
      isCheckingJira = false;
    }
  }

  onMount(() => {
    checkStatus();
  });

  async function handleConnectSubmit(e: SubmitEvent) {
    e.preventDefault();
    connectError = '';
    isConnecting = true;
    try {
      jiraStatus = await connectJira({
        site_url: siteUrl,
        email,
        api_token: apiToken
      });
      showConnectModal = false;
      apiToken = '';
    } catch (err) {
      connectError = err instanceof Error ? err.message : 'Koneksi ke Jira gagal.';
    } finally {
      isConnecting = false;
    }
  }
</script>

<div class="min-h-screen bg-slate-50 text-slate-900 font-sans">
  <!-- Top Navigation Bar (h-14) -->
  <header class="sticky top-0 z-30 flex h-14 border-b border-slate-200 bg-white shadow-2xs">
    <div class="mx-auto flex w-full max-w-7xl items-center justify-between px-4 sm:px-6">
      <!-- Left: Brand & Title -->
      <div class="flex items-center gap-3">
        <a href="/" class="flex items-center gap-2">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600 font-bold text-white shadow-xs">
            JT
          </div>
          <span class="text-sm font-bold tracking-tight text-slate-900">Jira Timesheet</span>
        </a>
        <span class="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-600">
          v0.2
        </span>
      </div>

      <!-- Center: Role-Aware Navigation Tabs -->
      <nav class="hidden md:flex items-center gap-1">
        <a
          href="/"
          class="rounded-md px-3 py-1.5 text-xs font-medium transition {page.url.pathname === '/' ? 'bg-primary-50 text-primary-700' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}"
        >
          Generator & Pratinjau
        </a>
        <a
          href="/profile"
          class="rounded-md px-3 py-1.5 text-xs font-medium transition {page.url.pathname === '/profile' ? 'bg-primary-50 text-primary-700' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}"
        >
          Profil & Tanda Tangan
        </a>
        <a
          href="/admin/templates"
          class="rounded-md px-3 py-1.5 text-xs font-medium transition {page.url.pathname.startsWith('/admin') ? 'bg-primary-50 text-primary-700' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}"
        >
          Template & Kalender Admin
        </a>
      </nav>

      <!-- Right: Jira Cloud Status -->
      <div class="flex items-center gap-3">
        {#if isCheckingJira}
          <span class="text-[11px] text-slate-400">Memeriksa koneksi Jira...</span>
        {:else if jiraStatus.connected}
          <div class="flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs text-emerald-800">
            <span class="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span class="font-medium">Jira: {jiraStatus.email || 'Connected'}</span>
          </div>
        {:else}
          <button
            type="button"
            onclick={() => (showConnectModal = true)}
            class="flex items-center gap-1.5 rounded-md bg-primary-600 px-3 py-1 text-xs font-medium text-white shadow-xs hover:bg-primary-700"
          >
            Hubungkan Jira
          </button>
        {/if}
      </div>
    </div>
  </header>

  <!-- Main Content Container -->
  <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6">
    {@render children()}
  </main>

  <!-- Connect Jira Modal -->
  {#if showConnectModal}
    <div
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
    >
      <button
        type="button"
        class="fixed inset-0 bg-slate-900/40 backdrop-blur-2xs"
        onclick={() => (showConnectModal = false)}
        aria-label="Tutup modal"
      ></button>

      <div class="relative z-10 w-full max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-200 pb-3">
          <h3 class="text-sm font-bold text-slate-900">Hubungkan Akun Jira Cloud</h3>
          <button
            type="button"
            onclick={() => (showConnectModal = false)}
            class="rounded p-1 text-slate-400 hover:bg-slate-100"
          >
            ✕
          </button>
        </div>

        <form onsubmit={handleConnectSubmit} class="mt-4 space-y-3 text-xs">
          <div>
            <label for="jira-site-url" class="block font-medium text-slate-700">Jira Site URL:</label>
            <input
              id="jira-site-url"
              type="url"
              bind:value={siteUrl}
              required
              class="mt-1 w-full rounded border border-slate-300 p-2 text-xs text-slate-900 focus:border-primary-500 focus:outline-hidden"
              placeholder="https://perusahaan.atlassian.net"
            />
          </div>

          <div>
            <label for="jira-email" class="block font-medium text-slate-700">Atlassian Email:</label>
            <input
              id="jira-email"
              type="email"
              bind:value={email}
              required
              class="mt-1 w-full rounded border border-slate-300 p-2 text-xs text-slate-900 focus:border-primary-500 focus:outline-hidden"
              placeholder="nama@perusahaan.com"
            />
          </div>

          <div>
            <label for="jira-api-token" class="block font-medium text-slate-700">Atlassian API Token:</label>
            <input
              id="jira-api-token"
              type="password"
              bind:value={apiToken}
              required
              class="mt-1 w-full rounded border border-slate-300 p-2 text-xs text-slate-900 focus:border-primary-500 focus:outline-hidden"
              placeholder="API Token dari Atlassian Account Security"
            />
          </div>

          {#if connectError}
            <p class="text-xs text-red-600">⚠ {connectError}</p>
          {/if}

          <div class="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onclick={() => (showConnectModal = false)}
              class="rounded border border-slate-300 px-3 py-1.5 text-slate-600 hover:bg-slate-50"
            >
              Batal
            </button>
            <button
              type="submit"
              disabled={isConnecting}
              class="rounded bg-primary-600 px-4 py-1.5 font-medium text-white shadow-xs hover:bg-primary-700 disabled:bg-slate-300"
            >
              {isConnecting ? 'Menghubungkan...' : 'Simpan & Hubungkan'}
            </button>
          </div>
        </form>
      </div>
    </div>
  {/if}
</div>
