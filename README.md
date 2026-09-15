# ProjectIQ — AI-Powered Project Tracking & Knowledge Intelligence Platform

> **Modern Jira / Plane Alternative featuring Role-Based Context-Aware RAG and Verifiable Executive AI Performance Analytics.**

---

## 📌 Executive Overview

**ProjectIQ** adalah platform kolaborasi dan manajemen proyek modern (seperti Jira / Plane) yang diintegrasikan secara mendalam dengan sistem kecerdasan buatan (**Retrieval-Augmented Generation / RAG**). 

Platform ini memecahkan hambatan komunikasi tradisional antar peran (*silos* antara Developer, Product Manager, dan Eksekutif/CTO) dengan menghadirkan:
1. **Pusat Pengetahuan Kontekstual Berbasis Hak Akses (Role-Based RAG)**: Akses instan ke PRD, BRD, dokumentasi teknis, dan arsitektur tanpa perlu saling menunggu respon manual.
2. **Kecerdasan Kinerja Eksekutif (AI Performance Analytics)**: Kemampuan bagi pimpinan (CTO/VP/Manager) untuk menganalisis dan menanyakan progres tim serta membuktikan siapa saja yang sedang berkinerja tinggi berbasis bukti nyata (*verifiable evidence* dari tiket, modul, dan aktivitas kerja).

---

## 🎯 Masalah yang Diselesaikan (The Core Problems)

| Masalah Tradisional | Solusi ProjectIQ |
| :--- | :--- |
| **Dev menunggu PM**: Developer bingung aturan bisnis atau spek PRD/BRD, harus menunggu rapat atau chat PM. | **Instant RAG**: Dev bertanya ke AI *"Bagaimana aturan validasi transaksi di PRD fitur Checkout?"* dan AI langsung menjawab dari dokumen resmi. |
| **PM menunggu Dev**: PM butuh kepastian endpoint atau dokumentasi teknis implementasi. | **Instant Tech Docs RAG**: PM bertanya ke AI *"Bagaimana arsitektur auth service saat ini?"* dan dijawab langsung dari Tech Specs. |
| **Dokumen Rahasia & Izin Akses**: Tidak semua dokumen boleh diakses oleh semua pihak (misal dokumen finansial/strategis vs teknis). | **Role-Based Document Access (RBAC)**: Setiap dokumen dikunci per-role. AI hanya mengambil referensi dari dokumen yang diizinkan untuk role penanya. |
| **Pelaporan Kinerja Subjektif**: CTO/Manajemen kesulitan mengetahui siapa yang benar-benar produktif tanpa micromanagement. | **Verifiable AI Performance Audit**: Pimpinan bisa bertanya ke AI *"Siapa saja yang perform minggu ini?"* dan AI merangkum data faktual: *10 task selesai, 2 modul dirilis, aktivitas issue log*. |

---

## 🏛️ Arsitektur Tiga Pilar Utama

```
                             ┌────────────────────────────────┐
                             │           ProjectIQ            │
                             └────────────────┬───────────────┘
                                              │
         ┌────────────────────────────────────┼────────────────────────────────────┐
         │                                    │                                    │
         ▼                                    ▼                                    ▼
┌──────────────────┐               ┌───────────────────────┐            ┌──────────────────────┐
│ Work Management  │               │   Role-Based RAG      │            │ AI Executive Audit   │
├──────────────────┤               ├───────────────────────┤            ├──────────────────────┤
│ • Workspaces     │               │ • Upload PRD/BRD      │            │ • Task Completion    │
│ • Projects       │               │ • Tech Specs & SOP    │            │ • Module Velocity    │
│ • Modules/Epics  │               │ • Granular RBAC Docs  │            │ • Activity Logging   │
│ • Cycles/Sprints │               │ • Qdrant Vector Store │            │ • Verifiable Proofs  │
│ • Issues / Tasks │               │ • Contextual Citations│            │ • Leader AI Inquiries│
└──────────────────┘               └───────────────────────┘            └──────────────────────┘
```

---

## 👥 Persona Pengguna & Peran (Role Mapping)

1. **Chief Technology Officer / Executive (CTO / Lead)**:
   - Memantau kesehatan proyek, *velocity*, dan produktivitas tim.
   - Bertanya ke AI mengenai performa individu dan hambatan teknis tanpa harus mengadakan rapat status harian.
   - Akses penuh ke seluruh dokumen arsitektur dan strategis.
2. **Product Manager (PM) / Product Owner**:
   - Mengunggah dan memelihara dokumen PRD, BRD, roadmap, dan acceptance criteria.
   - Menetapkan hak akses peran (*Role Assignment*) untuk setiap dokumen.
   - Menanyakan progres penyelesaian modul fitur ke AI.
3. **Software Engineer / Developer (DEV)**:
   - Mengerjakan tiket/isu, mengubah status, dan mencatat progres pekerjaan.
   - Bertanya ke AI seputar implementasi teknis, API specs, dan detail PRD secara instan 24/7.

---

## 🛠️ Tech Stack & Microservices

* **Core Backend API (`services/api`)**: FastAPI, SQLAlchemy (Async), Alembic Migration, PostgreSQL 15.
* **AI Knowledge Service (`services/ai-service`)**: FastAPI, Google Gemini 3.6 Flash, Gemini Embeddings, Qdrant Vector Store.
* **Frontend Web Application (`apps/client`)**: Next.js 16 (App Router), React 19, Tailwind CSS v4.
* **Cache & Message Broker**: Redis 7.
* **Monorepo Management**: Bun workspaces & Docker Compose.
