import requests

BASE = 'http://localhost:8080'
endpoints = [
    '/cards/base1-4/image/small',
    '/cards/base1-4/image/large',
    '/sets/base1/symbol',
    '/sets/base1/logo'
]

for ep in endpoints:
    try:
        r = requests.get(BASE+ep, allow_redirects=False, timeout=5)
        print(ep, '->', r.status_code, r.headers.get('location'))
    except Exception as e:
        print(ep, 'ERROR', e)
