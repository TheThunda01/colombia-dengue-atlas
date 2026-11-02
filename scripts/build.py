"""Build the browser data bundle, publication figure and Quarto site offline.

--prepare re-extracts the original inputs first; missing DANE inputs are fetched
only with their pinned checksums. The default uses committed processed data.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from plotly.offline import get_plotlyjs
from cartographic_plate import build_plate

ROOT = Path(__file__).resolve().parents[1]


def geometry_paths(frame: gpd.GeoDataFrame) -> list[dict]:
    """Project display geometry; data joins always use codes, never coordinates."""
    frame = frame.to_crs(9377)
    xmin, ymin, xmax, ymax = frame.total_bounds
    scale = min(520 / (xmax - xmin), 530 / (ymax - ymin))
    xpad, ypad = (560 - (xmax - xmin)*scale)/2, 12
    def xy(x, y):
        return round(xpad+(x-xmin)*scale, 2), round(ypad+(ymax-y)*scale, 2)
    result=[]
    for row in frame.itertuples():
        geom=row.geometry
        polygons=list(geom.geoms) if geom.geom_type=='MultiPolygon' else [geom]
        pieces=[]
        for polygon in polygons:
            for ring in [polygon.exterior,*polygon.interiors]:
                points=[xy(x,y) for x,y,*_ in ring.coords]
                pieces.append('M'+'L'.join(f'{x},{y}' for x,y in points)+'Z')
        anchor=geom.representative_point()
        x,y=xy(anchor.x,anchor.y)
        result.append({'code':row.department_code,'name':row.department_name,
                       'path':''.join(pieces),'x':x,'y':y})
    return result


def bundle() -> dict:
    processed=ROOT/'data/processed'
    rows=json.loads((processed/'surveillance_weekly.json').read_text(encoding='utf-8'))
    population=pd.read_csv(processed/'population.csv',dtype={'department_code':str})
    geo=gpd.read_file(processed/'departments.geojson')
    meta=json.loads((processed/'surveillance_audit.json').read_text(encoding='utf-8'))
    assert len(rows)==13794 and len(population)==132 and len(geo)==33
    assert set(geo.department_code)==set(population.department_code)=={r['department_code'] for r in rows}
    pop={f'{r.department_code}-{r.year}':int(r.population) for r in population.itertuples()}
    assert all(v>0 for v in pop.values())
    payload={'meta':{k:meta[k] for k in ['source_id','snapshot_date','source_title','source_url','source_data_updated_utc','license']},
             'rows':rows,'population':pop,'departments':geometry_paths(geo)}
    output=ROOT/'site/data';output.mkdir(exist_ok=True)
    (output/'atlas.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':'),allow_nan=False),encoding='utf-8')
    for name in ['surveillance_weekly.csv','population.csv','departments.geojson','surveillance_audit.json']:
        shutil.copyfile(processed/name,output/name)
    (ROOT/'site/assets/plotly.min.js').write_text(get_plotlyjs(),encoding='utf-8')
    # Check the source-level dataframe against bundle serialization.
    assert sum(r['cases'] or 0 for r in rows if r['event_code']=='210')==313814
    report={'surveillance_cells':len(rows),'population_rows':len(population),'mapped_units':len(geo),
            'unmatched_geographic_codes':0,'invalid_json_numbers':0,
            'atlas_bytes':(output/'atlas.json').stat().st_size,
            'inputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in processed.iterdir() if p.is_file()},
            'browser_data_sha256':hashlib.sha256((output/'atlas.json').read_bytes()).hexdigest()}
    (ROOT/'reports/build_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    return payload


def figure(payload: dict) -> None:
    frame=pd.DataFrame(payload['rows']);frame=frame[frame.event_code=='210']
    grouped=frame.groupby(['year','week']).cases.sum(min_count=1)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','svg.hashsalt':'colombia-dengue-atlas-v1',
                         'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,2,figsize=(11,6.8),sharex=True,sharey=True)
    colors=['#166b70','#bd632b','#69509b','#3b677f']
    maximum=grouped.max()*1.13
    for ax,year,color in zip(axes.flat,[2019,2020,2021,2022],colors):
        values=grouped.loc[year]
        ax.plot(values.index,values.values,color=color,lw=1.8)
        ax.fill_between(values.index,values.values,0,color=color,alpha=.08)
        ax.set_title(f'{year}  |  {int(values.sum()):,} recorded cases',loc='left',fontsize=11,fontweight='bold')
        ax.set_ylim(0,maximum);ax.set_xlim(1,53);ax.grid(axis='y',color='#e0e7e5',lw=.6)
        ax.set_xticks([1,13,26,39,53]);ax.tick_params(axis='both',length=3)
        ax.spines['left'].set_color('#9aabaa');ax.spines['bottom'].set_color('#9aabaa')
    fig.suptitle('Dengue records across four surveillance years',x=.08,y=.98,ha='left',fontsize=18,fontweight='bold',color='#14333d')
    fig.text(.08,.91,'Colombia · INS event 210 · Weekly sums of available department records',fontsize=11,color='#52666d')
    fig.supxlabel('Source epidemiological week',y=.13);fig.supylabel('Recorded cases',x=.025)
    fig.text(.08,.055,'INS / Sivigila, datos.gov.co/4hyg-wa9d · Snapshot retrieved 2 November 2026 · CC BY-SA 4.0\n'
             '32 departments contribute records; Bogotá is unavailable. Absent department-week rows are not inferred zeros.\n'
             'Closed years do not establish complete capture. Week 53 occurs only in 2020. Figure: Brandon Huynh.',
             fontsize=8,color='#52666d',linespacing=1.5)
    fig.subplots_adjust(left=.08,right=.98,bottom=.23,top=.84,hspace=.38,wspace=.18)
    for ext in ['svg','png','pdf']:
        destination=ROOT/f'figures/weekly-comparison.{ext}'
        metadata={'Creator':'Brandon Huynh; Colombia Dengue Surveillance Atlas'}
        if ext=='svg':metadata['Date']=payload['meta']['snapshot_date']
        if ext=='pdf':
            timestamp=datetime.fromisoformat(payload['meta']['snapshot_date']).replace(tzinfo=timezone.utc)
            metadata.update(CreationDate=timestamp,ModDate=timestamp)
        fig.savefig(destination,dpi=300,facecolor='white',metadata=metadata)
    plt.close(fig)
    (ROOT/'site/figures').mkdir(exist_ok=True)
    for file in (ROOT/'figures').glob('weekly-comparison.*'):
        shutil.copyfile(file,ROOT/'site/figures'/file.name)


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--no-render',action='store_true')
    args=parser.parse_args()
    if args.prepare:
        for script,extra in [('prepare_surveillance.py',[]),('prepare_geography.py',['--download'])]:
            subprocess.run([sys.executable,str(ROOT/'scripts'/script),*extra],cwd=ROOT,check=True)
    plate = build_plate()
    if "inkscape_export" not in plate:
        raise RuntimeError("Map exports do not match the generated SVG. Run scripts/cartographic_plate.py --inkscape PATH before publishing.")
    payload=bundle();figure(payload)
    shutil.copyfile(ROOT/'data/processed/map_comparison.csv', ROOT/'site/data/map_comparison.csv')
    for file in (ROOT/'figures').glob('map-comparison.*'):
        shutil.copyfile(file, ROOT/'site/figures'/file.name)
    if not args.no_render:
        subprocess.run([sys.executable,str(ROOT/'scripts/site.py'),'render'],cwd=ROOT,check=True)
    print('Built 13,794 surveillance cells, 132 denominators, 33 map units and two SVG/PNG/PDF figures.')


if __name__=='__main__':
    main()
