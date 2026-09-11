♿ Accessly

<p align="center">
  <strong>Tell Accessly your accessibility needs once — it coordinates the rest for every event.</strong>
</p>

<p align="center">
  <a href="https://accessly-murex.vercel.app/"><img src="https://img.shields.io/badge/Live_Demo-Vercel-000000?logo=vercel&logoColor=white"></a>
  <a href="https://github.com/ghaida-alsalamah/accessly"><img src="https://img.shields.io/badge/GitHub-Repository-181717?logo=github&logoColor=white"></a>
  <img src="https://img.shields.io/badge/AWS-Bedrock-FF9900?logo=amazonwebservices&logoColor=white">
  <img src="https://img.shields.io/badge/Strands-Agents_SDK-6C47FF">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/Playwright-Chromium-2EAD33?logo=playwright&logoColor=white">
</p>

🌍 What is Accessly?

Accessly is an AI accessibility coordination agent for events.

People who need accommodations often repeat the same process for every conference, workshop, seminar, university event, or community activity: find accessibility information, locate the correct contact or form, explain their needs again, check timing, submit a request, follow up, and wait for confirmation.

Accessly turns that repetitive workflow into one coordinated experience.

Tell it your accessibility needs once. For every event after that, it handles the accessibility coordination for you.

👉 Live demo

https://accessly-murex.vercel.app/

💡 The Problem

Accessibility information is often scattered, incomplete, hidden behind forms, or only available after contacting an organizer.

A user may need:

ASL interpretation

live captions

accessible parking

wheelchair access

accessible seating

assistive listening

large-print materials

screen-reader-friendly materials

quiet / sensory-friendly space

For every new event, they may need to repeat the entire search-and-request process.

Accessly is designed to reduce that friction.

✨ What Accessly Does

👤 1. Save accessibility needs

The user creates a reusable accessibility profile. No diagnosis is required.

🔗 2. Paste an event URL

The user provides the official event page.

🌐 3. Browse the real event website

Accessly uses Playwright/Chromium to inspect the event page and official linked resources.

🔎 4. Extract event details

Accessly verifies:

Event name

Date

Time

Location

Organizer

Event format

♿ 5. Evaluate every saved need

Status

Meaning

✅ Confirmed

Official evidence explicitly confirms the accommodation

❌ Not Confirmed

Applicable, but no confirmation was found

➖ Not Applicable

Clearly irrelevant to the event format

❓ Unknown

Accessly cannot verify it reliably

Accessly does not assume accessibility features exist without official evidence.

📝 6. Find the official request path

If action is needed, Accessly searches for the official form, organizer email, accessibility office, or other official contact channel.

⏰ 7. Check timing

Accessly distinguishes between a preferred notice period and a hard deadline, and performs date calculations programmatically.

✉️ 8. Prepare the request

Accessly drafts the recipient, subject, and body using only the user's saved applicable needs.

✅ 9. Human approval

Nothing is sent until the user reviews and explicitly approves the exact request.

📨 10. Send safely

During development, Test Mode redirects messages to a controlled inbox so real organizers are not contacted accidentally.

📊 11. Track the request

After sending, Accessly creates a request such as REQ-001 and tracks overall and per-accommodation statuses.

🔄 12. Check replies

Accessly can check the controlled inbox, classify a matching reply, and update the request status.

🧠 Agent Workflow

flowchart TD
    A[👤 Save accessibility needs] --> B[🔗 Submit event URL]
    B --> C[🤖 Strands Agent]
    C --> D[🌐 Playwright / Chromium]
    D --> E[Official event page + linked resources]
    E --> F[🔎 Extract event & accessibility evidence]
    F --> G[♿ Evaluate each need]
    G --> H{Action required?}
    H -- No --> I[✅ Show verified status]
    H -- Yes --> J[📝 Find official request channel]
    J --> K[⏰ Check timing]
    K --> L[✉️ Draft request]
    L --> M[👀 User reviews]
    M --> N{Approved?}
    N -- No --> O[✏️ Edit / cancel]
    N -- Yes --> P[📨 Send in Test Mode]
    P --> Q[📁 Create tracked request]
    Q --> R[📬 Check reply]
    R --> S[🧠 Classify response]
    S --> T[📊 Update statuses]

🛠️ Tech Stack

