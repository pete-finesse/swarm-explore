#!/usr/bin/env bash
# Drive the J-PACT pod FROM THE MAC (adapted from projects/silent-dissent/harness/pod.sh).
#   export POD_SSH="ssh root@<ip> -p <port> -i ~/.ssh/id_ed25519"
#   ./pod.sh push [--code]   copy harness + J-PACT code + NARCBench code to /workspace/jpact (and run setup_pod.sh)
#   ./pod.sh run NAME CMD..  run CMD (in the pod venv, from harness/) in the background, log /workspace/logs/NAME.log
#   ./pod.sh status [NAME]   GPU use, running jobs, tail of a log
#   ./pod.sh pull            results + logs to ../data/pod-results/ (git-ignored)
#   ./pod.sh ssh [CMD]
set -euo pipefail
: "${POD_SSH:?set POD_SSH}"
HERE=$(cd "$(dirname "$0")" && pwd); P=$(dirname "$HERE")   # projects/jpact
REMOTE=/workspace/jpact
read -r -a SSH <<< "$POD_SSH"; SSH=("${SSH[@]/#\~/$HOME}" -o ServerAliveInterval=30)
on_pod() { "${SSH[@]}" "$@"; }
case "${1:-}" in
  push)
    COPYFILE_DISABLE=1 tar --no-mac-metadata --no-xattrs -czf - --exclude='__pycache__' --exclude='results' --exclude='*.pdf' \
        -C "$P" harness -C "$P/repos" jpact-code narcbench \
      | on_pod "mkdir -p $REMOTE && tar -C $REMOTE --no-same-owner -xzf - && find $REMOTE -name '._*' -delete"
    [[ "${2:-}" == "--code" ]] && { echo "code updated"; exit 0; }
    on_pod "mkdir -p /workspace/logs; cd $REMOTE/harness; nohup bash setup_pod.sh > /workspace/logs/setup.log 2>&1 < /dev/null &"
    echo "setup started; ./pod.sh status setup" ;;
  run)
    name=${2:?job name}; shift 2
    # Detach fully: the whole job (env + command) runs under setsid with all three streams redirected, so ssh returns
    # at once. (Before, `source env.sh && nohup cmd > log &` backgrounded a subshell that kept ssh's stdout open, and
    # ssh waited for the job to end.)
    job="source /workspace/env.sh; exec $(printf '%q ' "$@")"
    on_pod -n "mkdir -p /workspace/logs; setsid bash -c $(printf '%q' "$job") > /workspace/logs/$name.log 2>&1 < /dev/null & disown; echo started '$name'" ;;
  status)
    on_pod "nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader; echo jobs:;
            ps -eo pid,etime,args | grep '[p]ython' | grep -v 'bash -c' | cut -c1-150 || echo '  none: pod idle'; df -h /workspace | tail -1;
            ${2:+tail -n 15 /workspace/logs/$2.log}" ;;
  pull)
    mkdir -p "$P/data/pod-results"
    on_pod "tar -C $REMOTE/harness -czf - results" | tar -C "$P/data/pod-results" -xzf -
    on_pod "tar -C /workspace -czf - logs" | tar -C "$P/data/pod-results" -xzf -
    echo "copied to $P/data/pod-results/" ;;
  ssh) shift; if [[ $# -gt 0 ]]; then on_pod "source /workspace/env.sh && $*"; else "${SSH[@]}" -t "source /workspace/env.sh; exec bash -l"; fi ;;
  *) sed -n '2,9p' "$0"; exit 1 ;;
esac
