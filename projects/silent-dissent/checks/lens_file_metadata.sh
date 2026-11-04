#!/bin/sh
# Reads n_prompts / source_layers / d_model of a Neuronpedia lens file without downloading the weights:
# fetches the first 16 KB (the zip's first member is data.pkl) and disassembles the pickle (never executes it).
# Usage: sh checks/lens_file_metadata.sh qwen-n1000/qwen3.5-4b/jlens/Salesforce-wikitext/Qwen3.5-4B_jacobian_lens_n1000.pt
T=$(mktemp); curl -sL -r 0-16383 "https://huggingface.co/neuronpedia/jacobian-lens/resolve/$1" -o "$T"
python3 -I - "$T" <<'PY'
import sys, struct, pickletools
b=open(sys.argv[1],'rb').read(); n,e=struct.unpack('<HH',b[26:30]); s=30+n+e; out=[]
for op,arg,pos in pickletools.genops(b[s:]):
    if op.name=='STOP': break
    if arg is not None and op.name not in ('BINPUT','LONG_BINPUT','BINGET','LONG_BINGET'): out.append(repr(arg))
t=' '.join(out); k=t.find("'n_prompts'"); print(t[k:k+700])
PY
rm -f "$T"