<p>
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Strands-Agents_SDK-6C47FF">
  <img src="https://img.shields.io/badge/Amazon_Bedrock-Claude_Sonnet-FF9900?logo=amazonwebservices&logoColor=white">
  <img src="https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/Playwright-Chromium-2EAD33?logo=playwright&logoColor=white">
  <img src="https://img.shields.io/badge/React-Frontend-61DAFB?logo=react&logoColor=black">
  <img src="https://img.shields.io/badge/Vite-Build-646CFF?logo=vite&logoColor=white">
  <img src="https://img.shields.io/badge/Docker-Container-2496ED?logo=docker&logoColor=white">
  <img src="https://img.shields.io/badge/Vercel-Frontend_Hosting-000000?logo=vercel&logoColor=white">
  <img src="https://img.shields.io/badge/Northflank-Backend_Hosting-0A84FF">
  <img src="https://img.shields.io/badge/Gmail-SMTP_%26_IMAP-EA4335?logo=gmail&logoColor=white">
  <img src="https://img.shields.io/badge/GitHub-Version_Control-181717?logo=github&logoColor=white">
</p>

Technology

Role

Python 3.11

Core backend and agent logic

Strands Agents SDK

Agent orchestration and tool use

Amazon Bedrock + Claude Sonnet

Reasoning, event understanding, drafting, reply classification

FastAPI

API between frontend and the agent

Playwright / Chromium

Real website and form inspection

React + Vite

Product frontend

Docker

Reproducible backend runtime with Chromium

Vercel

Public frontend hosting

Northflank

Public containerized backend hosting

Gmail SMTP / IMAP

Test-mode sending and reply checking

GitHub

Source control and deployment integration

🏗️ Architecture

flowchart LR
    U[👤 User] --> FE[💻 React / Vite Frontend]
    FE -->|HTTPS API| API[⚡ FastAPI]
    API --> AGENT[🤖 Strands Agent]
    AGENT --> BEDROCK[☁️ Amazon Bedrock]
    AGENT --> BROWSER[🌐 Playwright / Chromium]
    AGENT --> MAIL[📨 Gmail SMTP / IMAP]
    AGENT --> TRACK[📁 Request Tracking]
    FE --- VERCEL[▲ Vercel]
    API --- NF[☁️ Northflank]

User
  ↓
Vercel Frontend
  ↓ HTTPS
Northflank FastAPI Backend
  ↓
Strands Agent
  ├── Amazon Bedrock
  ├── Playwright / Chromium
  ├── Gmail SMTP / IMAP
  └── Request Tracking

🧩 Core Agent Tools

get_user_accessibility_needs — reads the user's saved profile.

check_event_timing — calculates days until the event and notice windows.

Browser tool — inspects event pages, linked accessibility resources, and forms.

send_accommodation_email — sends an explicitly approved request in safe Test Mode.

create_request_record — creates a tracked request after a successful send.

check_organizer_reply — checks for a matching reply.

update_request_status — updates overall and per-accommodation statuses.

🛡️ Safety by Design

Accessly will not:

invent accessibility information,

assume a feature exists,

invent form fields,

invent names, phone numbers, or diagnoses,

expand a saved accessibility need into additional needs,

send before explicit approval,

automatically retry a failed send,

submit a real organization's form during testing.

Human-in-the-loop

Before any send action, Accessly shows the exact:

Recipient
Subject
Body

The user must explicitly approve that content.

Real form protection

During development, Accessly may inspect or fill a real organization form, but it never clicks the final Submit button.

🎨 Frontend Experience

The frontend intentionally avoids dumping raw LLM text.

Event Details

Structured fields for event name, date, time, location, organizer, and format.

Accessibility Check

Each need appears as a dedicated card with a status badge and short evidence.

Request Action

Shows the official contact/form, timing information, and recommended next step.

Email Draft

Displayed in a dedicated component with recipient, subject, body, Edit, and Approve & Send.

My Requests

Shows request ID, event, overall status, individual accommodation statuses, and Check for Updates.

🧪 Testing

Accessly was tested against real public university event pages, including pages from:

University of Michigan

Syracuse University

University of Washington

Stanford University

Testing covered:

dynamic event extraction,

accessibility evidence checking,

virtual vs. in-person applicability,

notice calculations,

official accommodation forms,

organizer contact discovery,

email drafting,

test-mode sending,

request creation,

reply checking,

and status updates.

Production container smoke test

python container_smoke.py

Validated successfully:

PASS: Strands/browser imports, FastAPI startup, /health, headless Chromium

The public deployment was also tested end-to-end for profile loading, event analysis, structured results, request drafting, safe sending, request creation, and update checking.

🧭 Development Process

Phase 1 — Terminal agent prototype

We first proved the complete agent workflow from the terminal using Strands and Amazon Bedrock.

