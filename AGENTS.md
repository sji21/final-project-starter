# Working agreement

## Product

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

## Writing

- Conclusion first. The first sentence of a document, and of every section, is its point.
- No preamble, no restatement of the request, no recap section, no "key takeaways".
- Say it in the fewest words that stay accurate. Numbers, names and dates, not adjectives.
- Cut a sentence that only introduces the next one.
- State what was not verified, in one line, rather than implying it was.

## Files

- Do not create a file that was not asked for. Extend the document that already covers it.
- One document per subject. A new file needs a subject no existing file owns.
- No summary, index or status file that restates what other files already say. CHANGELOG.md is the one exception.
- Notes about one change go in the pull request, not in a new document.
- Write to the repository only what belongs under version control. Working notes stay out.

## Repository

- One repository. Do not run a separate development and main repository.
- Indexes, checkpoints, corpora, model weights and databases stay out of Git.
  Commit a manifest with sizes and hashes, and keep the artifacts where they are built.
- Task state lives in issues and the project board, never in a tracked table five people edit.
  A markdown task list works for one author and conflicts on every merge for five.
- The pull request is the primary record of a change: problem, visible change, cases checked,
  compatibility, and what was not verified.
- CHANGELOG.md summarises releases, not commits. Update it at the Friday demo and at each tag,
  in one language, with a Validation entry stating what was actually run and what was not.

## How we work

- main stays runnable at every commit.
- One issue, one short branch. No long-lived personal branches.
- Open a draft pull request as soon as something runs, so interfaces are shared early.
- One purpose per pull request, sized to review within one or two days.
- One reviewer plus the automated checks, then squash merge and delete the branch.
- Changes to the API, shared types or the database include the consumer in review.
- No direct push to main. Enforce it in the repository settings, not by agreement.
- One primary task per person. Cards are half a day to two days; split anything longer.
- Fix a schema, seed file or contract once, in the place every side reads.

## Definition of done

- The requested input and expected output are implemented.
- Real integration, or the contract check that fits the stage, passes.
- The representative failure case is handled.
- The pull request records how to reproduce the result.
- A reviewer confirmed it and it is merged to main.
- Mock-only work is "contract implemented", never "integrated".
- Report collected, executed and passed test counts as three different numbers.

## Ground rules

- Never present demo output as model output.
- Training, deployment and benchmarks that were not run are reported as unverified.
- Secrets, personal documents, model weights and runtime databases stay out of Git.
- Never change gold labels to raise a score. Record the error type and the evidence.
- Someone other than the training owner must be able to run the frozen evaluation.
- GPU work is booked with owner, time and experiment id, and its daily cost is recorded.
- Never build a new environment the day before a demo.
