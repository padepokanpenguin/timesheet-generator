<script lang="ts">
  import type { StoryEntry } from '@timesheet/api-client';
  import { detectTyposInText } from '$lib/utils/qualityChecker';

  interface Props {
    story: StoryEntry;
    onOpenProgress?: (storyKey: string) => void;
    onUpdateEpic?: (val: string) => void;
    onUpdateActivity?: (index: number, val: string) => void;
    onAddActivity?: (val: string) => void;
    onRemoveActivity?: (index: number) => void;
  }

  let {
    story,
    onOpenProgress = () => {},
    onUpdateEpic = (_val: string) => {},
    onUpdateActivity = (_index: number, _val: string) => {},
    onAddActivity = (_val: string) => {},
    onRemoveActivity = (_index: number) => {}
  }: Props = $props();

  let isEditingEpic = $state(false);
  let epicInput = $state('');

  let newActivityText = $state('');
  let isAddingActivity = $state(false);

  let editingActivityIndex = $state<number | null>(null);
  let activityInput = $state('');

  let titleTypos = $derived(detectTyposInText(story.title || ''));

  function handleSaveEpic() {
    if (epicInput.trim()) {
      onUpdateEpic(epicInput.trim());
    }
    isEditingEpic = false;
  }

  function handleAddActivitySubmit() {
    if (newActivityText.trim()) {
      onAddActivity(newActivityText.trim());
      newActivityText = '';
      isAddingActivity = false;
    }
  }

  function handleSaveActivity(index: number) {
    if (activityInput.trim()) {
      onUpdateActivity(index, activityInput.trim());
    }
    editingActivityIndex = null;
  }
</script>

