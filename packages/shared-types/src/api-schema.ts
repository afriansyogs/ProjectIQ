// HEALTH SCHEMAS
export interface HealthCheckResponse {
  status: string;
  service: string;
  ai_service_status: string;
}


// USER & WORKSPACE ENUMS & SCHEMAS
export enum UserRole {
  CTO = "CTO",
  PM = "PM",
  DEV = "DEV",
  LEAD = "LEAD",
}

export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string | null;
  avatar_url?: string | null;
  is_active: boolean;
  is_verified: boolean;
  role: UserRole;
  created_at: string;
  updated_at: string;
}

export enum WorkspaceMemberRole {
  ADMIN = "ADMIN",
  MEMBER = "MEMBER",
  GUEST = "GUEST",
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  description?: string | null;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceMember {
  id: string;
  workspace_id: string;
  user_id: string;
  role: WorkspaceMemberRole;
  created_at: string;
}


// WORK MANAGEMENT ENUMS & SCHEMAS
export interface Project {
  id: string;
  workspace_id: string;
  name: string;
  identifier: string;
  description?: string | null;
  lead_id?: string | null;
  created_at: string;
  updated_at: string;
}

export enum ModuleStatus {
  PLANNED = "PLANNED",
  IN_PROGRESS = "IN_PROGRESS",
  PAUSED = "PAUSED",
  COMPLETED = "COMPLETED",
  CANCELLED = "CANCELLED",
}

export interface Module {
  id: string;
  project_id: string;
  name: string;
  description?: string | null;
  status: ModuleStatus;
  lead_id?: string | null;
  start_date?: string | null;
  target_date?: string | null;
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export enum CycleStatus {
  DRAFT = "DRAFT",
  ACTIVE = "ACTIVE",
  COMPLETED = "COMPLETED",
}

export interface Cycle {
  id: string;
  project_id: string;
  name: string;
  description?: string | null;
  status: CycleStatus;
  start_date?: string | null;
  end_date?: string | null;
  created_at: string;
  updated_at: string;
}

export enum IssueType {
  TASK = "TASK",
  BUG = "BUG",
  FEATURE = "FEATURE",
  IMPROVEMENT = "IMPROVEMENT",
}

export enum IssueStatus {
  BACKLOG = "BACKLOG",
  TODO = "TODO",
  IN_PROGRESS = "IN_PROGRESS",
  IN_REVIEW = "IN_REVIEW",
  DONE = "DONE",
  CANCELLED = "CANCELLED",
}

export enum IssuePriority {
  URGENT = "URGENT",
  HIGH = "HIGH",
  MEDIUM = "MEDIUM",
  LOW = "LOW",
  NONE = "NONE",
}

export interface Issue {
  id: string;
  project_id: string;
  sequence_id: number;
  module_id?: string | null;
  cycle_id?: string | null;
  title: string;
  description?: string | null;
  issue_type: IssueType;
  status: IssueStatus;
  priority: IssuePriority;
  story_points?: number | null;
  assignee_id?: string | null;
  reporter_id: string;
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export enum ActivityType {
  CREATED = "CREATED",
  STATUS_CHANGE = "STATUS_CHANGE",
  ASSIGNEE_CHANGE = "ASSIGNEE_CHANGE",
  ESTIMATE_CHANGE = "ESTIMATE_CHANGE",
  COMMENT = "COMMENT",
}

export interface IssueActivity {
  id: string;
  issue_id: string;
  actor_id?: string | null;
  activity_type: ActivityType;
  old_value?: string | null;
  new_value?: string | null;
  comment?: string | null;
  created_at: string;
}


// KNOWLEDGE BASE & RBAC RAG SCHEMAS
export enum DocumentType {
  PRD = "PRD",
  BRD = "BRD",
  TECH_SPEC = "TECH_SPEC",
  API_DOC = "API_DOC",
  SOP = "SOP",
  GENERAL = "GENERAL",
}

export interface Document {
  id: string;
  workspace_id: string;
  project_id?: string | null;
  title: string;
  document_type: DocumentType;
  content_text: string;
  file_url?: string | null;
  file_size?: number | null;
  uploaded_by_id?: string | null;
  is_indexed: boolean;
  chunk_count: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentAccessRole {
  id: string;
  document_id: string;
  role: UserRole;
  created_at: string;
}

// RAG & AI COMMUNICATION DTOs
export interface SourceNode {
  document_id: string;
  title: string;
  chunk_index: number;
  text: string;
  score: number;
}

export interface DocumentIngestRequest {
  document_id: string;
  title: string;
  content: string;
  metadata?: Record<string, unknown>;
}

export interface DocumentIngestResponse {
  status: string;
  document_id: string;
  total_chunks: number;
  message: string;
}

export interface ChatQueryRequest {
  question: string;
  top_k?: number;
}

export interface ChatQueryResponse {
  answer: string;
  sources: SourceNode[];
  model_used: string;
}
