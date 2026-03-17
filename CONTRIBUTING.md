# Contributing

Thanks for helping improve this repository.

The goal of this repo is to collect practical LNbits skills that are clear enough for humans and structured enough for AI agents to follow reliably.

## What To Contribute

Useful contributions include:

- new skills
- corrections to existing skills
- clearer examples
- troubleshooting notes
- better references to official LNbits resources

This repository is for shared LNbits knowledge. If your documentation only applies to a single extension, it will usually fit better in that extension's own repository.

## Repository Conventions

- Put each skill under one category in `skills/`.
- Available categories are `skills/operational/`, `skills/development/`, and `skills/infrastructure/`.
- Use kebab-case for skill folder names.
- Keep one main task per skill.
- Put the main guide in `SKILL.md`.
- Add `examples/` or `assets/` only when they materially help.

## What Belongs Here

Good candidates for this repo:

- LNbits workflows used across multiple projects
- shared extension-development practices
- deployment and infrastructure guidance
- general troubleshooting patterns

Usually better in an extension repo:

- setup instructions for one extension
- extension-specific configuration notes
- codebase-specific implementation guides
- release or maintenance instructions for a single extension

## Creating A New Skill

1. Copy `templates/skill-template.md`.
2. Create a new folder at `skills/<category>/<skill-name>/`.
3. Add the copied template as `SKILL.md`.
4. Fill in the sections with concrete, tested guidance.
5. Add examples, commands, or config snippets when useful.

## Writing Guidelines

- Be specific about when to use the skill.
- Prefer step-by-step instructions over high-level theory.
- List prerequisites and required inputs up front.
- Include commands, configuration, and expected outcomes where relevant.
- Call out common failure modes and troubleshooting steps.
- Link to primary LNbits documentation or source material when possible.

## Quality Bar

Before opening a change, check that the skill:

- solves a real task
- is easy to scan quickly
- avoids unnecessary jargon
- uses consistent naming and formatting
- does not assume hidden context

## Updating Existing Skills

When editing an existing skill:

- preserve the original goal of the skill
- improve clarity without making it bloated
- update stale commands or references
- keep examples aligned with the documented steps

## Pull Requests

Small, focused pull requests are preferred.

In your PR description, include:

- what changed
- why it changed
- any assumptions or limitations

## Questions

If a skill feels too broad, split it into smaller skills instead of creating one large guide.
