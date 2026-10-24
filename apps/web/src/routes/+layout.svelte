<script lang="ts">
  import '../app.css';
  import { page } from '$app/state';
  import { onMount } from 'svelte';
  import { getAuthMe, login, logout, type UserPublic } from '@timesheet/api-client';

  interface Props {
    children: any;
  }
  let { children }: Props = $props();

  let currentUser = $state<UserPublic | null>(null);
  let isCheckingAuth = $state(true);
  let showLoginModal = $state(false);

  // Login form state
  let loginUsernameOrEmail = $state('');
  let loginPassword = $state('');
  let loginError = $state('');
  let isLoggingIn = $state(false);

  async function checkUserAuth() {
    try {
      currentUser = await getAuthMe();
    } catch {
      currentUser = null;
    } finally {
      isCheckingAuth = false;
    }
  }

  onMount(() => {
    checkUserAuth();
  });

  async function handleLoginSubmit(e: SubmitEvent) {
    e.preventDefault();
    loginError = '';
    isLoggingIn = true;
    try {
      const res = await login({
        username_or_email: loginUsernameOrEmail,
        password: loginPassword
      });
      currentUser = res.user;
      showLoginModal = false;
      loginPassword = '';
      window.location.reload();
    } catch (err) {
      loginError = err instanceof Error ? err.message : 'Login gagal. Akun dibuat dan dikelola oleh Admin.';
    } finally {
      isLoggingIn = false;
    }
  }

  async function handleLogout() {
    await logout();
    currentUser = null;
    window.location.reload();
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
        {#if currentUser && currentUser.role === 'admin'}
          <a
            href="/admin/templates"
            class="rounded-md px-3 py-1.5 text-xs font-medium transition {page.url.pathname === '/admin/templates' ? 'bg-primary-50 text-primary-700' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}"
          >
            Template & Kalender Admin
          </a>
          <a
            href="/admin/users"
            class="rounded-md px-3 py-1.5 text-xs font-medium transition {page.url.pathname === '/admin/users' ? 'bg-primary-50 text-primary-700' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}"
          >
            Kelola Akun Pengguna
          </a>
        {/if}
      </nav>

      <!-- Right: User Session / Login Status -->
      <div class="flex items-center gap-3">
        {#if isCheckingAuth}
          <span class="text-[11px] text-slate-400">Memeriksa sesi...</span>
        {:else if currentUser}
          <div class="flex items-center gap-2">
            <div class="flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs text-emerald-800">
              <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
              <span class="font-medium" title={currentUser.email}>
                {currentUser.display_name}
              </span>
              <span class="rounded bg-emerald-100 px-1 text-[10px] uppercase font-semibold text-emerald-800">
                {currentUser.role}
              </span>
            </div>
            <button
              type="button"
              onclick={handleLogout}
              class="rounded border border-slate-200 bg-white px-2 py-1 text-[11px] text-slate-600 shadow-2xs hover:bg-slate-50 hover:text-red-600"
              title="Keluar dari akun"
            >
              Logout
            </button>
          </div>
        {:else}
          <button
            type="button"
            onclick={() => (showLoginModal = true)}
            class="flex items-center gap-1.5 rounded-md bg-primary-600 px-3.5 py-1.5 text-xs font-medium text-white shadow-xs hover:bg-primary-700"
          >
            Login dengan Jira
          </button>
        {/if}
      </div>
    </div>
  </header>

  <!-- Main Content Container -->
  <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6">
    {@render children()}
  </main>

  <!-- Login Modal (Hanya login, akun dibuat oleh admin) -->
  {#if showLoginModal}
    <div
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
    >
      <button
        type="button"
        class="fixed inset-0 bg-slate-900/40 backdrop-blur-2xs"
        onclick={() => (showLoginModal = false)}
        aria-label="Tutup modal"
      ></button>

      <div class="relative z-10 w-full max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-200 pb-3">
          <div>
            <h3 class="text-sm font-bold text-slate-900">Login Pengguna Jira Timesheet</h3>
            <p class="text-[11px] text-slate-500">Akun pengguna dibuat dan dikelola oleh Admin.</p>
          </div>
          <button
            type="button"
            onclick={() => (showLoginModal = false)}
            class="rounded p-1 text-slate-400 hover:bg-slate-100"
          >
            ✕
          </button>
        </div>

        <form onsubmit={handleLoginSubmit} class="mt-4 space-y-3.5 text-xs">
          <div>
            <label for="login-username" class="block font-medium text-slate-700">Username atau Email Jira:</label>
            <input
              id="login-username"
              type="text"
              bind:value={loginUsernameOrEmail}
              required
              class="mt-1 w-full rounded border border-slate-300 p-2 text-xs text-slate-900 focus:border-primary-500 focus:outline-hidden"
              placeholder="misal: admin atau developer"
            />
          </div>

          <div>
            <label for="login-password" class="block font-medium text-slate-700">Password:</label>
            <input
              id="login-password"
              type="password"
              bind:value={loginPassword}
              required
              class="mt-1 w-full rounded border border-slate-300 p-2 text-xs text-slate-900 focus:border-primary-500 focus:outline-hidden"
              placeholder="Masukkan password akun Anda"
            />
          </div>

          <div class="rounded-lg bg-slate-50 p-2.5 text-[11px] text-slate-500">
            <span class="font-medium text-slate-700">Akun bawaan sistem:</span>
            <ul class="mt-1 list-disc pl-4 space-y-0.5">
              <li><strong>admin</strong> / password: <code>admin123</code> (Admin PMO)</li>
              <li><strong>developer</strong> / password: <code>dev123</code> (Developer)</li>
            </ul>
          </div>

          {#if loginError}
            <p class="text-xs text-red-600">⚠ {loginError}</p>
          {/if}

          <div class="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onclick={() => (showLoginModal = false)}
              class="rounded border border-slate-300 px-3.5 py-1.5 text-slate-600 hover:bg-slate-50"
            >
              Batal
            </button>
            <button
              type="submit"
              disabled={isLoggingIn}
              class="rounded bg-primary-600 px-4 py-1.5 font-medium text-white shadow-xs hover:bg-primary-700 disabled:bg-slate-300"
            >
              {isLoggingIn ? 'Memeriksa...' : 'Login'}
            </button>
          </div>
        </form>
      </div>
    </div>
  {/if}
</div>
