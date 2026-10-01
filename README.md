# LeakHub — APIRadar

**Every public API. Every endpoint. In one searchable index.**

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![Textual](https://img.shields.io/badge/TUI-Textual-8A2BE2)
![License](https://img.shields.io/badge/License-MIT-yellow)

APIRadar scrapes public API catalogues (APIs.guru, GitHub OpenAPI/Swagger files), parses every spec, and indexes every path and HTTP method into a local SQLite database. Browse it through a FastAPI REST layer or an interactive Textual terminal UI.

---

## Why this exists

If you're doing bug-bounty recon or building an API-aggregator product, the first thing you need is a searchable list of "every REST endpoint the internet publishes". That doesn't exist as a downloadable dataset. APIRadar builds it locally, on demand, from open sources — and gives you both a machine-readable API and a fast keyboard-driven UI to explore it.

---

## Try it in 60 seconds

```bash
git clone https://github.com/Danush-Aries/leakhub
cd leakhub
pip install -r requirements.txt

cp .env.example .env     # optional: set GITHUB_TOKEN for GitHub search

# Start the FastAPI backend on :8000 (API docs at /docs)
python main.py backend

# In another terminal: trigger a scrape of APIs.guru
curl -X POST http://localhost:8000/scrape/apis-guru

# Browse results: REST endpoints /apis, /endpoints, /providers ...
curl http://localhost:8000/apis
```

Or open the Textual UI in a terminal:

```bash
python main.py tui
```

Other commands: `python main.py scrape` (one-shot APIs.guru scrape), `make test`.

---

## How it works

```
+-- Scrape sources --------------+
|  apis.guru (2500+ public APIs) |
|  GitHub code search (openapi)  |
+--------------|-----------------+
               v
+-- OpenAPI parser --------------+
|  OpenAPI 2 + 3                 |
|  extracts path + method + tags |
+--------------|-----------------+
               v
+-- SQLModel storage ------------+
|  providers / apis / endpoints  |
|  SQLite (portable) or Postgres |
+--------------|-----------------+
               v
+-- FastAPI REST + Textual TUI --+
|  /apis  /endpoints  /providers |
|  /scrape/apis-guru /scrape/github |
|  live search screen            |
|  dashboard: source health      |
+--------------------------------+
```

Docker files are under `apiradar/devops/`.

---

## Stack

| Layer | Tech |
|---|---|
| API | FastAPI + Uvicorn |
| ORM | SQLModel (SQLite default, Postgres-ready) |
| TUI | Textual |
| Config | python-dotenv |
| Deploy | Dockerfile + docker-compose |
| Sources | APIs.guru + GitHub code search |

---

## More from Danush

Part of a broader stack of AI + security tooling:

- [jarvis](https://github.com/Danush-Aries/jarvis) — portable multi-provider AI assistant (voice/web/CLI)
- [breachintel](https://github.com/Danush-Aries/breachintel) — OSINT breach intelligence aggregator
- [cve-advisor](https://github.com/Danush-Aries/cve-advisor) — AI-powered CVE triage and patch recommendation
- [llm-fragility-lab](https://github.com/Danush-Aries/llm-fragility-lab) — adversarial testing lab for LLM robustness
- [network-intrusion-analyzer](https://github.com/Danush-Aries/network-intrusion-analyzer) — Suricata + Claude AI intrusion triage
- [autonomous-coding-agent](https://github.com/Danush-Aries/autonomous-coding-agent) — two-agent autonomous coding system

Built by [Dhanush](https://github.com/Danush-Aries) — AI engineering + cybersecurity.

## License

MIT — see [LICENSE](LICENSE).
