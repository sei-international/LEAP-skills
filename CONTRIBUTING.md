# Contributing a skill

Thank you for helping other LEAP users. A skill is a short instruction file that teaches an AI
assistant how to do one kind of LEAP work well. This page says how to write one and how it gets
into the repository.

## How a contribution moves through the repository

1. Open one pull request per skill. A pull request that touches several skills is sent back.
2. A maintainer reviews it. The checks in `.github/workflows/validate.yml` must pass first.
3. Once merged, the skill ships in the `leap-community` plugin
   (`plugins/leap-community/skills/<skill-name>/`).
4. After it has been tested on a sample area and reviewed again, a maintainer moves it to the
   `leap-core` plugin.

Fixes to an existing skill follow the same route: one skill per pull request, reviewed before merge.

## What a skill looks like

```
plugins/leap-community/skills/
└── leap-my-topic/
    ├── SKILL.md            required
    └── references/         optional, for longer material SKILL.md links to
```

- The folder name is the skill name: lowercase letters, digits and single hyphens, and the
  `name` line in the front matter must be the same text. Start it with `leap-`.
- The front matter has `name`, `description` and `metadata`, and nothing else, so the file
  stays portable to every tool that reads the Agent Skills format.
- `description` decides when the assistant uses the skill. Say what the skill does and name the
  user's own phrasings ("what is in this model", "create a scenario"). Keep it under 1024
  characters.
- `metadata` holds, as `key: value` lines, at least `author`, `leap-version`, `mcp-tools` (the LEAP
  MCP tools the skill calls), `tested-on` and `status`. Copy the block from any skill in
  `plugins/leap-core/skills` and change the values.
- `SKILL.md` stays under 500 lines, with no tab characters. Longer material goes in `references/`
  and is linked from `SKILL.md`.

## Writing rules

- Plain language. Short sentences. American spelling.
- Use the exact tool and parameter names of the LEAP MCP server (`leap_status`, `get_branch`,
  `set_expressions`, `api_call` and so on) and LEAP's own words for things in LEAP (area, branch,
  variable, expression, scenario, Current Accounts, region).
- Rules and checks, not essays. Every step says which tool to call and what to look at in the
  answer.
- One worked example per skill, on a public sample area. Freedonia ships with LEAP and is the
  usual choice.
- Nothing vendor-specific: no instructions that only work in one assistant, no scripts in the
  skill folder, no `allowed-tools` or other tool-specific front matter.
- Nothing that bypasses the user's access setting in LEAP. The user decides in LEAP's settings
  whether an assistant may read, change or calculate; a skill works within that and never tells
  the assistant to work around a refusal.
- Do not name private models or clients in the text or the example.

## Testing before you submit

Test the skill in a fresh assistant session with LEAP running and a sample area open. Ask a
question the description names and check that the assistant follows the steps and that the
tool calls succeed. Then write what you tested in the `tested-on` line of the metadata, for
example:

```
  tested-on: "Freedonia, LEAP 2026.9.0.19, 2026-11-06 (read-only; nothing calculated)"
```

Say what was not exercised as well as what was. A skill with no `tested-on` line is not merged.

## Checking the file locally

Run the same check the pull request runs:

```
python scripts/validate_skills.py
```

It needs only Python 3. It checks the front matter keys, the name, the description length, the
line count, tabs, and the plugin and marketplace files.

## Review

A maintainer reads every pull request before merge: the instructions, the tool names against the
current LEAP MCP server, and the test note. Expect questions. Skills are merged into
`leap-community` first and promoted to `leap-core` by a maintainer after a second test.
