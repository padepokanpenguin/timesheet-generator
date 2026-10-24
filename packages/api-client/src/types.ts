import type { components } from './schema';

type Schemas = components['schemas'];

export type TimesheetDraft = Schemas['TimesheetDraft-Output'];
export type DayRow = Schemas['DayRow-Output'];
export type StoryEntry = Schemas['StoryEntry-Output'];
export type StoryState = Schemas['StoryState-Output'];
export type TemplateSpec = Schemas['TemplateSpec-Output'];
export type TemplateSpecInput = Schemas['TemplateSpec-Input'];
export type FormulaConfig = Schemas['FormulaConfig-Output'];
export type FormulaConfigInput = Schemas['FormulaConfig-Input'];
export type PreviewRequest = Schemas['PreviewRequest'];
export type GenerateRequest = Schemas['GenerateRequest'];
export type SignatureStatus = Schemas['SignatureStatus'];
export type JiraStatus = Schemas['JiraStatus'];
export type JiraConnectRequest = Schemas['JiraConnectRequest'];
export type FormulaSimulateRequest = Schemas['FormulaSimulateRequest'];
export type FormulaSimulateResponse = Schemas['FormulaSimulateResponse'];
export type LoginRequest = Schemas['LoginRequest'];
export type AuthResponse = Schemas['AuthResponse'];
export type UserPublic = Schemas['UserPublic'];
export type UserAccountCreate = Schemas['UserAccountCreate'];
export type UserAccountUpdate = Schemas['UserAccountUpdate'];
export type RowKind = DayRow['kind'];
