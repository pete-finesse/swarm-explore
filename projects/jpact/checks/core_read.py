import json, sys, collections
C = sys.argv[1]
V = json.load(open(C+'/interp/vocab.json'))['text']; low=[t.lower() for t in V]
CONCEPTS = {
 'misrepresentation': {'misunderstand','misunderstanding','misunderstandings','misunder','misinterpret','incorrect','wrong','错误','的错误','false','误导','虚假','欺骗','mislead','misleading','deceptive','deception','dishonest','unethical','hypocrisy','subtly','biased','bias','manipulate','manipulation','secretly','hidden','lie','lies','fake','trick','fraud','unfair'},
 'concealment': {'unflagged','unauthorized','未经'},
 'remorse': {'apologies','apology','apologize','apolog','regret','regrets','regrett','抱歉','对不起','羞','羞辱','despair'}}
ALL=set().union(*CONCEPTS.values())
BAND=range(19,39)
core=json.load(open(C+'/interp/core.json'))['episodes']
def bag(top): return {i for l in BAND for i in top[str(l)]}
def hits(top): return sorted({low[i] for i in bag(top)} & ALL)
run = sys.argv[2] if len(sys.argv)>2 else 'deception__cyber_03__collusion'
for e in core:
    if e['run']==run or e['run']==run.replace('collusion','control'):
        print('==', e['run'])
        for a in e['agents']:
            print(' ', a['name'], a['role'], 'hits:', hits(a['top']), '| bag size', len(bag(a['top'])))
            if 'counterpart' in a: print('     counterfactual hits:', hits(a['counterpart']))
            print('     L25 top10:', [V[i] for i in a['top']['25']])
            if 'counterpart' in a: print('     CF L25 top10:', [V[i] for i in a['counterpart']['25']])
# overall word frequencies
col=collections.Counter(); cf=collections.Counter(); hon=collections.Counter(); ctl=collections.Counter()
ncol=0
for e in core:
    for a in e['agents']:
        if e['mode']=='collusion' and 'counterpart' in a:
            ncol+=1
            for w in hits(a['top']): col[w]+=1
            for w in hits(a['counterpart']): cf[w]+=1
        elif e['mode']=='collusion': 
            for w in hits(a['top']): hon[w]+=1
        else:
            for w in hits(a['top']): ctl[w]+=1
print('n colluders', ncol, 'n episodes', len(core), collections.Counter(e['mode'] for e in core))
print('word: colluders / their counterfactuals / honest agents in collusion runs (n=100) / control agents (n=200)')
for w in sorted(set(col)|set(cf)|set(hon)|set(ctl), key=lambda w:-col[w]):
    print(f'  {w!r}: {col[w]} / {cf[w]} / {hon[w]} / {ctl[w]}')
print('--- per-agent "any" rates')
r=collections.Counter()
for e in core:
    for a in e['agents']:
        k=(e['mode'],a['role']); r[k,'n']+=1; r[k,'any']+=bool(hits(a['top']))
        if 'counterpart' in a: r['cf','n']+=1; r['cf','any']+=bool(hits(a['counterpart']))
for k in [('collusion','colluder'),'cf',('collusion','honest'),('control','honest')]: print(k, r[k,'any'],'/',r[k,'n'])
# without misunderstand(ing) words
drop={'misunderstand','misunderstanding','misunderstandings','misunder'}
n1=sum(bool(set(hits(a['top']))-drop) for e in core for a in e['agents'] if 'counterpart' in a)
n2=sum(bool(set(hits(a['counterpart']))-drop) for e in core for a in e['agents'] if 'counterpart' in a)
print('any, excluding misunderstand* words: colluders',n1,'counterfactuals',n2)
