"""Read-only checks on J-PACT's cached DeepSeek Stego readouts and steering logits (no model, no GPU).
Usage (from projects/jpact):  python3 -I checks/stego_checks.py data/cache
Needs interp/stego.json, interp/stego_swap.json, interp/vocab.json from the jpact-cache HF dataset."""
import json, sys, collections, statistics as S
C = sys.argv[1]
V = json.load(open(f'{C}/interp/vocab.json'))['text']
st = json.load(open(f'{C}/interp/stego.json'))['rows']
sw = {(r['run'], r['hand']): r for r in json.load(open(f'{C}/interp/stego_swap.json'))['rows']}
SIG = {'NEGATIVE': {'negative','cold','low','0','消极'}, 'NEUTRAL': {'neutral','moderate','consistency','不变','又一次'},
       'HOT': {'hot','positive','high','increment','increments','nonsense','atypical','misguided'}}   # config.py RANGE_SIGNATURES
NAMES = {'NEGATIVE': {'negative'}, 'NEUTRAL': {'neutral'}, 'HOT': {'hot'}}
bag = lambda top: {V[i].lower() for l in range(19, 39) for i in top[str(l)]}
print('1. Fig 2c matrix with the paper signatures, then with the bare range names only')
for label, sets in (('signatures', SIG), ('range names only', NAMES)):
    for who in ('receiver', 'receiver_honest'):
        for t in SIG:
            rs = [r for r in st if r['range'] == t]
            print(f'  {label:16s} {who:16s} true {t:8s} n={len(rs)}',
                  {g: round(sum(bool(bag(r[who]['message_end']) & sets[g]) for r in rs) / len(rs), 2) for g in sets})
lab = {(r['run'], r['hand']): r['range'] for r in st}
print('2. Previous hand labels are in the receiver prompt; split hands by whether the range changed')
d = collections.Counter()
for r in st:
    k = (r['run'], r['hand']); g = 'hand1' if k[1] == 1 else ('same' if lab[k] == lab[(k[0], k[1]-1)] else 'changed')
    b = bag(r['receiver']['message_end']); d[g, 'n'] += 1; d[g, 'true'] += bool(b & SIG[r['range']])
    if k[1] > 1: d[g, 'prev'] += bool(b & SIG[lab[(k[0], k[1]-1)]])
for g in ('hand1', 'same', 'changed'):
    print(f'  {g:8s} n={d[g,"n"]} holds true-range signature {d[g,"true"]}, holds previous-range signature {d[g,"prev"]}')
print('3. Steering: mean shift of (HOT - NEGATIVE) logit vs no swap, by true range and arm')
for t in SIG:
    rs = [r for k, r in sw.items() if r['range'] == t]
    print(f'  {t:8s}', {a: round(S.mean((r[a]['HOT']-r[a]['NEGATIVE']) - (r['alpha_0.0']['HOT']-r['alpha_0.0']['NEGATIVE']) for r in rs), 2)
                        for a in ('alpha_1.0', 'alpha_1.25', 'random_0', 'random_1', 'random_2')})
