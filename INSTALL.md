# Install `krusch-bizlaw`

These are instructions for a coding agent (Claude Code, Codex, Cursor, Windsurf, or Antigravity) that a person asked to install and configure `krusch-bizlaw` (`v0.2.0`) on their machine.

`krusch-bizlaw` is a Python `>= 3.11` deterministic statutory compliance engine and Contract-vs-Statute Join platform ("The Join"). It evaluates commercial and residential contract slots against statutory floors, ceilings, effective dates (`as_of_date`), and public policy prohibitions via a strict-loopback FastAPI server (`127.0.0.1:8087`) and an optional Streamlit UI (`127.0.0.1:8507`), with zero LLM calls, zero Docker containers, and zero external database requirements in standalone mode.

## 1. Check Prerequisites First (All at Once)

Run a single read-only check before making any changes:

```bash
id -u
python3 --version 2>/dev/null || echo "MISSING: python3"
python3 -m venv --help >/dev/null 2>&1 || echo "MISSING: python3-venv"
git --version 2>/dev/null || echo "MISSING: git"
ss -ltnp 2>/dev/null | grep -E ':(8087|8507)\b' || lsof -iTCP:8087 -iTCP:8507 -sTCP:LISTEN 2>/dev/null || true
```

Evaluate the results:
1. **User check**: If `id -u` prints `0` (`root`), stop and ask the person to run you under a standard non-root user account.
2. **Python `>= 3.11` with `venv` (Required)**: `pyproject.toml` requires Python `3.11` or newer (`3.11` or `3.12` recommended). If `python3` is missing, older than `3.11`, or lacks the `venv` module, ask the person before installing Python `3.11+` (`uv python install 3.12`, `pyenv`, `brew`, or OS packages).
3. **Port availability (`8087` and `8507`)**: Check whether `127.0.0.1:8087` (FastAPI) or `127.0.0.1:8507` (Streamlit) is already bound before starting a server.
4. **Upstream Pillars & External Databases (Strictly Optional)**: `krusch-bizlaw` runs air-gapped out of the box with zero PostgreSQL or Ollama dependencies. Only connect `LAW_BASE_URL` (`http://127.0.0.1:8085`) and `BIZ_BASE_URL` (`http://127.0.0.1:8086`) if the person is also running `krusch-law` and `krusch-biz`.

## 2. Choose the Right Setup Mode

- **Mode A: Standalone Compliance Engine + FastAPI Loopback Server (Recommended Default)**: Clones `krusch-bizlaw`, installs dependencies in `.venv`, verifies all `77` automated `pytest` tests plus the 11-scenario compliance benchmark, and optionally launches the FastAPI REST server on `127.0.0.1:8087`.
- **Mode B: Full Local Workbench (FastAPI `:8087` + Streamlit Web UI `:8507`)**: Adds the interactive Streamlit cross-examination interface bound strictly to `127.0.0.1:8507`.
- **Mode C: Federated Three-Pillar Mesh (Optional)**: Connects `krusch-bizlaw` (`:8087`) to local `krusch-law` (`:8085`) and `krusch-biz` (`:8086`) REST services while preserving graceful fallback (`INV-9`) if either upstream service goes offline.

## 3. Install in an Isolated Virtual Environment & Verify

Check `pwd` first so you clone into an appropriate workspace directory (for example, `$HOME/src/krusch-bizlaw` if `pwd` is `$HOME`):

```bash
git clone https://github.com/kruschdev/krusch-bizlaw.git
cd krusch-bizlaw
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"
```

Run the headless demo, the 11-scenario statutory benchmark (`11/11`), and the full `pytest` verification suite (`77` tests covering `INV-1` through `INV-10`, AB 12 temporal boundaries, loopback data residency, and API security hardening):

```bash
.venv/bin/python scripts/demo_60s.py
.venv/bin/python scripts/eval_benchmark.py
.venv/bin/pytest tests/ -v
```

## 4. Start the Service (When Requested)

### FastAPI REST Server (`127.0.0.1:8087`)

Confirm port `8087` is free, then start the loopback API server:

```bash
.venv/bin/python -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8087
```

Verify health and run a sample deterministic AB 12 post-enactment check (`as_of_date` in `YYYY-MM-DD` format is mandatory under `INV-1`):

```bash
curl -fsS http://127.0.0.1:8087/health
curl -fsS http://127.0.0.1:8087/api/mandates
curl -fsS -X POST http://127.0.0.1:8087/api/conflicts/contract-vs-statute \
  -H "Content-Type: application/json" \
  -d '{
    "as_of_date": "2024-08-01",
    "jurisdiction": "CA",
    "property_type": "residential",
    "topics": ["SECURITY_DEPOSIT"],
    "contract_slots": {"security_deposit_months": 2.0}
  }'
```

### Optional: Streamlit Web UI (`127.0.0.1:8507`)

Only launch Streamlit if the person wants the browser UI and port `8507` is free:

```bash
.venv/bin/streamlit run src/frontend/app.py --server.port 8507 --server.address 127.0.0.1 --server.headless true
```

### Optional: Environment Variables (`.env`)

No `.env` file is required for local development (`APP_ENV=development` on `127.0.0.1:8087`). If the person requests production hardening or custom ports, configure only explicit variables without inventing placeholder secrets:
- `HOST=127.0.0.1` and `PORT=8087` (strict loopback residency under `INV-8`).
- `APP_ENV=production` and `REQUIRE_API_KEY=true` require a strong, caller-supplied `API_KEY` passed via the `X-API-Key` header (placeholder strings such as `default`, `changeme`, or `secret` are rejected at startup).
- `LAW_BASE_URL=http://127.0.0.1:8085` and `BIZ_BASE_URL=http://127.0.0.1:8086` configure optional Three-Pillar federation.

## Never

- **Never run global `pip install` or `sudo pip`**: always install inside `.venv` (`python3 -m venv .venv && .venv/bin/pip install ...`).
- **Never run `uvicorn`, `streamlit`, or `pytest` as `root` or with `sudo`**.
- **Never bind `--host 0.0.0.0` or set `ALLOW_LAN=1`** unless the person explicitly asks to expose the service beyond `127.0.0.1` (`INV-8` rejects non-loopback bindings by default).
- **Never omit `as_of_date` or hardcode a silent "today" fallback** in client calls (`INV-1` requires an explicit `YYYY-MM-DD` date on every compliance request).
- **Never set weak placeholder values** (`changeme`, `default`, `secret`, `replace_me`) for `API_KEY`.

## Tell the Person After

Share a concise status report:
1. **Virtual environment & location**: Report the exact clone directory and `.venv` path.
2. **Verification status**: Confirm `scripts/demo_60s.py`, `scripts/eval_benchmark.py` (`11/11` scenarios), and `.venv/bin/pytest tests/ -v` (`77/77` tests) passed cleanly.
3. **Active endpoints (if started)**: Report `http://127.0.0.1:8087/health` (and `http://127.0.0.1:8087/docs` or `http://127.0.0.1:8507` if Streamlit was requested), noting whether upstream `krusch-law` / `krusch-biz` federation is active or running in standalone mode.
4. **Next-step verification command**: Share a ready-to-run `POST /api/conflicts/contract-vs-statute` `curl` command with an explicit `as_of_date` so the person can test deterministic slot evaluation immediately.
