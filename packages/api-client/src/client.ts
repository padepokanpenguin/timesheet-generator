import type {
  FormulaSimulateRequest,
  FormulaSimulateResponse,
  JiraConnectRequest,
  JiraStatus,
  PreviewRequest,
  SignatureStatus,
  TemplateSpec,
  TemplateSpecInput,
  TimesheetDraft
} from './types';

let baseUrl = '/api';

/** Ubah base URL (default `/api`, diproksi oleh Vite/hooks.server.ts). */
export function configureApi(options: { baseUrl: string }): void {
  baseUrl = options.baseUrl.replace(/\/$/, '');
}

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(typeof body.detail === 'string' ? body.detail : `Permintaan gagal (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export const listTemplates = (): Promise<TemplateSpec[]> =>
  fetch(`${baseUrl}/templates`).then((r) => json<TemplateSpec[]>(r));

export const getTemplate = (id: string): Promise<TemplateSpec> =>
  fetch(`${baseUrl}/templates/${id}`).then((r) => json<TemplateSpec>(r));

export const createTemplate = (template: TemplateSpecInput): Promise<TemplateSpec> =>
  fetch(`${baseUrl}/templates`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(template)
  }).then((r) => json<TemplateSpec>(r));

export const updateTemplate = (id: string, template: TemplateSpecInput): Promise<TemplateSpec> =>
  fetch(`${baseUrl}/templates/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(template)
  }).then((r) => json<TemplateSpec>(r));

export const deleteTemplate = async (id: string): Promise<void> => {
  const res = await fetch(`${baseUrl}/templates/${id}`, { method: 'DELETE' });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(typeof body.detail === 'string' ? body.detail : 'Hapus template gagal');
  }
};

export const previewTimesheet = (body: PreviewRequest): Promise<TimesheetDraft> =>
  fetch(`${baseUrl}/timesheet/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  }).then((r) => json<TimesheetDraft>(r));

/** Mengunduh .xlsx dari draf yang sudah diedit. */
export async function generateTimesheet(draft: TimesheetDraft): Promise<void> {
  const res = await fetch(`${baseUrl}/timesheet/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ draft })
  });
  if (!res.ok) throw new Error(`Generate gagal (${res.status})`);
  const name = /filename="([^"]+)"/.exec(res.headers.get('Content-Disposition') ?? '')?.[1] ?? 'TimeSheet.xlsx';
  const url = URL.createObjectURL(await res.blob());
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

export const getSignatureStatus = (): Promise<SignatureStatus> =>
  fetch(`${baseUrl}/signatures`).then((r) => json<SignatureStatus>(r));

export async function uploadSignature(role: 'employee' | 'team_lead', file: File): Promise<void> {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${baseUrl}/signatures/${role}`, { method: 'POST', body: form });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(typeof body.detail === 'string' ? body.detail : 'Upload gagal');
  }
}

export async function deleteSignature(role: 'employee' | 'team_lead'): Promise<void> {
  const res = await fetch(`${baseUrl}/signatures/${role}`, { method: 'DELETE' });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(typeof body.detail === 'string' ? body.detail : 'Hapus tanda tangan gagal');
  }
}

export const getJiraStatus = (): Promise<JiraStatus> =>
  fetch(`${baseUrl}/jira/status`).then((r) => json<JiraStatus>(r));

export const connectJira = (req: JiraConnectRequest): Promise<JiraStatus> =>
  fetch(`${baseUrl}/jira/connect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req)
  }).then((r) => json<JiraStatus>(r));

export const simulateFormula = (req: FormulaSimulateRequest): Promise<FormulaSimulateResponse> =>
  fetch(`${baseUrl}/formula/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req)
  }).then((r) => json<FormulaSimulateResponse>(r));
