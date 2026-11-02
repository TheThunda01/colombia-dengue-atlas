"""Check generated local links and self-hosted assets, without network access."""
from pathlib import Path
from urllib.parse import unquote, urlparse
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]/'site/_site'
checked=0
for path in ROOT.glob('*.html'):
    soup=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
    for element in soup.select('a[href],script[src],img[src],link[href]'):
        value=element.get('href',element.get('src',''))
        url=urlparse(value)
        if url.scheme or value.startswith('//') or not url.path:
            continue
        assert not url.path.startswith('/'),f'Root-relative asset breaks project hosting: {path.name}: {value}'
        target=path.parent/unquote(url.path)
        assert target.exists(),f'Broken local link: {path.name}: {value}'
        checked+=1
    for script in soup.select('script[src]'):
        assert not urlparse(script['src']).scheme,'External script dependency'
print(f'Checked {checked} local references and self-hosted scripts across4 rendered pages.')
