Cloudflare Workers (Python) migration notes

This repo contains a scaffold to run a Python Cloudflare Worker as a new entrypoint.
It does NOT port the full FastAPI app automatically — many dependencies (psycopg2,
SQLAlchemy, synchronous servers, websockets, long-running CPU tasks) are not
supported in the Workers sandbox. Follow the guidance below to deploy and to
progressively port functionality.

Files added:
- wrangler.toml                (pointing to worker.py)
- worker.py                    (Workers entrypoint scaffold)
- pyproject.workers.toml       (project metadata for the Worker)
- .github/workflows/deploy-cloudflare-workers.yml  (CI: wrangler publish on push)

Quick local steps (developer machine):
1. Install wrangler (requires Node):
   npm install -g wrangler@3

2. Configure wrangler.toml:
   - Set account_id (or provide CF_ACCOUNT_ID secret in CI).
   - Optionally set "route" for production.

3. Test build / publish locally (you need CF_API_TOKEN with appropriate permissions):
   # Optional: login
   export CF_API_TOKEN="..."
   wrangler whoami
   # Publish to workers.dev (workers_dev=true in wrangler.toml):
   wrangler publish

GitHub integration (automatic on push to main):
- Create two repository secrets: CF_API_TOKEN (write access to Workers) and CF_ACCOUNT_ID.
- The included workflow publishes on push to main and will appear under the repo's Deployments → Cloudflare Workers when connected via the Cloudflare GitHub integration.

Porting guidance & limitations:
- FastAPI and Starlette cannot run inside Workers. Replace route handlers with small async functions in worker.py or split business logic into a separate HTTP API (hosted on a service that supports FastAPI) and let the Worker proxy or act as edge cache.
- No direct PostgreSQL drivers (psycopg2). Use HTTP APIs, Cloudflare D1 (SQLite-compatible), or managed DBs exposed via a secure HTTP layer.
- No background workers or long-running CPU tasks. Use Cloudflare Queues / Durable Objects / external workers.
- Websockets are not supported the same way; Workers do not host arbitrary websocket servers.

Next steps recommended:
1. Decide: Full port to Workers (rewrite handlers to avoid unsupported libs) OR use Worker as an edge proxy to an existing FastAPI service.
2. Implement a small set of critical endpoints (health, static proxies) in worker.py and test.
3. Securely add CF_API_TOKEN and CF_ACCOUNT_ID as GitHub secrets, then push to main to trigger deployment.

If you want, continue and the migration can proceed in phases: health/proxy → auth → data endpoints.