<div class="group/story relative rounded border border-slate-200 bg-white p-2 text-xs shadow-2xs hover:border-slate-300">
  <div class="flex flex-wrap items-center gap-1.5 leading-snug">
    <!-- Epic Chip -->
    {#if story.epic}
      {#if isEditingEpic}
        <input
          type="text"
          bind:value={epicInput}
          onblur={handleSaveEpic}
          onkeydown={(e) => e.key === 'Enter' && handleSaveEpic()}
          class="rounded border border-primary-500 bg-white px-1.5 py-0.5 text-xs text-primary-900 focus:outline-hidden"
          placeholder="Nama Epic..."
        />
      {:else}
        <button
          type="button"
          onclick={() => {
            epicInput = story.epic || '';
            isEditingEpic = true;
          }}
          title="Klik untuk ubah label Epic"
          class="inline-flex cursor-pointer items-center rounded bg-primary-50 px-1.5 py-0.5 font-medium text-primary-700 hover:bg-primary-100"
        >
          [{story.epic}]
        </button>
      {/if}
    {:else}
      {#if isEditingEpic}
        <input
          type="text"
          bind:value={epicInput}
          onblur={handleSaveEpic}
          onkeydown={(e) => e.key === 'Enter' && handleSaveEpic()}
          class="rounded border border-red-500 bg-red-50 px-1.5 py-0.5 text-xs text-red-900 focus:outline-hidden"
          placeholder="Ketik Label Epic wajib..."
        />
      {:else}
        <button
          type="button"
          onclick={() => {
            epicInput = '';
            isEditingEpic = true;
          }}
          class="inline-flex cursor-pointer items-center rounded border border-dashed border-red-500 bg-red-50 px-1.5 py-0.5 font-medium text-red-700 hover:bg-red-100"
        >
          [+ Isi Label Epic Wajib]
        </button>
      {/if}
    {/if}

    <!-- Key & Title -->
    <span class="font-mono font-semibold text-slate-900">{story.key}:</span>
    <span class="text-slate-800 {titleTypos.length > 0 ? 'bg-amber-50 underline decoration-amber-500 decoration-wavy' : ''}">
      {story.title}
    </span>
    {#if titleTypos.length > 0}
      <span class="rounded bg-amber-100 px-1 text-[10px] text-amber-800" title={titleTypos.map((t) => `${t.word} -> ${t.suggestion}`).join(', ')}>
        ⚠ Typo: {titleTypos.map((t) => t.word).join(', ')}
      </span>
    {/if}

    <!-- Percentage Badge -->
    <button
      type="button"
      onclick={() => onOpenProgress(story.key)}
      title="Buka panel progres dan segmentasi"
      class="inline-flex cursor-pointer items-center rounded border border-slate-200 bg-slate-50 px-1.5 py-0.5 font-mono font-semibold text-slate-800 hover:border-primary-500 hover:bg-primary-50 hover:text-primary-700"
    >
      {#if story.percent !== null && story.percent !== undefined}
        ({story.percent}%)
      {:else}
        <span class="text-amber-600">(??%)</span>
      {/if}
    </button>
  </div>

  <!-- Sub-task Activities -->
  <div class="mt-1.5 space-y-1 pl-2">
    {#if story.activities.length === 0}
      <div class="flex items-center gap-2 text-amber-700">
        <span class="rounded bg-amber-50 px-1.5 py-0.5 text-[11px] font-medium text-amber-800">
          ⚠ Tanpa sub-task di Jira — isi aktivitas manual:
        </span>
      </div>
    {/if}

    {#each story.activities as act, idx}
      {@const actTypos = detectTyposInText(act)}
      <div class="flex items-center justify-between gap-1 text-slate-600 hover:text-slate-900">
        <div class="flex flex-1 items-center gap-1">
          <span class="text-slate-400">-</span>
          {#if editingActivityIndex === idx}
            <input
              type="text"
              bind:value={activityInput}
              onblur={() => handleSaveActivity(idx)}
              onkeydown={(e) => e.key === 'Enter' && handleSaveActivity(idx)}
              class="flex-1 rounded border border-primary-500 px-1 py-0.5 text-xs text-slate-900 focus:outline-hidden"
            />
          {:else}
            <button
              type="button"
              onclick={() => {
                editingActivityIndex = idx;
                activityInput = act;
              }}
              class="cursor-pointer text-left hover:underline {actTypos.length > 0 ? 'bg-amber-50 underline decoration-amber-500 decoration-wavy' : ''}"
              title="Klik untuk mengedit aktivitas"
            >
              {act}
            </button>
            {#if actTypos.length > 0}
              <span class="rounded bg-amber-100 px-1 text-[10px] text-amber-800" title={actTypos.map((t) => `${t.word} -> ${t.suggestion}`).join(', ')}>
                ⚠ Typo: {actTypos.map((t) => t.word).join(', ')}
              </span>
            {/if}
          {/if}
        </div>
        <button
          type="button"
          onclick={() => onRemoveActivity(idx)}
          title="Hapus aktivitas"
          class="opacity-0 group-hover/story:opacity-100 text-slate-400 hover:text-red-600"
        >
          ✕
        </button>
      </div>
    {/each}

    <!-- Add Activity Button/Input -->
    <div class="pt-0.5">
      {#if isAddingActivity}
        <div class="flex items-center gap-1">
          <input
            type="text"
            bind:value={newActivityText}
            onkeydown={(e) => e.key === 'Enter' && handleAddActivitySubmit()}
            placeholder="Tambah aktivitas sub-task..."
            class="flex-1 rounded border border-slate-300 px-1.5 py-0.5 text-xs text-slate-800 focus:border-primary-500 focus:outline-hidden"
          />
          <button
            type="button"
            onclick={handleAddActivitySubmit}
            class="rounded bg-primary-600 px-2 py-0.5 font-medium text-white hover:bg-primary-700"
          >
            Simpan
          </button>
          <button
            type="button"
            onclick={() => (isAddingActivity = false)}
            class="rounded px-1.5 py-0.5 text-slate-500 hover:bg-slate-100"
          >
            Batal
          </button>
        </div>
      {:else}
        <button
          type="button"
          onclick={() => (isAddingActivity = true)}
          class="text-[11px] text-primary-600 hover:text-primary-800 hover:underline"
        >
          + Tambah Sub-task Aktivitas
        </button>
      {/if}
    </div>
  </div>
</div>
