# Accessly local app

Accessly's existing Strands agent runs through FastAPI and Amazon Bedrock. The React frontend displays a validated structured result instead of parsing the agent's Markdown. The original agent tools, system prompt, email workflow, request tracking and Bedrock configuration in `main.py` are unchanged. No AgentCore is used.

## Run locally

From the workspace root:

```powershell
.venv/Scripts/python.exe -m pip install -r requirements-api.txt
.venv/Scripts/python.exe -m uvicorn api:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Frontend: http://127.0.0.1:8443
API docs: http://127.0.0.1:8000/docs

If either port is already occupied by this app, use the running server. This local adapter is single-user, unauthenticated and loopback-only. Keep one backend worker. Credentials remain in the root server environment/.env, never in frontend files or VITE_ variables.

## Result data flow and bug fix

There is no POST /chat endpoint in this repository. The actual flow is:

1. `POST /api/events` starts a real event check and returns a job ID.
2. `GET /api/jobs/{id}` polls until the job completes.
3. The unchanged agent's text report is passed to a separate formatter using the existing model provider, with no browser/email/action tools.
4. The formatter returns a Pydantic-validated schema. The serializer checks event values against the report, validates classifications against quoted evidence, preserves the exact saved need names, and verifies draft text appears in the report.
5. `AgentWorkspace.tsx` stores the completed job's `result` object on the conversation turn. `AgentResult.tsx` receives that object directly and renders `result.event.name`, `.date`, `.time`, `.location`, `.organizer`, and `.format`.

The previous implementation received and stored the text correctly, but a frontend regex recognized only exact `Label: value` lines. The real report used table rows such as `| **Event Name** | ... |` and `Organizer/Sponsor`, so the Event Details component showed placeholders. Time and Format were not mapped at all. That parser has been removed.

A completed job includes the original `response` string for compatibility/diagnostics and a `result` object with:

- `schema_version`, `presentation_status`, `message`
- `event`: name, date, time, location, organizer, format, url
- `event_sources`: supporting text for event fields
- `accessibility_results`: exact need name, status, evidence, source_quote
- `recommended_action`: official_contact, official_form, notice_period, recommendation
- `draft`: to, subject, body, or null
- `requests`: matching stored request records

The UI never renders the raw response. It displays a short summary, six event fields, per-need badges and explanations, request action, a dedicated editable email draft, and stored request statuses. Unverified fields remain explicitly unavailable. Formatting involves an additional Bedrock call; it has no tools and cannot send anything. If it fails, `POST /api/jobs/{id}/presentation` retries only formatting, never the original agent action.

Conversation state stores structured results under a versioned, event-URL-specific session key. The workspace is keyed by event URL. Follow-ups retain previously verified fields when the new message does not state them, while a new event session starts fresh. Old unstructured browser caches are not reused. Drafts are not inherited when absent from the current response, preventing obsolete approvals.

## Preserved actions

- Profile Save & Continue writes exact selected needs and preserves other saved profile fields.
- Replies and approval messages use `POST /api/sessions/{session_id}/messages`.
- Edit sends a revision request that explicitly prohibits sending.
- Approve & Send approves the exact displayed recipient, subject and body once.
- The existing development email tool redirects to its configured test inbox. A new stored request record is required for the send-success banner.
- My Requests uses `GET /api/requests`; Check for Updates uses `POST /api/requests/{request_id}/check`.

## Verified results

A real headless Chromium run checked https://adata.org/event/1010/ and https://wpaccessibility.day/2026/register/ through the frontend and real backend/Bedrock. The test compared every rendered event field with the actual completed API result. The ADA event had all six values and rendered Accessible parking as Not Applicable and ASL interpretation as Not Confirmed. In the same conversation, the real email draft rendered with recipient, subject and body exactly matching the API. No send button was clicked.

The second event replaced the first event's details in a different session and rendered ASL interpretation as Confirmed based on that event's report. No stale first-event fields were carried over. Mobile overflow checks passed, and no browser console errors or backend exceptions occurred during the final live run. API/formatter regression tests and controlled approval/update/error/recovery tests passed. Production build and TypeScript checks passed.

Run checks:

```powershell
.venv/Scripts/python.exe -m unittest test_result_presenter -v
.venv/Scripts/python.exe test_frontend_ux.py
cd frontend
node test-presentation.mjs
npm.cmd run build
npx.cmd tsc --noEmit
```

Optional live regression from the root (uses Bedrock, requires existing credentials and saved profile):

```powershell
.venv/Scripts/python.exe test_live_frontend.py
```

Captured real API responses and screenshots are in `screenshots/event-mapping/`, excluded from Git. Actual email transmission, organizer inbox checks and form submission were not performed in the live test; approval and update UI paths use controlled responses in the regression suite.
