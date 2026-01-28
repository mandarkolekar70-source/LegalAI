# Copilot Instructions for LegalAI

Purpose: concise, actionable guidance for AI coding agents to be productive in this repository.

- **Big picture:** Flask-based web app with async SQLAlchemy and a FAISS-backed vector store.
  - Entry point: [app/main.py](../app/main.py) — registers Blueprints (`auth`, `api`, `history`) and initializes DB with `asyncio.run(init_db())`.
  - API surface: Blueprints under `app/auth` and `app/api` (e.g., [app/api/analysis.py](../app/api/analysis.py)).
  - Persistence: async SQLAlchemy engine configured in [app/core/database.py](../app/core/database.py); models in [app/models](../app/models).
  - Retrieval & vector store: [app/vector_store/faiss_store.py](../app/vector_store/faiss_store.py) using `sentence-transformers` and `faiss` with default files `data/faiss_index.bin` and `data/metadata.pkl`.
  - ETL pipeline: [app/etl/pipeline.py](../app/etl/pipeline.py) processes PDFs -> chunking -> vector store.

- **Why this structure:** separation of concerns — web layer (Flask Blueprints), async DB layer (AsyncSession), and ML/IR components (agents, ETL, vector store). The project mixes synchronous Flask request handling with asynchronous DB/agent calls (route functions are `async` and use `await`).

- **Key integration points & patterns:**
  - Token-based auth: `app/core/config.py` reads settings from `.env`; JWT logic in `app/api/deps.py` and `app/auth/router.py` uses `create_access_token` / `token_required` patterns.
  - DB access: use `AsyncSessionLocal` as context manager (see [app/core/database.py](../app/core/database.py)); add/commit/refresh inside `async with AsyncSessionLocal()` blocks.
  - Vector metadata conventions: ETL writes metadata keys like `ipc_sections`, `acts`, `source`. Code expects these keys when presenting `app/agents/rag.py` results.
  - Singletons in API handlers: `analysis_bp` initializes `CaseClassifier`, `VectorStore`, and `LegalReasoningAgent` at module import time — change cautiously (might require reload or re-init during tests).

- **Project-specific conventions (observed):**
  - Route handlers are declared `async`, even under Flask.
  - File uploads saved to `data/uploads` (see [app/api/analysis.py](../app/api/analysis.py)).
  - Classifier is a lightweight, keyword-based heuristic (see [app/agents/classifier.py](../app/agents/classifier.py)); heavy transformer-based code is present but commented out.
  - VectorStore defaults and persistence: `faiss_index.bin` and `metadata.pkl` stored under `data/` unless overridden.

- **Developer workflows & commands:**
  - Run app locally: `python app/main.py` (app runs on port 8000).
  - Run ETL for PDFs: `python app/etl/pipeline.py --dir path/to/pdfs` (stores vectors in `data/`).
  - DB schema: app creates tables at startup via `init_db()` in `app/main.py`; there is no Alembic migration setup.
  - Environment: configure `.env` with `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` (see [app/core/config.py](../app/core/config.py)).
  - Heavy native deps: `faiss` and `sentence-transformers` require native binaries — use a compatible wheel or conda environment. Expect model downloads on first run.

- **When editing code, watch for:**
  - Async vs sync boundaries: keep DB/IO usage consistent; route functions are `async` and call `await` on DB/agent operations.
  - Singleton initialization: re-initializing `VectorStore()` may be slow and download models; use test doubles when unit testing.
  - Token decorator: `@token_required` injects the `current_user` as the first arg to the route handler — follow that signature.
  - Metadata keys and schema evolution: ETL metadata is relied upon by `rag` logic — changing keys requires updating consumer code.

- **Examples to reference in PRs / code edits:**
  - Adding an API endpoint: follow `analysis_bp` patterns in [app/api/analysis.py](../app/api/analysis.py).
  - Persisting new model fields: update `app/models/*`, then rely on startup `init_db()` or add manual migration steps.
  - Extending retrieval logic: modify [app/agents/rag.py](../app/agents/rag.py) and tests should mock `VectorStore.search()`.

If any section is unclear or you want this adjusted to enforce stricter rules (tests, linters, CI), tell me which area to expand or lock-down next.
