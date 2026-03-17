# LNbits Skills Repository

A curated collection of reusable LNbits skills for humans and AI agents.

This repository is meant to capture practical, repeatable ways to operate, develop, and deploy LNbits. Each skill should be self-contained, easy to scan, and useful in real work.

## Purpose

LNbits knowledge often lives across docs, issues, chats, and personal notes. This repo brings that knowledge into one place as structured skills that can be reused by contributors, operators, and coding agents.

The goals are to:

- document real workflows, not just concepts
- keep guidance consistent across topics
- make tasks easier to hand off to humans or AI agents
- build a durable library of LNbits operational knowledge

This repo is intentionally focused on shared LNbits knowledge. Extension-specific implementation details should usually live in the relevant extension repository, where they can evolve alongside the code.

## What A Skill Is

A skill is a focused guide for completing one concrete task.

Examples:

- install LNbits with Docker
- create a new LNbits extension
- configure a wallet backend
- debug an extension startup issue
- deploy LNbits behind a reverse proxy

Good fit for this repo:

- reusable extension-development patterns
- common operational workflows
- infrastructure and deployment guidance
- cross-cutting troubleshooting approaches

Usually not a fit for this repo:

- docs for one specific extension only
- extension-local setup quirks
- implementation details tied to a single extension codebase
- release notes or maintenance instructions for one extension repo

Each skill should live in its own folder and include a `SKILL.md` as the primary guide.

## Repository Structure

```text
agent-skills/
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── skills/
│   ├── development/
│   ├── infrastructure/
│   └── operational/
└── templates/
    └── skill-template.md
```

Category overview:

- `skills/operational/`: running, maintaining, and troubleshooting LNbits
- `skills/development/`: shared extension-development patterns, integrations, APIs, and local development
- `skills/infrastructure/`: deployment, scaling, hosting, and production setup

Suggested per-skill layout:

```text
skills/<category>/<skill-name>/
├── SKILL.md
├── examples/
└── assets/
```

## Getting Started

1. Browse the folders in `skills/`.
2. Choose the category that matches the task.
3. Open the skill directory.
4. Follow the instructions in `SKILL.md`.

If you are contributing a new skill, start with `templates/skill-template.md` and read `CONTRIBUTING.md`.

If you are using an AI coding agent in this repo, read `AGENTS.md` first.

## Scope Boundary

Use this repository for skills that apply across LNbits or across multiple extensions.

Keep extension-specific guides in each extension repository when the instructions depend on that extension's code, release flow, configuration, or maintenance lifecycle.

## Design Principles

- Modular: each skill should stand on its own
- Practical: focus on actions, commands, checks, and outcomes
- Consistent: use the shared template and naming conventions
- Reusable: write so both people and agents can follow the same guidance

## Contributing

Contributions are welcome. New skills, edits, corrections, and refinements are all useful.

Use `CONTRIBUTING.md` for contribution rules and `templates/skill-template.md` as the starting point for new skills.
