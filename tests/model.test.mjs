import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {defaults,readState,sumPresent,selectedRows,summaries,mapSummaries,timeSeries,csv} from '../site/assets/model.mjs';

// These tests use the release's actual built payload and pinned public aggregates.
// Tiny copies with a removed denominator or an explicit zero are test fixtures only.
const root = new URL('../', import.meta.url);
const read = path => JSON.parse(readFileSync(new URL(path,root),'utf8'));
const data = read('site/data/atlas.json');
const raw = [2019,2020,2021,2022].flatMap(y=>read(`data/raw/ins_dengue_${y}.json`));
const codes = data.departments.map(d=>d.code);
const state = changes => ({...defaults,...changes});
const rawCount = s => {
  const present = raw.filter(r=>String(r.cod_eve)===s.event && Number(r.ano)>=s.start && Number(r.ano)<=s.end && Number(r.semana)>=s.first && Number(r.semana)<=s.last && codes.includes(String(Number(r.cod_dpto_o)).padStart(2,'0')) && (s.department==='all'||String(Number(r.cod_dpto_o)).padStart(2,'0')===s.department));
  return present.length ? present.reduce((total,r)=>total+Number(r.conteo),0) : null;
};
function parseCsv(text) {
  const rows=[]; let row=[],cell='',quoted=false;
  for(let i=0;i<text.length;i++) {
    const ch=text[i];
    if(ch==='"') {
      if(quoted && text[i+1]==='"'){cell+='"';i++;} else quoted=!quoted;
    } else if(ch===','&&!quoted){row.push(cell);cell='';}
    else if(ch==='\r'&&!quoted&&text[i+1]==='\n'){row.push(cell);rows.push(row);row=[];cell='';i++;}
    else cell+=ch;
  }
  if(cell||row.length){row.push(cell);rows.push(row);}
  return rows;
}

test('release payload preserves the complete null-bearing 33-unit grid',()=>{
  assert.equal(data.rows.length,13794);
  assert.equal(new Set(codes).size,33);
  assert.equal(data.rows.filter(r=>r.cases!==null).length,8130);
  assert.equal(data.rows.filter(r=>r.cases===null).length,5664);
  assert.equal(data.rows.filter(r=>r.cases===0).length,0);
  assert.ok(!codes.includes('00')&&!codes.includes('01'));
});

test('both event categories independently reconcile with original source rows',()=>{
  for(const [event,total] of [['210',313814],['220',4461]]) {
    const s=state({event});
    assert.equal(rawCount(s),total);
    assert.equal(sumPresent(summaries(data,s).map(r=>r.cases)),total);
    assert.equal(sumPresent(mapSummaries(data,s).map(r=>r.cases)),total);
    assert.equal(sumPresent(timeSeries(data,s).map(r=>r.cases)),total);
    assert.ok(selectedRows(data,s).every(r=>r.event_code===event));
  }
});

test('a selected territory and partial season agree with independent raw counts',()=>{
  for(const event of ['210','220']) {
    const s=state({department:'50',event,start:2019,end:2021,first:7,last:21});
    const table=summaries(data,s);
    assert.equal(table.length,3);
    assert.ok(table.every(r=>r.department_code==='50'&&r.first_week===7&&r.last_week===21));
    assert.equal(sumPresent(table.map(r=>r.cases)),rawCount(s));
    assert.equal(sumPresent(timeSeries(data,s).map(r=>r.cases)),rawCount(s));
    for(const row of table) assert.equal(row.cases,rawCount({...s,start:row.year,end:row.year}));
  }
});

test('Bogota keeps unavailable numerators despite available populations',()=>{
  const s=state({department:'11'}), table=summaries(data,s);
  assert.equal(table.length,4);
  assert.ok(table.every(r=>r.cases===null&&r.cases_per_100k===null&&r.population_total>0&&r.availability==='no_source_rows'));
  assert.ok(timeSeries(data,s).every(r=>r.cases===null));
  const map=mapSummaries(data,s).find(r=>r.code==='11');
  assert.equal(map.cases,null); assert.equal(map.rate,null); assert.equal(map.present,0);
});

test('year-specific rates use matching DANE denominator and mean yearly rates',()=>{
  const s=state({department:'05',first:3,last:17,metric:'rate'}), table=summaries(data,s);
  const independentRates=table.map(r=>{
    const count=rawCount({...s,start:r.year,end:r.year});
    const population=data.population[`05-${r.year}`];
    assert.equal(r.population_total,population);
    assert.equal(r.cases_per_100k,count/population*100000);
    return count/population*100000;
  });
  const expected=independentRates.reduce((a,b)=>a+b,0)/4;
  const map=mapSummaries(data,s).find(r=>r.code==='05');
  assert.equal(map.rate,expected);
  assert.equal(map.cases,rawCount(s));
});

test('missing a single annual denominator disables the multiyear rate only',()=>{
  const fixture={...data,population:{...data.population}};
  delete fixture.population['05-2020'];
  const s=state({department:'05',metric:'rate'});
  const map=mapSummaries(fixture,s).find(r=>r.code==='05');
  assert.equal(map.rate,null);
  assert.equal(map.cases,rawCount(s));
  assert.equal(summaries(fixture,s).find(r=>r.year===2020).cases_per_100k,null);
});

