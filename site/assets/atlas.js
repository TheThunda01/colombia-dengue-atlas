import {defaults,readState,selectedRows,summaries,mapSummaries,timeSeries,sumPresent,csv} from './model.mjs';
const $=id=>document.getElementById(id), fmt=n=>n===null?'No data':new Intl.NumberFormat('en-US').format(n), dec=n=>n===null?'No data':new Intl.NumberFormat('en-US',{maximumFractionDigits:1}).format(n);
const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const colors={2019:'#166b70',2020:'#bd632b',2021:'#69509b',2022:'#3b677f'};
const bindings={department:'department',event:'event',start:'year-start',end:'year-end',first:'week-start',last:'week-end',metric:'metric'};
let data,state,latestSummary=[],latestWeekly=[],renderToken=0;
function setControls(){for(const[k,id]of Object.entries(bindings))$(id).value=state[k];}
function stateUrl(){const p=new URLSearchParams();for(const[k,v]of Object.entries(state))p.set(k,v);return '?'+p;}
function selectDepartment(code){state.department=code;setControls();history.pushState(null,'',stateUrl());render();}
function download(rows,kind){const blob=new Blob(['\uFEFF'+csv(rows)],{type:'text/csv;charset=utf-8;'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`colombia-${state.event}-${state.department}-${state.start}-${state.end}-w${state.first}-${state.last}-${kind}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);}
function renderMap(){
 const map=mapSummaries(data,state),val=d=>state.metric==='rate'?d.rate:d.cases,max=Math.max(1,...map.map(d=>val(d)??0)),rate=state.metric==='rate';
 $('map-subtitle').textContent=rate?'Mean of yearly selected-week cases per 100,000 total residents. Each year uses its own DANE population.':'Circle area is proportional to recorded cases summed across the selected years and weeks.';
 const fill=d=>{if(val(d)===null)return 'url(#missing)';if(!rate)return '#e4ece9';const f=val(d)/max;return `rgb(${Math.round(229-207*f)},${Math.round(241-134*f)},${Math.round(237-125*f)})`;};
 const paths=map.map(d=>`<path class="department-shape${d.code===state.department?' selected':''}" data-code="${d.code}" d="${d.path}" fill="${fill(d)}" tabindex="0" role="button" aria-label="${escape(d.name)}, ${rate?dec(val(d)):fmt(val(d))}${rate?' per 100,000 (mean)':' recorded cases'}" aria-pressed="${d.code===state.department}"><title>${escape(d.name)}: ${rate?dec(val(d)):fmt(val(d))}; ${d.present}/${d.expected} week cells present</title></path>`).join('');
 const dots=rate?'':map.filter(d=>d.cases!==null).sort((a,b)=>b.cases-a.cases).map(d=>`<circle class="map-dot${d.code===state.department?' selected':''}" cx="${d.x}" cy="${d.y}" r="${Math.sqrt(d.cases/max)*24}"/>`).join('');
 $('map-container').innerHTML=`<svg viewBox="0 0 560 600" aria-label="Colombia departmental map" role="group"><defs><pattern id="missing" patternUnits="userSpaceOnUse" width="5" height="5"><rect width="5" height="5" fill="#e5e6e4"/><path d="M0,5 L5,0" stroke="#919b98" stroke-width="1"/></pattern></defs>${paths}${dots}<text x="16" y="575" font-size="10" fill="#52666d">San Andrés / Providencia shown at true geographic position</text></svg>`;
 $('map-container').querySelectorAll('path[data-code]').forEach(p=>{p.addEventListener('click',()=>selectDepartment(p.dataset.code));p.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selectDepartment(p.dataset.code);}});});
 $('map-legend').innerHTML=rate?`<span style="display:inline-block;width:100px;height:10px;background:linear-gradient(90deg,#e5f1ed,#166b70)"></span> 0–${dec(max)} per 100,000 · <span class="legend-swatch" style="background:repeating-linear-gradient(135deg,#e5e6e4,#e5e6e4 3px,#919b98 4px)"></span>No usable value`:`<svg width="106" height="54" viewBox="0 0 106 54" aria-hidden="true"><circle cx="28" cy="27" r="24" fill="#166b70" fill-opacity=".58"/><circle cx="77" cy="27" r="12" fill="#166b70" fill-opacity=".58"/></svg> ${fmt(max)} / ${fmt(Math.round(max/4))} cases · Hatched: no usable value`;
 const ranked=[...map].sort((a,b)=>(val(b)??-1)-(val(a)??-1));
 $('rank-description').textContent=rate?'Mean across the selected years, using only the selected weeks. This is not an official dengue incidence measure.':'All 33 department-level units; Bogotá remains unavailable. Select a row to inspect its weeks.';
 $('rank-table').innerHTML=ranked.map(d=>`<div class="rank-row"><button type="button" data-code="${d.code}" aria-pressed="${d.code===state.department}">${escape(d.name)}</button><div class="rank-bar"><span style="width:${val(d)===null?0:100*val(d)/max}%"></span></div><span class="rank-number">${rate?dec(val(d)):fmt(val(d))}</span></div>`).join('');
 $('rank-table').querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>selectDepartment(b.dataset.code)));
}
const layout=()=>({font:{family:'system-ui, sans-serif',size:12,color:'#14333d'},paper_bgcolor:'transparent',plot_bgcolor:'transparent',margin:{l:60,r:20,t:20,b:65},xaxis:{showgrid:false,zeroline:false},yaxis:{title:{text:'Recorded cases'},rangemode:'tozero',gridcolor:'#e0e7e5',zerolinecolor:'#a6b8b6'},showlegend:false,hovermode:'closest',dragmode:false});
const config={responsive:true,displayModeBar:false,scrollZoom:false};
async function renderPlots(){
 const series=timeSeries(data,state),any=series.some(r=>r.cases!==null),name=state.department==='all'?'Available department records':data.departments.find(d=>d.code===state.department).name;
 $('time-description').textContent=`${name} · ${state.event==='210'?'Dengue (210)':'Severe dengue (220)'} · Source epidemiological year and week.`;
 $('season-description').textContent=`${name} · ${state.start}–${state.end} · Selected weeks ${state.first}–${state.last}.`;
 if(!any){for(const id of ['timeline','seasonal']){Plotly.purge($(id));$(id).innerHTML='<div class="empty-state">No source rows for this selection. No zero is inferred.<br>Choose another department or period, or use Reset.</div>';}return;}
 const token=renderToken;
 for(const id of ['timeline','seasonal'])if(!$(id).classList.contains('js-plotly-plot'))$(id).innerHTML='';
 const tick=series.filter((r,i)=>i===0||r.week===1||r.week===26),l=layout();l.xaxis={...l.xaxis,tickvals:tick.map(r=>r.label),ticktext:tick.map(r=>`${r.year} W${r.week}`),title:{text:'Source epidemiological year / week'}};
 await Plotly.react($('timeline'),[{x:series.map(r=>r.label),y:series.map(r=>r.cases),type:'scatter',mode:'lines+markers',marker:{size:3,color:'#166b70'},connectgaps:false,line:{color:'#166b70',width:2},customdata:series.map(r=>`${r.present}/${r.expected} department cells present`),hovertemplate:'%{x}<br>%{y:,} recorded cases<br>%{customdata}<extra></extra>'},{x:series.filter(r=>r.present<r.expected&&r.cases!==null).map(r=>r.label),y:series.filter(r=>r.present<r.expected&&r.cases!==null).map(r=>r.cases),type:'scatter',mode:'markers',marker:{color:'#a65b24',size:4,symbol:'circle-open'},hoverinfo:'skip'}],l,config);
 if(token!==renderToken)return;
 const sl=layout();sl.showlegend=true;sl.legend={orientation:'h',x:0,y:1.17};sl.margin.t=45;sl.xaxis={...sl.xaxis,title:{text:'Source epidemiological week'},range:[Math.max(.5,state.first-.5),Math.min(53.5,state.last+.5)],dtick:state.last-state.first>20?8:2};
 const traces=[];for(let year=state.start;year<=state.end;year++){const rows=series.filter(r=>r.year===year);if(rows.length)traces.push({name:String(year),x:rows.map(r=>r.week),y:rows.map(r=>r.cases),type:'scatter',mode:'lines+markers',marker:{size:3,color:colors[year]},connectgaps:false,line:{color:colors[year],width:2,dash:year===2021?'dash':'solid'},hovertemplate:`${year} W%{x}<br>%{y:,} recorded cases<extra></extra>`});}
 await Plotly.react($('seasonal'),traces,sl,config);
}
function renderTable(){
 latestSummary=summaries(data,state);latestWeekly=selectedRows(data,state).map(r=>({...r,snapshot_date:data.meta.snapshot_date,source_url:data.meta.source_url,time_basis:'source epidemiological week; onset/notification unresolved',location_basis:'occurrence/procedence',count_unit:'recorded cases'}));
 $('download').disabled=!latestSummary.length;$('download-weekly').disabled=!latestWeekly.length;
 $('table-description').textContent=`${latestSummary.length} department-year rows for the current geographic and time filters. Blank CSV values mean unavailable; zeros, if reported, remain 0. Rates below use each row’s year-specific DANE total population, not official population-at-risk incidence. Scroll the table horizontally on smaller screens.`;
 $('summary-table').innerHTML=latestSummary.length?`<table><caption class="visually-hidden">Filtered department-year summaries; cases are sums of available source records.</caption><thead><tr><th>Department</th><th>Year</th><th class="numeric">Recorded cases</th><th class="numeric">Population</th><th class="numeric">Cases per 100,000 residents</th><th>Weeks present</th><th>Availability</th></tr></thead><tbody>${latestSummary.map(r=>`<tr><td>${escape(r.department_name)}</td><td>${r.year}</td><td class="numeric">${fmt(r.cases)}</td><td class="numeric">${fmt(r.population_total)}</td><td class="numeric">${dec(r.cases_per_100k)}</td><td>${r.source_present_weeks}/${r.expected_weeks}</td><td>${r.availability==='no_source_rows'?'No source rows':r.availability==='partial_week_cells'?'Some weeks absent':'All week cells present'}</td></tr>`).join('')}</tbody></table>`:'<div class="empty-state">No periods match this selection. Set the first year/week before the last, or use Reset.</div>';
 const total=sumPresent(latestSummary.map(r=>r.cases)),present=latestSummary.reduce((a,r)=>a+r.source_present_weeks,0),expected=latestSummary.reduce((a,r)=>a+r.expected_weeks,0);
 $('kpi-cases').textContent=fmt(total);$('kpi-event').textContent=state.event==='210'?'Dengue · INS event 210':'Severe dengue · INS event 220';$('kpi-availability').textContent=`${fmt(present)} / ${fmt(expected)}`;
 $('scope-note').textContent=total===null?'No usable source rows in this selection. Absence is not evidence of zero cases.':`${fmt(expected-present)} department-week cells have no source row. Counts sum the available records; field availability does not measure surveillance reporting completeness. ${state.department==='all'?'Bogotá is unavailable and does not contribute to the count.':''}`;
 $('provenance-content').innerHTML=`<ul><li>Surveillance: <a href="${data.meta.source_url}">INS / Sivigila historical aggregates</a>, CC BY-SA 4.0. Retrieved ${data.meta.snapshot_date}; dataset last updated ${data.meta.source_data_updated_utc.slice(0,10)}.</li><li>Geography: 32 departments plus Bogotá D.C. District municipality records are included once in their parent department; foreign and unknown geography are excluded.</li><li>Time: source epidemiological year/week, 52 weeks in 2019/2021/2022 and 53 in 2020. The metadata does not settle symptom onset versus notification date.</li><li>Population: DANE’s 2025 revision, matched by department and year. Annual table rate = available cases ÷ annual total population × 100,000. A multiyear map shows the arithmetic mean of these yearly rates, and requires a usable numerator and denominator for every selected year. Restricting weeks does not annualize the result.</li><li>Case status: INS describes the routine series as confirmed notifications; this extract has no individual classification fields. Events 210 and 220 are shown separately.</li></ul>`;
}
async function render(){
 const current=++renderToken;$('atlas').setAttribute('aria-busy','true');
 const name=state.department==='all'?'All department-level units':data.departments.find(d=>d.code===state.department).name;
 $('selection').textContent=`${name} · Event ${state.event} · ${state.start}–${state.end} · Weeks ${state.first}–${state.last} · Map: ${state.metric==='rate'?'mean yearly selected-week cases per 100,000':'recorded cases'}`;
 renderMap();renderTable();await renderPlots();if(current===renderToken){$('atlas').setAttribute('aria-busy','false');window.atlasReady=true;}
}
async function boot(){
 const response=await fetch('data/atlas.json');if(!response.ok)throw Error(`Data request returned ${response.status}`);data=await response.json();
 $('department').innerHTML='<option value="all">All departments + Bogotá</option>'+data.departments.map(d=>`<option value="${d.code}">${escape(d.name)}</option>`).join('');
 for(const id of ['year-start','year-end'])$(id).innerHTML=[2019,2020,2021,2022].map(y=>`<option>${y}</option>`).join('');
 state=readState(location.search,data.departments.map(d=>d.code));setControls();
 $('filters').addEventListener('submit',e=>e.preventDefault());
 for(const[k,id]of Object.entries(bindings))$(id).addEventListener('change',()=>{state[k]=typeof defaults[k]==='number'?Number($(id).value):$(id).value;state=readState(new URLSearchParams(state),data.departments.map(d=>d.code));setControls();history.pushState(null,'',stateUrl());render();});
 $('reset').addEventListener('click',()=>{state={...defaults};setControls();history.pushState(null,'',location.pathname);render();});
 window.addEventListener('popstate',()=>{state=readState(location.search,data.departments.map(d=>d.code));setControls();render();});
 $('download').addEventListener('click',()=>download(latestSummary,'summary'));$('download-weekly').addEventListener('click',()=>download(latestWeekly,'weekly'));
 await render();
}
boot().catch(e=>{$('app-error').hidden=false;$('app-error').textContent=`The atlas could not load. Reload the page or use the CSV files on Data & sources. Details: ${e.message}`;$('atlas').setAttribute('aria-busy','false');console.error(e);});
