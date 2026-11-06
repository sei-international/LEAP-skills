# LEAP skills for AI assistants

Skills are short instruction files that teach an AI assistant how to do a kind of work well.
These skills teach an assistant how to work with [LEAP](https://leap.sei.org), the Low Emissions
Analysis Platform from the Stockholm Environment Institute (SEI), through LEAP's MCP server:
how to read a model, write expressions, build scenarios, read results, write a report and more.

Each skill is a folder with a `SKILL.md` file and sometimes a `references/` folder, in the open
[Agent Skills](https://agentskills.io) format that Claude Code, Claude.ai, OpenAI Codex,
Gemini CLI, Cursor and other tools read. The skills complement the LEAP MCP server: the server's
own guide says how to call its tools; a skill says how to do a modeling task with them.

## What you need

- **LEAP 2026.9.0.19 or later.** Earlier versions lack tool fixes the skills rely on.
- In LEAP, switch on **Allow AI assistants to interact with LEAP using LEAP's MCP Server**
  (Settings, Scripts & AI tab) and connect your assistant to the server as the LEAP help describes.
- An area open in LEAP while you work.

The skills never change what the assistant is allowed to do: LEAP's own access setting decides
whether an assistant may read, change or calculate the model.

## Using the skills

**Most LEAP users need nothing from this page.** LEAP installs the `leap-core` skills with the
program and places them where Claude Code, Codex and Gemini CLI look, under your own user folder,
the first time each LEAP version starts. The switch **Enable default LEAP AI skills** on LEAP's
Settings, Scripts & AI tab turns them on and off. LEAP's MCP server also offers every skill as a
prompt, so an assistant connected to LEAP can use them without any files at all. Come here when
you want the latest skills between LEAP releases, the contributed skills in `leap-community`, or
to use the skills in Claude.ai.

### Claude Code

The repository is a Claude Code plugin marketplace with two plugins: `leap-core` (reviewed and
tested skills) and `leap-community` (contributed skills awaiting review). In a Claude Code
session:

```
/plugin marketplace add sei-international/LEAP-skills
/plugin install leap-core@LEAP-skills
```

The second command opens the plugin's details, where you pick a scope and install. From a
shell, without a session:

```
claude plugin marketplace add sei-international/LEAP-skills
claude plugin install leap-core@LEAP-skills
```

In the Claude desktop app, add the marketplace the same way in a local session, then use the
**+** button next to the prompt box, **Add plugins**, to install from it.

To try one skill without the plugin, copy its folder into `.claude/skills/` of a project or into
`~/.claude/skills/` and start a new session.

### Claude.ai and the Claude desktop app

1. Zip one skill folder (for example `leap-orientation/`, with `SKILL.md` inside it). The folder
   name must stay the skill name.
2. In Claude.ai go to **Customize**, then **Skills** (claude.ai/customize/skills), click **+**,
   **Create skill**, **Upload a skill**, and upload the zip. Skills need **Code execution and file
   creation** switched on under Settings, Capabilities.
3. The skill is then on for your account. The desktop app and Cowork read the same list:
   **Customize** in the desktop app's sidebar shows it.

### Codex, Gemini CLI, Cursor and other tools

These tools read the same `SKILL.md` format. Copy the skill folder (not the zip) into the tool's
skills directory and restart the tool. The directory name differs by tool; its documentation
names it (for example a `skills/` folder under the tool's configuration directory, or the
project's `.agents/skills/` or `.cursor/skills/` folder).

### ChatGPT

ChatGPT does not read skill files. Open the skill's `SKILL.md`, copy the text below the front
matter, and paste it as the instructions of a ChatGPT project (or a custom GPT) that is
connected to LEAP's MCP server.

## The skills

| Skill | What it covers |
|---|---|
| `leap-orientation` | Reading an unfamiliar area before doing anything: status, years, scenario tree, demand and supply structure, a few anchoring numbers, a written summary. |
| `leap-expressions` | Writing, reading and fixing expressions: finding the right cell, Current Accounts versus scenarios, the implicit base-year value, shares and scales, references, checking after entry. |
| `leap-build-scenario` | A policy or sensitivity scenario from agreement on what changes, through `add_scenario` and `set_expressions`, to calculation and a comparison against the baseline. |
| `leap-demand-modeling` | The four demand methods and how to recognize them; reading a demand result back to its drivers; changing shares, intensities and stock data; adding branches; checks. |
| `leap-demand-structures` | How to structure a demand tree: top-down to bottom-up, branch properties, balance data in user variables, final versus useful energy, technology-share approaches, the hybrid historical/projection pattern with calibration, template regions. |
| `leap-transformation` | Modules, processes and fuels; the capacity, dispatch and reserve-margin variables; why a plant does not generate; adding capacity; load shapes; checks. |
| `leap-results` | Which tool answers which question; result variable names, filters, units; putting views on screen; presenting numbers honestly. |
| `leap-reporting` | From a calculated model to a report: chart set, favorites and overviews, exports, consistent units, writing the text. |
| `leap-data-from-spreadsheet` | Mapping a table to cells, unit and scale conversion, bulk entry into Current Accounts, calibration against the Energy Balance. |
| `leap-troubleshooting` | From LEAP's message to the cell: calculation errors, stale or odd results, Transformation and emissions gaps, optimization infeasibility, tool refusals, slow calculations. |
| `leap-api-scripting` | Reaching the rest of LEAP through `api_describe`, `api_get`, `api_set` and `api_call`, and writing VBScript or Python scripts for the Script Editor or outside LEAP. |
| `leap-lcds` | The LEAP Cloud Data Server: its data sets, the web service that lists and retrieves them, and the LEAP expression that links to a series. |
| `leap-milestones` | Milestones on Results charts: what they are, listing, adding, changing and removing them, and the chart options that show them. |
| `leap-uncertainty` | Stochastic (Monte Carlo-style) analysis: Vary and VaryGroup, the stochastic settings, running samples, reading statistics and percentiles. |
| `leap-costs` | Cost data, costing settings and the cost boundary, social cost and cost-benefit results, MACC and levelized costs. |
| `leap-emissions` | Emission factors and effect branches, GWP sets, non-energy effects, environment results, and the IBC air-pollution and health add-on. |
| `leap-optimization` | Least-cost optimization with NEMO: modes, requirements, data, constraints, reading results, the infeasibility routine. |
| `leap-multi-region` | Regions, region inheritance and groups, trade and transmission between regions, reading results per region or summed. |
| `leap-model-review` | A read-only audit checklist for a whole area before it is used for a report, with a findings list. |
| `leap-load-shapes` | Time slices, load shapes and yearly shapes, how dispatch uses them, reading time-sliced results. |
| `leap-tags-indicators` | Tags and tag filters, indicator branches, user variables, for custom groupings and reporting. |
| `leap-user-variables` | Defining user variables, units, visibility by branch type, tree position, tags and scenario, categories and colors, limits, Key Assumptions versus user variables, reading them in Results. |

Every skill was tried in a fresh assistant session on a sample area (Freedonia, which ships with
LEAP, or a larger model where the subject needed one) and revised from the findings. Each
file's `tested-on` line in the front matter says what was and was not exercised. All are still
marked `draft for review`; please report what does not work.

## Repository layout

```
.claude-plugin/marketplace.json     the marketplace: lists the two plugins
plugins/leap-core/                  reviewed and tested skills
plugins/leap-community/             contributed skills, awaiting review
scripts/validate_skills.py          the check that runs on every pull request
```

## Contributing

Corrections and new skills are welcome. [CONTRIBUTING.md](CONTRIBUTING.md) explains the format,
the writing rules, how to test on a sample area, and how a contribution moves from
`leap-community` to `leap-core`.

## License

The skills in this repository are released by the Stockholm Environment Institute under the
[Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/)
license (CC BY-SA 4.0): see [LICENSE](LICENSE). You may copy, change and share them, and build on
them, as long as you credit SEI and share what you make under the same license. The license
covers these files only, not LEAP itself.
