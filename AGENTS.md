# AGENTS.md

This file gives repository-specific guidance to AI agents working in this project.

## Mission

Help maintain a clean, reusable library of LNbits skills that can be followed by both humans and AI systems.

## What This Repo Contains

- `skills/operational/`: operational runbooks and troubleshooting
- `skills/development/`: development workflows, extension work, APIs, and integrations
- `skills/infrastructure/`: deployment and production-oriented guidance
- `templates/skill-template.md`: the base template for new skills

## Preferred Agent Workflow

1. Read `README.md` for repository intent.
2. Read `CONTRIBUTING.md` before adding or restructuring skills.
3. Reuse `templates/skill-template.md` when creating a new skill.
4. Keep changes focused on one task or one documentation improvement at a time.

## Authoring Rules

- Use one folder per skill.
- Name skill folders in kebab-case.
- Put the main content in `SKILL.md`.
- Keep examples practical and minimal.
- Prefer direct commands, checks, and outcomes over long explanations.
- Add troubleshooting guidance when failure is common or costly.

## Editing Guidance

- Do not rename categories unless explicitly asked.
- Do not add broad repository tooling unless it supports the skill library directly.
- Preserve existing contributor intent when refining documentation.
- If you find stale or conflicting instructions, update them rather than layering duplicate guidance elsewhere.

## Style Expectations

- Write for fast comprehension.
- Be concrete about prerequisites, inputs, and success criteria.
- Avoid filler, marketing language, and unnecessary theory.
- Prefer official LNbits references when linking out.

## Definition Of Done

A documentation change is in good shape when:

- the repository structure stays consistent
- the skill or doc is easy to navigate from a fresh clone
- an agent can tell where a new skill belongs
- a contributor can create a new skill without guessing the format
