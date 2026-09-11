"""Controlled browser regression. All API requests are intercepted; no email sends."""
import copy,re
from playwright.sync_api import sync_playwright,expect
BASE={'schema_version':1,'presentation_status':'ready','message':'Review your accessibility check.',
 'event':{'name':'Controlled Event','date':'October 15, 2026','time':'14:00','location':'Online','organizer':'Test Organizer','format':'Virtual','url':'https://example.com'},
 'accessibility_results':[{'name':'Live captions','status':'NOT CONFIRMED','evidence':'Not mentioned.'}],
 'recommended_action':{'official_contact':'organizer@example.com','official_form':None,'notice_period':None,'recommendation':'Request captions.'},
 'draft':{'to':'organizer@example.com','subject':'Accommodation request','body':'Dear organizer,\nPlease provide Live captions.\nThank you.'},'requests':[]}
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True)
 page=browser.new_page(viewport={'width':1440,'height':1000})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 state={'result':copy.deepcopy(BASE),'job':0,'messages':[],'requests':[],'fail':False,'events':0,'format_fail':True}
 record={'request_id':'REQ-TEST','event_name':'Controlled Event','event_url':'https://example.com','status':'PENDING','accommodations':{'Live captions':'PENDING'}}
 def route_api(route):
  path=route.request.url.split('/api')[-1];code=200
  if path=='/profile': data={'needs':['Live captions']}
  elif path=='/requests': data=state['requests']
  elif path=='/events' or path.endswith('/messages') or path.endswith('/check') or path.endswith('/presentation'):
   if state['fail']: route.fulfill(status=503,json={'detail':'Backend temporarily unavailable'});return
   if path=='/events': state['events']+=1
   if path.endswith('/presentation'): state['format_fail']=False
   if path.endswith('/messages'):
    message=route.request.post_data_json['message'];state['messages'].append(message)
    if message.startswith('Please revise'): state['result']['draft']['body']='Dear organizer,\nPlease provide Live captions for the keynote.\nThank you.'
    elif message.startswith('I explicitly approve'):
     state['requests']=[record];state['result']['draft']=None;state['result']['requests']=[record];state['result']['message']='Request sent to the test inbox.'
   state['job']+=1;data={'id':str(state['job']),'session_id':'test','status':'processing','response':''};code=202
  else: data={'id':str(state['job']),'session_id':'test','status':'completed','response':'Raw report must never be displayed','result':({'schema_version':1,'presentation_status':'unavailable','message':'Formatting failed. Retry formatting.','event':None,'accessibility_results':[],'recommended_action':None,'draft':None,'requests':[]} if state['format_fail'] else state['result'])}
  route.fulfill(status=code,json=data)
 page.route('**/api/**',route_api)
 page.goto('http://127.0.0.1:8443')
 page.get_by_role('button',name='Enter the app').click()
 page.get_by_role('button',name='Save preferences and continue').click()
 page.get_by_role('button',name='Drop a Link',exact=False).click()
 page.get_by_placeholder('https://event-website.com/...').fill('https://example.com')
 page.get_by_role('button',name='Process Event').click()
 page.get_by_role('alert').wait_for()
 page.get_by_role('button',name='Retry formatting').click()
 page.get_by_role('heading',name='Event Details',exact=True).wait_for()
 assert state['events']==1, 'Formatting retry reran the agent action'
 expect(page.locator('[data-event-field="name"] dd')).to_have_text('Controlled Event')
 assert 'Raw report must never be displayed' not in page.locator('body').inner_text()
 page.get_by_role('button',name='Edit',exact=True).click()
 page.get_by_label('Message',exact=True).fill('Dear organizer,\nPlease provide Live captions for the keynote.\nThank you.')
 page.get_by_role('button',name='Review revised draft').click()
 page.get_by_role('button',name='Approve & Send',exact=True).wait_for()
 assert 'Do not send it.' in state['messages'][0]
 page.get_by_role('button',name='Approve & Send',exact=True).click()
 page.get_by_text('Request sent to test inbox',exact=True).wait_for()
 assert sum(m.startswith('I explicitly approve') for m in state['messages'])==1
 page.set_viewport_size({'width':390,'height':844})
 assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
 page.get_by_role('button',name='View My Requests').click()
 page.get_by_role('button',name='Check for Updates').click()
 page.wait_for_function("!document.querySelector('.loading-card')")
 state['fail']=True
 page.get_by_role('button',name='Check for Updates').click()
 page.get_by_role('alert').wait_for()
 assert page.get_by_role('button',name='Check for Updates').is_enabled()
 assert not errors,errors
 print('PASS: structured contract, exact draft editing, one approval, send confirmation, request cards, backend failure, mobile layout.')
 browser.close()