Phase 2 — Real browser automation

Some event sites rejected simple HTTP requests, so Accessly moved to Playwright/Chromium for real browser navigation.

Phase 3 — Safe email workflow

Gmail SMTP was added with a strict Test Mode and approval guard.

Phase 4 — Request tracking

The prototype gained request IDs, per-accommodation status, reply checking, and automatic updates.

Phase 5 — Dynamic profiles

Accessibility needs were moved out of hardcoded logic and into a reusable user profile.

Phase 6 — Product frontend

The agent was exposed through FastAPI and connected to the React/Vite interface. Raw agent output was converted into structured UI components.

Phase 7 — Public deployment

The frontend was deployed on Vercel and the Dockerized backend on Northflank.

📁 Repository Structure

accessly/
├── frontend/                     # React/Vite frontend
├── api.py                        # FastAPI application
├── main.py                       # Strands Agent + tools
├── result_presenter.py           # Structured result presentation
├── deployment_runtime.py         # Production runtime configuration
├── container_smoke.py            # Production smoke test
├── Dockerfile.northflank
├── .dockerignore
├── .gitignore
├── requirements-api.txt
├── requirements-production.txt
├── test_frontend_ux.py
├── test_live_frontend.py
├── test_northflank.py
├── test_public_send.py
├── test_result_presenter.py
├── .env.production.example
└── README.md

Secret .env files, logs, user profiles, request data, virtual environments, and credentials should never be committed.

⚙️ Run Locally

Backend

git clone https://github.com/ghaida-alsalamah/accessly.git
cd accessly

python -m venv .venv

Windows:

.venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements-production.txt

Create .env:

AWS_BEARER_TOKEN_BEDROCK=
AWS_REGION=eu-north-1

ACCESSLY_EMAIL=
ACCESSLY_EMAIL_APP_PASSWORD=
ACCESSLY_TEST_RECIPIENT=

ACCESSLY_ALLOWED_ORIGINS=http://localhost:5173
PORT=8000

Start FastAPI:

python -m uvicorn api:app --host 0.0.0.0 --port 8000

Health check:

http://localhost:8000/health

Expected:

{"status":"ok"}

Frontend

cd frontend
npm install
npm run dev

Frontend API variable:

VITE_API_BASE_URL=http://localhost:8000/api

☁️ Deployment

Vercel

Root Directory: frontend
Build Command: npm run build
Output Directory: dist

VITE_API_BASE_URL=https://<northflank-backend>/api

Northflank

Service: Combined
Build: Dockerfile / BuildKit
Dockerfile: /Dockerfile.northflank
Build context: /
Internal port: 8000
Protocol: HTTP
Instances: 1

Runtime variables:

AWS_BEARER_TOKEN_BEDROCK=
AWS_REGION=eu-north-1
ACCESSLY_EMAIL=
ACCESSLY_EMAIL_APP_PASSWORD=
ACCESSLY_TEST_RECIPIENT=
ACCESSLY_ALLOWED_ORIGINS=https://accessly-murex.vercel.app
PORT=8000

📌 Current Limitations

Profile/request storage is currently lightweight local storage and should move to a persistent database for production.

CAPTCHA, authentication, and anti-bot protections can prevent verification on some event websites.

If official evidence cannot be verified, Accessly returns Unknown instead of guessing.

Organizer integrations currently rely mainly on official webpages, forms, and email.

🔮 Roadmap

30 days

Persistent database, stronger parsing, improved error recovery.

60 days

Event-platform connectors, richer notifications, reusable institutional integrations.

90 days

Multi-user authentication, accessibility-office integrations, fulfillment analytics, and larger-scale deployment.

🌱 Impact

Accessly is not intended to replace accessibility teams.

It is designed to reduce repetitive coordination between attendees and organizers.

Accessibility needs should not have to be re-explained from scratch for every event.

🏆 Built for Agents for Humans

Accessly demonstrates an agent that moves beyond answering questions and carries a real workflow through multiple steps:

Understand → Browse → Verify → Decide → Draft → Ask → Act → Track → Follow up

👥 Team

Built by the Accessly team through a combination of:

AI agent development

backend engineering

browser automation

frontend/product design

accessibility-focused UX

testing

cloud deployment

🔐 Security

Never commit:

.env
AWS credentials
Gmail App Passwords
test inbox credentials
user_profile.json
requests.json
backend logs

Production secrets should be stored only as secure hosting environment variables.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
<p align="center">
  <strong>Accessly ♿</strong><br>
  Accessibility coordination, handled.
</p>
