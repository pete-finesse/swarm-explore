"""Band mean vs output-layer readout of the original bridge, from the released summary.
Usage: python3 -I checks/output_layer_readout.py repos/silent-dissent/docs/results/crossmodel_summary.json
The last layer under the logit lens is the model's own next-token distribution."""
import json, sys
d = json.load(open(sys.argv[1]))
print(f"{'model':24s} {'cell':8s} {'band J':>7s} {'band logit':>10s} {'output layer':>12s}")
for m, v in d["models"].items():
    b, L = v["meta"]["band"], v["meta"]["n_layers"]
    for c in ("round0", "agree", "held", "flipped"):
        j = v["curves"][f"{c}/jlens/orig_bridge"]; l = v["curves"][f"{c}/logit/orig_bridge"]
        print(f"{m:24s} {c:8s} {sum(j[i] for i in b)/len(b):7.2f} {sum(l[i] for i in b)/len(b):10.2f} {l[L-1]:12.2f}")
