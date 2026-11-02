"""Exercise the rendered atlas at a real local or deployed URL with Playwright."""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import io
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]


def run(url: str, channel: str|None, report_name: str) -> None:
    url=url.rstrip('/')+'/'
    class Checks(list):
        def append(self, item):
            print('PASS: '+item, flush=True)
            super().append(item)
    checks=Checks();errors=[];failed=[]
    screenshots=ROOT/'docs/screenshots';screenshots.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,**({'channel':channel} if channel else {}))
        context=browser.new_context(viewport={'width':1440,'height':1000},device_scale_factor=1,accept_downloads=True,reduced_motion='reduce')
        page=context.new_page()
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('response',lambda response:failed.append({'url':response.url,'status':response.status}) if response.status>=400 else None)
        def ready():
            try:
                page.wait_for_function("window.atlasReady === true && document.getElementById('atlas').getAttribute('aria-busy') === 'false'",timeout=45000)
            except Exception:
                print({'page_errors':errors,'http_errors':failed,'visible_error':page.locator('#app-error').inner_text()},flush=True)
                raise
        def select(id,value):
            page.locator('#'+id).select_option(str(value));ready()
        def number(id,value):
            if not page.locator('#'+id).is_visible():
                page.locator('.week-options summary').click()
            page.locator('#'+id).fill(str(value));page.locator('#'+id).press('Tab');ready()
        def downloaded(button):
            with page.expect_download() as event:
                page.locator('#'+button).click()
            download=event.value
            text=Path(download.path()).read_text(encoding='utf-8-sig')
            return list(csv.DictReader(io.StringIO(text))),download.suggested_filename
        response=page.goto(urljoin(url,'explore.html'),wait_until='domcontentloaded');assert response.status==200
        ready();assert page.locator('#kpi-cases').inner_text()=='313,814'
        assert page.locator('#map-container path[data-code]').count()==33
        assert page.locator('#summary-table tbody tr').count()==132
        assert page.locator('#timeline .scatterlayer').count()>0
        assert not page.locator('#app-error').is_visible()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(screenshots/'desktop.png'),full_page=True)
        page.screenshot(path=str(screenshots/'desktop-viewport.png'))
        checks.append('Desktop initial render: 313814 dengue counts, 33 map units, 132 summary rows, two rendered charts, no horizontal overflow')
        rows,name=downloaded('download');assert len(rows)==132
        assert sum(int(r['cases']) for r in rows if r['cases'])==313814
        assert len([r for r in rows if r['department_code']=='11' and r['cases']==''])==4
        assert 'all-2019-2022' in name
        checks.append('Default summary CSV agrees with table and source totals; Bogota remains blank')
        select('department','08');select('year-start',2020);select('year-end',2021);number('week-start',10);number('week-end',20)
        rows,_=downloaded('download');weekly,_=downloaded('download-weekly')
        assert len(rows)==2 and len(weekly)==22 and all(r['department_code']=='08' for r in weekly)
        assert sum(int(r['cases']) for r in rows if r['cases'])==sum(int(r['cases']) for r in weekly if r['cases'])
        assert int(page.locator('#kpi-cases').inner_text().replace(',',''))==sum(int(r['cases']) for r in rows if r['cases'])
        plotted=page.locator('#timeline').evaluate('(el)=>el.data[0].y')
        assert sum(v for v in plotted if v is not None)==sum(int(r['cases']) for r in rows if r['cases'])
        assert page.locator('#seasonal').evaluate('(el)=>el.data.map(t=>t.name)')==['2020','2021']
        select('metric','rate')
        assert 'Mean of yearly' in page.locator('#map-subtitle').inner_text()
        assert page.locator('#map-container circle').count()==0
        for r in rows:
            if r['cases']:assert abs(float(r['cases_per_100k'])-int(r['cases'])/int(r['population_total'])*100000)<1e-9
        saved_url=page.url;page.reload(wait_until='domcontentloaded');ready();assert page.locator('#department').input_value()=='08' and page.locator('#week-start').input_value()=='10'
        checks.append('Department/year/week/rate filters, persisted URL, timeline and seasonal series agree with both CSV exports and year-specific rate arithmetic')
        page.locator('#map-container path[data-code="11"]').focus();page.keyboard.press('Enter');ready()
        assert page.locator('#department').input_value()=='11' and page.locator('#kpi-cases').inner_text()=='No data'
        assert 'No source rows' in page.locator('#timeline').inner_text()
        rows,_=downloaded('download');assert all(r['cases']=='' and r['cases_per_100k']=='' for r in rows)
        assert all(int(r['population_total'])>0 for r in rows)
        checks.append('Keyboard map selection and Bogota empty state preserve unavailable counts/rates despite available population')
        page.locator('#reset').click();ready();assert page.locator('#kpi-cases').inner_text()=='313,814'
        select('event','220');assert page.locator('#kpi-cases').inner_text()=='4,461'
        select('department','97');select('year-start',2019);select('year-end',2019)
        assert page.locator('#timeline').evaluate('(el)=>el.data[0].mode')=='lines+markers'
        assert 'markers' in page.locator('#seasonal').evaluate('(el)=>el.data[0].mode')
        checks.append('Severe dengue stays separate; sparse Vaupes observations have point marks even between gaps')
        page.locator('#reset').click();ready();select('department','05');select('year-start',2020);select('year-end',2020);number('week-start',53);number('week-end',53)
        assert page.locator('#timeline').evaluate('(el)=>el.data[0].x.length')==1
        assert page.locator('#timeline .scatterlayer .point').count()>=1
        select('year-end',2019)
        assert page.locator('#download').is_disabled() and 'No periods match' in page.locator('#summary-table').inner_text()
        select('metric','rate');assert 'NaN' not in page.locator('#map-container').inner_html()
        checks.append('Single-week point visible; inverted range shows empty state, disables downloads and never emits NaN map values')
        page.locator('#reset').click();ready();number('week-start',53);number('week-end',53)
        rows,_=downloaded('download');assert {r['year'] for r in rows}=={'2020'}
        checks.append('Week53-only export includes only2020; other years are not invented')
        page.locator('#reset').click();ready()
        page.set_viewport_size({'width':390,'height':844})
        page.reload(wait_until='domcontentloaded');ready()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert page.locator('#reset').is_visible()
        select('department','13');assert page.locator('#department').input_value()=='13'
        page.locator('#reset').click();ready()
        page.screenshot(path=str(screenshots/'mobile.png'),full_page=True)
        page.screenshot(path=str(screenshots/'mobile-viewport.png'))
        page.locator('#seasonal').scroll_into_view_if_needed();page.screenshot(path=str(screenshots/'mobile-seasonal.png'))
        checks.append('390px mobile portrait: filters/reset work, charts render, no page overflow; screenshots captured')
        page.set_viewport_size({'width':844,'height':390});page.reload(wait_until='domcontentloaded');ready();assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        checks.append('844px narrow landscape: no page overflow')
        page.set_viewport_size({'width':1440,'height':1000})
        for name in ['index.html','methods.html','data.html']:
            resp=page.goto(urljoin(url,name),wait_until='domcontentloaded');assert resp.status==200
            assert page.locator('h1').count()>0
            if name=='data.html':assert '122,992' in page.locator('main').inner_text()
            if name=='index.html':
                page.wait_for_function("Array.from(document.querySelectorAll('img')).every(i=>i.complete&&i.naturalWidth>0)")
                page.screenshot(path=str(screenshots/'overview.png'),full_page=True)
            # Validate local navigation/assets linked from each main page.
            links=page.locator('a[href]').evaluate_all('(links)=>links.map(a=>a.href)')
            for target in set(links):
                if target.startswith(url) and '#' not in target:
                    response=context.request.head(target)
                    assert response.status==200,(target,response.status)
        checks.append('Overview, methods, data and same-site links return200; executed Python source table and exported figure load')
        # Verify a visible failure state using a separate page with deliberate network failure.
        offline=context.new_page();offline.route('**/data/atlas.json',lambda route:route.abort())
        offline.goto(urljoin(url,'explore.html'),wait_until='domcontentloaded');offline.locator('#app-error').wait_for(state='visible')
        assert 'could not load' in offline.locator('#app-error').inner_text()
        offline.close();checks.append('Data-load failure produces an informative visible fallback')
        assert not errors,errors
        assert not failed,failed
        browser.close()
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'url':url,'browser_channel':channel or 'chromium',
            'checks':checks,'page_errors':errors,'http_errors':failed,'passed':True,
            'visual_review':'Screenshots captured; human/model visual review is recorded separately in RELEASE_REPORT.md.'}
    (ROOT/'reports'/report_name).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='http://127.0.0.1:4200/')
    parser.add_argument('--channel',default='msedge')
    parser.add_argument('--report',default='browser_local.json')
    args=parser.parse_args();run(args.url,None if args.channel=='chromium' else args.channel,args.report)
