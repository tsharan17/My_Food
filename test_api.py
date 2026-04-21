import urllib.request, json

base = 'http://127.0.0.1:5000'

def post(path, payload):
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(base + path, data=data,
                                   headers={'Content-Type': 'application/json'})
    res  = urllib.request.urlopen(req)
    return json.loads(res.read())

def get(path):
    res = urllib.request.urlopen(base + path)
    return json.loads(res.read())

print('=' * 55)
print('NUTRIGUARD  --  API TEST SUITE')
print('=' * 55)

# ── Test 1: Health check ─────────────────────
r = get('/health')
print('[1] Health check:', r)

# ── Test 2: Set condition ────────────────────
r = post('/api/set_condition', {'condition': 'weight_loss'})
print('[2] Set condition:', r)

# ── Test 3: Analyse banana BEFORE eating ─────
r = post('/api/analyze', {'food': 'banana', 'portion': 1,
                           'health_condition': 'weight_loss'})
n = r['nutrition']
rec = r['recommendation']
ana = r['analysis']
print('[3] Analyse banana (before / weight_loss):')
print('    Calories :', n['calories'], 'kcal')
print('    Protein  :', n['protein'], 'g')
print('    Score    :', rec['health_score'], '/ 10  (', rec['score_label'], ')')
print('    Severity :', ana['severity'])

# ── Test 4: Log pizza x2 (diabetes) ─────────
r = post('/api/log', {'food': 'pizza', 'portion': 2,
                       'health_condition': 'diabetes'})
n   = r['nutrition']
rec = r['recommendation']
ana = r['analysis']
print('[4] Log pizza x2 (diabetes):')
print('    Calories :', n['calories'], 'kcal')
print('    Score    :', rec['health_score'], '/ 10  (', rec['score_label'], ')')
print('    Severity :', ana['severity'])
print('    Warnings :', rec['warnings'][:2])

# ── Test 5: Log salad (general) ──────────────
r   = post('/api/log', {'food': 'salad', 'portion': 1,
                         'health_condition': 'general'})
rec = r['recommendation']
ana = r['analysis']
print('[5] Log salad (general):')
print('    Score    :', rec['health_score'], '/ 10  (', rec['score_label'], ')')
print('    Severity :', ana['severity'])
print('    Positives:', rec['positives'][:2])

# ── Test 6: Daily summary ────────────────────
r = get('/api/daily_summary')
t = r['totals']
print('[6] Daily summary:')
print('    Calories :', t['calories'], 'kcal')
print('    Protein  :', t['protein'], 'g')
print('    Items    :', r['entry_count'])
print('    Day Score:', r['health_score'])

# ── Test 7: Weekly summary ───────────────────
r = get('/api/weekly_summary')
print('[7] Weekly summary: returned', len(r['weekly']), 'days')

# ── Test 8: Unknown food ─────────────────────
try:
    r = post('/api/analyze', {'food': 'xyz_unknown', 'portion': 1,
                               'health_condition': 'general'})
    print('[8] Unknown food: SHOULD HAVE ERRORED')
except Exception as e:
    print('[8] Unknown food correctly returned error:', str(e)[:60])

# ── Test 9: Clear today ──────────────────────
r = post('/api/clear_today', {})
print('[9] Clear today:', r)

print('=' * 55)
print('ALL TESTS COMPLETE')
print('=' * 55)
