#!/usr/bin/env bash
# One-shot setup ON THE POD. Safe to rerun. Everything under /workspace (survives a pod stop).
#   /workspace/jpact/{harness,jpact-code,narcbench}  pushed by pod.sh
#   /workspace/jpact/jpact-code/artifacts/...        model, lens, NARCBench data, J-PACT cache (J-PACT's own layout)
set -euo pipefail
W=/workspace; J=$W/jpact; A=$J/jpact-code/artifacts
export HF_HOME=$W/hf_cache UV_CACHE_DIR=$W/uv/cache UV_PYTHON_INSTALL_DIR=$W/uv/python PATH=$W/uv/bin:$PATH
export HF_HUB_ENABLE_HF_TRANSFER=1
mkdir -p "$HF_HOME" "$W/uv/bin" "$W/logs" "$A"
cat > $W/env.sh <<E2
export HF_HOME=$HF_HOME UV_CACHE_DIR=$UV_CACHE_DIR UV_PYTHON_INSTALL_DIR=$UV_PYTHON_INSTALL_DIR PATH=$W/uv/bin:\$PATH
export TOKENIZERS_PARALLELISM=false PYTHONPATH=$J/jpact-code NARCBENCH_DIR=$J/narcbench
source $J/venv/bin/activate
cd $J/harness
E2
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=$W/uv/bin INSTALLER_NO_MODIFY_PATH=1 sh
[ -d $J/venv ] || uv venv --python 3.12 $J/venv
source $J/venv/bin/activate
# J-PACT's pins (env/requirements.txt), minus kernels (GPT-OSS only) and playwright (figures only)
uv pip install -q "torch>=2.6" numpy==2.1.0 scipy==1.18.0 scikit-learn==1.7.2 transformers==5.17.0 transformer-lens==3.9.0 \
  huggingface-hub==1.28.0 accelerate==1.15.0 safetensors==0.8.0 PyYAML==6.0.1 tqdm==4.70.0 hf_transfer
python -c "import torch; assert torch.cuda.is_available(); print('torch', torch.__version__, torch.version.cuda, torch.cuda.get_device_name())"
# jacobian-lens at J-PACT's pin (for JacobianLens, used by J-PACT's lens loader)
[ -d $J/jacobian-lens/.git ] || git clone -q https://github.com/anthropics/jacobian-lens.git $J/jacobian-lens
git -C $J/jacobian-lens checkout -q 581d398613e5602a5af361e1c34d3a92ea82ba8e && uv pip install -q --no-deps -e $J/jacobian-lens
cd $J/jpact-code
python - <<'PY'
from huggingface_hub import hf_hub_download, snapshot_download
A='artifacts'
# NARCBench dataset at J-PACT's pin: Qwen Core transcripts + release metadata
snapshot_download('aaronrose227/narcbench', repo_type='dataset', revision='19cb14b269e052b19ba6d2bd2f4519afd3b10c57',
    local_dir=f'{A}/narcbench', allow_patterns=['scenarios/qwen3_32b/core/**', 'activations/qwen3_32b/core/metadata_gen.json'])
# J-PACT's cache: Qwen Core rows, decompositions, labels, identities
snapshot_download('throwaway-reproducibility-354364563/jpact-cache', repo_type='dataset', local_dir=A,
    allow_patterns=['maj/2026-09-22-repro/qwen3_32b/end_of_response/*', 'maj/2026-09-22-repro/qwen3_32b/end_of_response/evaluator/*',
                    'maj/2026-09-22-repro/qwen3_32b/end_of_response/training/*', 'maj/2026-09-22-repro/qwen3_32b/end_of_response/pairs/core.npz',
                    'maj/2026-09-22-repro/qwen3_32b/end_of_response/raw/input/core_*', 'maj/2026-09-22-repro/qwen3_32b/end_of_response/individual_j_reconstruction/sparse/core_*',
                    'cache_expansion/qwen3_32b/**', 'qwen_reproduction/**', 'observations/*qwen3_32b*'])
# The lens J-PACT used (partial 80-prompt checkpoint) and its config
for n in ('Qwen3-32B_jacobian_lens.pt', 'config.yaml'):
    hf_hub_download('neuronpedia/jacobian-lens', f'qwen3-32b/jlens/Salesforce-wikitext/{n}', revision='8aa8152c99710a9d7a2f8889319502d46443ff10',
                    local_dir=f'{A}/lens_candidate')
snapshot_download('Qwen/Qwen3-32B', revision='9216db5781bf21249d130ec9da846c4624c16137', local_dir=f'{A}/qwen3_32b',
    allow_patterns=['*.json', '*.safetensors', '*.txt', '*.jinja'])
print('downloads done')
PY
du -sh $A/* | sort -h
echo "setup done"
