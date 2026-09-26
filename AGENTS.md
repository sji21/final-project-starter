# Working agreement

- The product is a local, domain-swappable document review foundation.
- Domain rules and prompts belong in packs/<id>/, not conditionals in app/.
- Keep demo replay visibly distinct from model inference. Never return demo output as model output.
- Evidence must resolve to the immutable run document snapshot and exact quote.
- A partial search cannot prove absence. Preserve needs_review when scope is incomplete.
- Human decisions append audit entries and require the current revision.
- Never put secrets, private documents, model weights, or runtime databases in Git.
- Do not silently convert generated or approved UI suggestions into human-verified training labels.
- Preserve input hashes, pack hashes, prompt hashes, served model names, and evaluation provenance.
- Checks: python -m ruff check app tests; python -m ruff format --check app tests; python -m pytest -q; node --check web/app.js.
- Add tests for changed contracts, failure paths, persistence, and model/provider boundaries.
- This app has no organizational authentication. Keep local-only deployment defaults.
- GPU training, deployment, and model benchmarks must be reported as unverified until actually run.

