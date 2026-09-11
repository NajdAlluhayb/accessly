"""Opt-in live browser regression: real events + Bedrock, no sending/submission."""
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parent
ARTIFACTS=ROOT/'screenshots'/'event-mapping'
ARTIFACTS.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1100})
    browser_errors=[]
    completed=[]
    page.on('pageerror',lambda error:browser_errors.append(str(error)))
    page.on('console',lambda message:browser_errors.append(message.text) if message.type=='error' else None)
    def capture(response):
        if '/api/jobs/' in response.url and response.request.method=='GET' and response.status==200:
            payload=response.json()
            if payload.get('status')=='completed': completed.append(payload)
    page.on('response',capture)
    def wait_result():
        page.wait_for_function("!document.querySelector('.loading-card')",timeout=300000)
        assert not page.get_by_role('alert').count(),page.get_by_role('alert').all_text_contents()
        assert completed,'No completed backend response captured'
        job=completed[-1]
        assert job['result']['presentation_status']=='ready',job['result']
        return job
    def check_fields(job):
        data=job['result']
        for field in ['name','date','time','location','organizer','format']:
            value=data['event'][field]
            cell=page.locator(f'[data-event-field="{field}"] dd')
            assert cell.count()==1, f'Duplicate/missing {field} card'
            expect(cell).to_have_text(value or 'Not stated by the organizer')
        for need in data['accessibility_results']:
            row=page.locator('[data-need]').filter(has=page.get_by_role('heading',name=need['name'],exact=True))
            expect(row.locator('.status-badge')).to_have_text(need['status'].title())
        assert page.locator('.agent-notes').count()==0,'Raw report is still rendered'
        assert not re.search(r'\*\*|\|---|## ',page.locator('.structured-result').inner_text())
    def submit(url):
        page.get_by_role('button',name='Drop a Link',exact=False).click()
        page.get_by_placeholder('https://event-website.com/...').fill(url)
        with page.expect_response(lambda r:r.url.endswith('/api/events') and r.request.method=='POST') as response:
            page.get_by_role('button',name='Process Event').click()
        assert response.value.status==202
        print('Submitted real URL:',url,flush=True)
        return wait_result()
    page.goto('http://127.0.0.1:8443')
    page.get_by_role('button',name='Enter the app').click()
    page.get_by_role('button',name='Save preferences and continue').click()
    first=submit('https://adata.org/event/1010/')
    assert 'Planning Accessible Events' in first['result']['event']['name']
    assert all(first['result']['event'][field] for field in ['name','date','time','location','organizer','format'])
    check_fields(first)
    ARTIFACTS.joinpath('real-event-result.json').write_text(json.dumps(first,ensure_ascii=False,indent=2),encoding='utf-8')
    page.screenshot(path=str(ARTIFACTS/'event-details.png'),full_page=True)
    print('PASS: all six API event fields equal the rendered card, and accessibility badges match.',flush=True)
    page.get_by_label('Continue the conversation').fill('Please prepare the accommodation request email for review using my saved needs. Do not send any email or submit any form.')
    page.get_by_role('button',name=re.compile('Send reply')).click()
    draft_job=wait_result()
    assert draft_job['result']['draft'],'Agent draft was not exposed as structured data'
    check_fields(draft_job)
    draft=draft_job['result']['draft']
    expect(page.locator('.draft-meta dd').nth(0)).to_have_text(draft['to'])
    expect(page.locator('.draft-meta dd').nth(1)).to_have_text(draft['subject'])
    expect(page.locator('.email-body')).to_have_text(draft['body'])
    assert page.get_by_role('button',name='Approve & Send',exact=True).is_enabled()
    ARTIFACTS.joinpath('real-draft-result.json').write_text(json.dumps(draft_job,ensure_ascii=False,indent=2),encoding='utf-8')
    page.screenshot(path=str(ARTIFACTS/'email-draft.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.screenshot(path=str(ARTIFACTS/'mobile.png'),full_page=True)
    page.set_viewport_size({'width':1440,'height':1100})
    print('PASS: real email draft has exact recipient, subject and body; no send action clicked.',flush=True)
    page.get_by_role('button',name=re.compile('Home')).click()
    second=submit('https://wpaccessibility.day/2026/register/')
    assert second['session_id']!=first['session_id']
    assert second['result']['event']['name']!=first['result']['event']['name']
    assert 'WordPress' in second['result']['event']['name']
    check_fields(second)
    page.screenshot(path=str(ARTIFACTS/'second-event.png'),full_page=True)
    ARTIFACTS.joinpath('second-event-result.json').write_text(json.dumps(second,ensure_ascii=False,indent=2),encoding='utf-8')
    assert not browser_errors,browser_errors
    print('PASS: second real URL changed the card, no stale first-event values, no browser errors.',flush=True)
    browser.close()
