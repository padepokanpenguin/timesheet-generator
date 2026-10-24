import type {
  AuthResponse,
  FormulaSimulateRequest,
  FormulaSimulateResponse,
  JiraConnectRequest,
  JiraStatus,
  LoginRequest,
  PreviewRequest,
  SignatureStatus,
  TemplateSpec,
  TemplateSpecInput,
  TimesheetDraft,
  UserAccountCreate,
  UserAccountUpdate,
  UserPublic
} from './types';

let baseUrl = '/api';
let authToken: string | null = null;

/** Ubah base URL (default `/api`, diproksi oleh Vite/hooks.server.ts). */
export function configureApi(options: { baseUrl: string }): void {
  baseUrl = options.baseUrl.replace(/\/$/, '');
}

export function setAuthToken(token: string | null): void {
  authToken = token;
  if (typeof window !== 'undefined') {
    if (token) {
      localStorage.setItem('jira_session_token', token);
    } else {
      localStorage.removeItem('jira_session_token');
    }
  }
}

export function getAuthToken(): string | null {
  if (!authToken && typeof window !== 'undefined') {
    authToken = localStorage.getItem('jira_session_token');
  }
  return authToken;
}

function authHeaders(existing?: Record<string, string>): Record<string, string> {
  const token = getAuthToken();
  const h: Record<string, string> = { ...(existing || {}) };
  if (token) {
    h['Authorization'] = `Bearer ${token}`;
  }
  return h;
}

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(typeof body.detail === 'string' ? body.detail : `Permintaan gagal (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export const listTemplates = (): Promise<TemplateSpec[]> =>
  fetch(`${baseUrl}/templates`, { headers: authHeaders() }).then((r) => json<TemplateSpec[]>(r));

export const getTemplate = (id: string): Promise<TemplateSpec> =>
  fetch(`${baseUrl}/templates/${id}`, { headers: authHeaders() }).then((r) => json<TemplateSpec>(r));

export const createTemplate = (template: TemplateSpecInput): Promise<TemplateSpec> =>
  fetch(`${baseUrl}/templates`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(template)
  }).then((r) => json<TemplateSpec>(r));

export const updateTemplate = (id: string, template: TemplateSpecInput): Promise<TemplateSpec> =>
  fetch(`${baseUrl}/templates/${id}`, {
    method: 'PUT',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(template)
  }).then((r) => json<TemplateSpec>(r));

export const deleteTemplate = async (id: string): Promise<void> => {
  const res = await fetch(`${baseUrl}/templates/${id}`, {
    method: 'DELETE',
    headers: authHeaders()
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(typeof body.detail === 'string' ? body.detail : 'Hapus template gagal');
  }
};

export const previewTimesheet = (body: PreviewRequest): Promise<TimesheetDraft> =>
  fetch(`${baseUrl}/timesheet/preview`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(body)
  }).then((r) => json<TimesheetDraft>(r));

/** Mengunduh .xlsx dari draf yang sudah diedit. */
export async function generateTimesheet(draft: TimesheetDraft): Promise<void> {
  const res = await fetch(`${baseUrl}/timesheet/generate`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
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
  fetch(`${baseUrl}/signatures`, { headers: authHeaders() }).then((r) => json<SignatureStatus>(r));

export async function uploadSignature(role: 'employee' | 'team_lead', file: File): Promise<void> {
  const form = new FormData();
  form.append('file', file);
  const headers = authHeaders();
  const res = await fetch(`${baseUrl}/signatures/${role}`, {
    method: 'POST',
    headers,
    body: form
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(typeof body.detail === 'string' ? body.detail : 'Upload gagal');
  }
}

export async function deleteSignature(role: 'employee' | 'team_lead'): Promise<void> {
  const res = await fetch(`${baseUrl}/signatures/${role}`, {
    method: 'DELETE',
    headers: authHeaders()
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(typeof body.detail === 'string' ? body.detail : 'Hapus tanda tangan gagal');
  }
}

export const getJiraStatus = (): Promise<JiraStatus> =>
  fetch(`${baseUrl}/jira/status`, { headers: authHeaders() }).then((r) => json<JiraStatus>(r));

export async function connectJira(req: JiraConnectRequest): Promise<JiraStatus> {
  const status = await fetch(`${baseUrl}/jira/connect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req)
  }).then((r) => json<JiraStatus>(r));

  if (status.token) {
    setAuthToken(status.token);
  }
  return status;
}

export async function logout(): Promise<void> {
  try {
    await fetch(`${baseUrl}/auth/logout`, {
      method: 'POST',
      headers: authHeaders()
    });
  } finally {
    setAuthToken(null);
  }
}

export const simulateFormula = (req: FormulaSimulateRequest): Promise<FormulaSimulateResponse> =>
  fetch(`${baseUrl}/formula/simulate`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(req)
  }).then((r) => json<FormulaSimulateResponse>(r));

export async function login(req: LoginRequest): Promise<AuthResponse> {
  const res = await fetch(`${baseUrl}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req)
  }).then((r) => json<AuthResponse>(r));

  if (res.token) {
    setAuthToken(res.token);
  }
  return res;
}

export const getAuthMe = (): Promise<UserPublic> =>
  fetch(`${baseUrl}/auth/me`, { headers: authHeaders() }).then((r) => json<UserPublic>(r));

export const adminListUsers = (): Promise<UserPublic[]> =>
  fetch(`${baseUrl}/admin/users`, { headers: authHeaders() }).then((r) => json<UserPublic[]>(r));

export const adminCreateUser = (data: UserAccountCreate): Promise<UserPublic> =>
  fetch(`${baseUrl}/admin/users`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(data)
  }).then((r) => json<UserPublic>(r));

export const adminUpdateUser = (userId: string, data: UserAccountUpdate): Promise<UserPublic> =>
  fetch(`${baseUrl}/admin/users/${userId}`, {
    method: 'PUT',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(data)
  }).then((r) => json<UserPublic>(r));

export const adminDeleteUser = async (userId: string): Promise<void> => {
  const res = await fetch(`${baseUrl}/admin/users/${userId}`, {
    method: 'DELETE',
    headers: authHeaders()
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(typeof body.detail === 'string' ? body.detail : 'Hapus akun gagal');
  }
};