test('null source cells stay absent and never count as explicit zero weeks',()=>{
  const s=state({department:'97',event:'220',start:2021,end:2021});
  const table=summaries(data,s)[0];
  assert.equal(table.cases,null);
  assert.equal(table.source_absent_weeks,52);
  assert.equal(table.explicit_zero_weeks,0);
  assert.equal(table.availability,'no_source_rows');
  assert.ok(timeSeries(data,s).every(r=>r.cases===null));
});

test('explicit zero test fixture remains a numeric zero in model and CSV',()=>{
  assert.equal(sumPresent([null,null]),null);
  assert.equal(sumPresent([null,0]),0);
  const original=data.rows.find(r=>r.department_code==='05'&&r.year===2019&&r.week===1&&r.event_code==='210');
  const fixture={...data,rows:[{...original,cases:0,observation_status:'explicit_zero'}]};
  const table=summaries(fixture,state({department:'05',start:2019,end:2019,first:1,last:1}));
  assert.equal(table[0].cases,0); assert.equal(table[0].cases_per_100k,0);
  assert.equal(table[0].explicit_zero_weeks,1);
  const records=parseCsv(csv(table));
  assert.equal(records[1][records[0].indexOf('cases')],'0');
});

test('week 53 appears only in 2020 without inventing other years',()=>{
  const s=state({first:53,last:53,metric:'rate'}), rows=selectedRows(data,s), table=summaries(data,s);
  assert.equal(rows.length,33); assert.ok(rows.every(r=>r.year===2020&&r.week===53));
  assert.equal(table.length,33); assert.ok(table.every(r=>r.expected_weeks===1));
  assert.equal(timeSeries(data,s).length,1);
  assert.equal(sumPresent(table.map(r=>r.cases)),rawCount(s));
  assert.ok(mapSummaries(data,s).every(r=>r.rate===null));
  for(const row of mapSummaries(data,{...s,start:2020,end:2020})) {
    const annual=table.find(r=>r.department_code===row.code);
    assert.equal(row.rate,annual.cases_per_100k);
  }
});

test('invalid temporal order produces empty exports and null map values',()=>{
  for(const changes of [{start:2020,end:2019},{start:2022,end:2019},{first:30,last:12}]){
    const s=state({...changes,metric:'rate'});
    assert.deepEqual(selectedRows(data,s),[]);
    assert.deepEqual(summaries(data,s),[]);
    assert.deepEqual(timeSeries(data,s),[]);
    assert.equal(csv(summaries(data,s)),'');
    assert.ok(mapSummaries(data,s).every(r=>r.cases===null&&r.rate===null));
  }
});

test('map context is independent of the selected department, tables are filtered',()=>{
  const a=state({event:'220',start:2022,end:2022,first:10,last:20});
  const b={...a,department:'13'};
  assert.deepEqual(mapSummaries(data,a),mapSummaries(data,b));
  assert.ok(summaries(data,b).every(r=>r.department_code==='13'));
  assert.equal(sumPresent(summaries(data,b).map(r=>r.cases)),rawCount(b));
});

test('CSV preserves filter metadata, exact calculated values, and unavailable blanks',()=>{
  const s=state({event:'220',start:2020,end:2021,first:12,last:18});
  const table=summaries(data,s), parsed=parseCsv(csv(table)), header=parsed[0];
  assert.equal(parsed.length,table.length+1);
  assert.ok(header.includes('source_url')&&header.includes('population_version')&&header.includes('rate_unit'));
  for(let i=0;i<table.length;i++) {
    for(let j=0;j<header.length;j++) assert.equal(parsed[i+1][j],table[i][header[j]]===null?'':String(table[i][header[j]]));
    assert.equal(table[i].cases,rawCount({...s,department:table[i].department_code,start:table[i].year,end:table[i].year}));
  }
  assert.ok(!csv(table).includes('NaN')&&!csv(table).includes('undefined'));
});

test('URL parsing rejects unknown fields and preserves inverted ranges for empty state',()=>{
  const invalid=readState('?department=bad&event=999&start=abc&end=2099&first=0&last=54&metric=incidence',codes);
  assert.deepEqual(invalid,defaults);
  const inverted=readState('?department=08&event=220&start=2020&end=2019&first=53&last=53&metric=rate',codes);
  assert.equal(inverted.department,'08');assert.equal(inverted.start,2020);assert.equal(inverted.end,2019);
  assert.equal(inverted.first,53); assert.equal(inverted.event,'220');
  assert.equal(defaults.department,'all');
});

test('CSV round-trips comma and quote text while protecting formula prefixes',()=>{
  const parsed=parseCsv(csv([{name:'Bogotá, D.C.',detail:'A "quoted" label',formula:'=1+1',count:0,absent:null}]));
  assert.deepEqual(parsed[1],['Bogotá, D.C.','A "quoted" label',"'=1+1",'0','']);
});

