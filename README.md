# Jira Timesheet Auto-Generator (monorepo)

Menarik sub-task dari story Jira Cloud, menghitung persentase progres, dan menghasilkan `.xlsx`
dengan layout identik template referensi. Spesifikasi lengkap: [`docs/prd.md`](docs/prd.md),
rencana pengembangan: [`docs/development-plan.md`](docs/development-plan.md).

## Arsitektur

```
apps/
  api/                 FastAPI: routing, konfigurasi, upload tanda tangan
  web/                 SvelteKit + Tailwind: pilih bulan -> pratinjau editable -> generate
packages/
  timesheet-core/      (Python) skema, hari aktif, persentase, builder draf, renderer openpyxl, template JSON
  jira-client/         (Python) klien Jira Cloud REST v3 (httpx, pagination, retry 429)
  api-client/          (TypeScript) klien fetch + tipe yang DI-GENERATE dari OpenAPI backend
infra/docker/          Dockerfile api & web (build context = root repo)
docs/                  PRD dan development plan
```

Arah dependensi (tidak boleh berbalik):

```
web ──► api-client ──(OpenAPI)──► api ──► jira-client ──► timesheet-core
                                    └──────────────────────────────────┘
```

- `timesheet-core` murni (tanpa HTTP/FastAPI) sehingga bisa dipakai API, worker antrean, atau CLI.
- Kontrak FE–BE satu sumber: skema Pydantic -> `openapi.json` -> `packages/api-client/src/schema.d.ts`.
  Setelah mengubah skema/route backend jalankan `pnpm gen:api` (CI menolak bila lupa).
- Tooling: **uv workspace** untuk Python, **pnpm workspace + Turborepo** untuk JS/TS.

## Mulai cepat

Prasyarat: Python 3.12+, [uv](https://docs.astral.sh/uv/), Node 22+, pnpm.

```bash
make install            # uv sync --all-packages && pnpm install
cp .env.example .env    # JIRA_MOCK=true: data contoh, tanpa Jira
make dev-api            # http://localhost:8000/docs
make dev-web            # http://localhost:5173
make test               # 23 tes Python
make check build        # svelte-check + build web
make up                 # atau semuanya via Docker Compose (web :3000, api :8000)
```

## Perintah penting

| Tujuan | Perintah |
|---|---|
| Tes Python | `uv run --all-packages pytest` |
| Lint/format | `make lint` / `make format` |
| Regenerasi tipe TS dari OpenAPI | `pnpm gen:api` |
| Type-check web | `pnpm check` |
| Build web | `pnpm build` |

## Memakai Jira sungguhan

1. Isi `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, set `JIRA_MOCK=false` di `.env`.
2. Cek ID field Story Points (`/rest/api/3/field`) lalu isi `JIRA_STORY_POINTS_FIELD`.
3. Story harus punya sub-task, Original Estimate (atau Story Points), dan Epic induk.

## Aturan inti (ringkas)

- Hari aktif = hari kerja dengan aktivitas user di sub-task (changelog); akhir pekan/libur/cuti diabaikan.
- Persentase kumulatif: Done = 100%, belum Done = hari aktif ÷ estimasi (maks 95%); dibagi acak berseed
  (kelipatan 5%, minimal 5%/hari) atau diinput manual; lintas bulan melanjutkan persentase sebelumnya.
- Story tanpa Epic: label wajib manual. Story tanpa sub-task: peringatan, aktivitas kosong.
- Working Hour ditulis sebagai angka (openpyxl tidak menghitung rumus).