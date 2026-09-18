# Architecture Toolkit Implementation Plan

> For agentic workers: use superpowers:executing-plans for inline implementation; use writing-skills for the independent before/after reference retrieval exercise.

**Goal:** Extend the approved reference pack with source-qualified implementation patterns and one project architecture selection skill.
**Architecture:** Keep case discovery, permissions, delivery and release in existing skills. A new reference-routing skill selects a minimal pattern set and produces a project-owned selection/deployment plan; no runtime or production executor is added.
**Tech Stack:** Markdown, JSON catalog, existing Python standard-library integrity/install tests.
**Spec:** User-approved knowledge + architecture patterns + one selection skill design; implementation boundaries recorded below.

## Global constraints

- Existing nine skills and 24 PDF cases remain; no customer facts, credentials, videos or complete creator transcripts in the distribution.
- Source observations remain candidate, not independently verified; parameter examples are not defaults.
- No new third-party dependency, network executor, auto-install or automatic project upgrade.
- New skill must be present in catalog, plugin skill directory, installer allowlist and manifest.
- Repository release 0.2.0; reference pack content 0.2.0. Additive new skill, no existing project lock migration.

## Tasks

- [x] Baseline: verify clean remote snapshot and 133 existing tests; independent retrieval exercise before new files.
- [x] Write tests/test_architecture_toolkit.py before content. Require 10 unique patterns, 61 source identities, source-to-pattern references, in-bundle links, skill discovery/install availability and no deployment claims. Run test to observe missing catalog failure.
- [x] Create architecture/README.md, catalog.json, 10 pattern documents and sources.json. Each pattern supplies selection/exclusion, component data flow, field contract, implementation sequence, fallback, test cases and provenance. Preserve extended knowledge in knowledge/ without raw media or host paths.
- [x] Add skills/fde-architecture-select/SKILL.md, selection/deployment template and two synthetic examples. Wire catalog and existing entrypoints without altering existing skill behavior.
- [x] Exercise new skill independently on the same baseline scenario plus a deterministic CSV counterexample; record actual gaps and fix them.
- [x] Update version, changelog, reviewed file manifest. Run all standard-library tests, skill syntax validation, exact-tree integrity check and heuristic secret scan; inspect diff and references.
- [ ] Push reviewed feature branch; create PR, inspect remote commit/tree and checks. Upload is not production deployment or host skill-install proof.

## Test boundaries

Automated tests establish packaging/links/install compatibility, not architecture correctness. Independent exercises establish limited sample behavior, not general model reliability. Project deployment and business acceptance remain unperformed.
