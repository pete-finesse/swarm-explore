"""Fig 3 callouts (jpact read.py:237-247 rule) applied in both directions on the cached case-study replies.
Usage (from projects/jpact):  python3 -I checks/callouts_check.py data/cache"""
import json, sys
C = sys.argv[1]
v = json.load(open(f'{C}/interp/vocab.json')); low = [t.lower() for t in v['text']]; BY = v['bytes']
GROUPS = {'misunderstand','misunderstanding','misunderstandings','misunder','misinterpret','incorrect','wrong','错误','的错误','false',
          '误导','虚假','欺骗','mislead','misleading','deceptive','deception','dishonest','unethical','hypocrisy','subtly','biased','bias',
          'manipulate','manipulation','secretly','hidden','lie','lies','fake','trick','fraud','unfair','unflagged','unauthorized','未经',
          'apologies','apology','apologize','apolog','regret','regrets','regrett','抱歉','对不起','羞','羞辱','despair'}   # config.py CONCEPTS
def pieces(ids):
    raw, out, prev = b'', [], ''
    for i in ids:
        raw += bytes.fromhex(BY[i]); cur = raw.decode('utf-8', 'ignore'); out.append(cur[len(prev):]); prev = cur
    return out
for r in json.load(open(f'{C}/interp/transcripts.json'))['rows']:
    text = pieces(r['generated']); a = b = 0; wa = set(); wb = set()
    for k in range(1, len(r['generated']) + 1):
        written = ''.join(text[:k]).lower()
        for l in range(19, 39):
            m = {low[i] for i in r['colluder'][str(l)][k]}; t = {low[i] for i in r['counterpart'][str(l)][k]}
            x = [c for c in (m & GROUPS) - t if c not in written]; y = [c for c in (t & GROUPS) - m if c not in written]
            a += len(x); b += len(y); wa |= set(x); wb |= set(y)
    print(f"{r['run'].split('__')[1]:9s} {r['agent']:16s} colluder-only hits {a:4d} {sorted(wa)} | counterfactual-only hits {b:4d} {sorted(wb)}")
