set shell := ["bash", "-cu"]
set dotenv-load := true

venv_python := ".venv/bin/python"
venv_pip := ".venv/bin/python -m pip"
venv_pytest := ".venv/bin/pytest"
venv_paip := ".venv/bin/paip"

help:
  just --list

setup:
  python -m venv .venv
  {{venv_pip}} install -e '.[dev]'

test:
  {{venv_pytest}} -q

qc-setup:
  {{venv_pip}} install -r query-catalog/requirements-qc.txt

qc-validate:
  {{venv_python}} scripts/qc_validate.py --root . --policy query-catalog/policy.template.yaml

qc-validate-ci:
  bash scripts/qc_validate_ci.sh

monitor-add TITLE CITY TOPIC QUERY INTERVAL_MIN CHAT_ID:
  {{venv_paip}} monitor add --title "{{TITLE}}" --city "{{CITY}}" --topic "{{TOPIC}}" --query "{{QUERY}}" --interval-min "{{INTERVAL_MIN}}" --chat-id "{{CHAT_ID}}"

monitor-list:
  {{venv_paip}} monitor list

run-once MONITOR_ID:
  {{venv_paip}} run once --monitor-id "{{MONITOR_ID}}"

run-scheduler:
  {{venv_paip}} run scheduler

history MONITOR_ID LIMIT='20':
  {{venv_paip}} history --monitor-id "{{MONITOR_ID}}" --limit "{{LIMIT}}"

logs MONITOR_ID='1' LIMIT='20':
  {{venv_paip}} history --monitor-id "{{MONITOR_ID}}" --limit "{{LIMIT}}"

stats MONITOR_ID='1' LIMIT='10':
  PAIP_DB_PATH="${PAIP_DB_PATH:-./tmp/paip.db}" {{venv_python}} -m paip.debug --monitor-id "{{MONITOR_ID}}" --limit "{{LIMIT}}"

telegram-preview MONITOR_ID='1' LIMIT='10' RUN_ID='':
  PAIP_DB_PATH="${PAIP_DB_PATH:-./tmp/paip.db}" {{venv_python}} -m paip.debug --monitor-id "{{MONITOR_ID}}" --limit "{{LIMIT}}" --telegram-preview {{ if RUN_ID != "" { "--run-id " + RUN_ID } else { "" } }}

env-example:
  @printf '%s\n' \
    'Required:' \
    '  SEARXNG_BASE_URL=https://your-searxng.example' \
    '  TELEGRAM_BOT_TOKEN=<telegram-bot-token>' \
    '' \
    'Optional:' \
    '  PAIP_DB_PATH=./tmp/paip.db' \
    '  PAIP_LOG_LEVEL=INFO' \
    '  SEARXNG_API_KEY='
