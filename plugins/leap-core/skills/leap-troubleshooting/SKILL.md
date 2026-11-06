---
name: leap-troubleshooting
description: Diagnose problems in a LEAP model or in working with LEAP through the MCP tools: a calculation that stops with an error, shares that do not sum to 100, "no results available", results that look wrong or out of date, a plant that does not generate, emissions missing, a tool that refuses, LEAP busy or waiting on a message, slow calculations, optimization infeasible. Use when the user reports an error message, an unexpected number or something that "doesn't work" in LEAP.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: leap_status, get_area, get_values, get_expression, get_branch, get_branches, find_branches, get_notes, list_fuels, get_changes, search_help, read_help_topic, show_in_leap, read_view
  tested-on: Freedonia (sample area)
  status: draft for review
---

# Troubleshooting in LEAP

Start from what LEAP said, not from a theory. Quote the message, find where it points (branch,
variable, scenario, region, year), read that cell, and only then explain. The help's Frequently
Asked Questions topic and the Diagnostics topic (section Views) cover the common cases; read them
with `read_help_topic` when a case matches.

## First: what state is LEAP in?

`leap_status` answers most "nothing works" reports:

| It says | What it means | What to do |
|---|---|---|
| not ready, calculating | A calculation is running | Wait; call again. Do not start another. |
| a message is waiting for the user | LEAP shows a dialog | Tell the user to answer it in LEAP; you cannot. |
| `resultsUpToDate: false` | Data changed since the last calculation | Results tools return nothing; `calculate` when the user agrees. |
| `assistantAccess: read only` | The user limited assistants in Settings: Scripts & AI | Say so; the user changes it in LEAP if they want. |
| no area open | | The user opens one, or `open_area` if allowed. |
| last calculation failed | | Read the message it gives; see below. |

## A calculation stopped with an error

The message names a branch, variable, scenario, region and year. Then:

1. `get_expression` for that cell in that scenario and region: is the expression what the user
   intended? Is it inherited from a parent scenario (then the fix belongs there)?
2. `get_values` for the years around the error, in that scenario, to see the value that broke the
   rule.
3. Match the message to its rule:
   - **Shares do not sum to 100**: read every neighbor's expression in that scenario; one was
     changed without the others, or `Remainder(100)` was replaced. Fix the set together with
     `set_expressions`.
   - **Value out of range (negative, above 100%)**: a growth rate too long, a subtraction gone
     negative, a scale error (5 entered for 5%).
   - **Division by zero**: a reference to a variable that is zero in that year (an activity before
     a First Sales Year, a capacity retired).
   - **Circular reference**: an expression refers to a result that depends on itself; the help
     topic on referencing results says what a data variable may read.
   - **Fuel not produced / module order**: a Diagnostics message rather than an error; see
     Transformation below.
4. Propose the fix, in the scenario where the expression lives, and apply it only with agreement.
   If the IDE setting lets LEAP continue after errors, the Diagnostics tab lists every failed
   scenario at once; tell the user it exists.

## Results look wrong

Before anything else, match the user's words to the area: `get_area` lists the scenarios (many
areas have no scenario called "Reference"; the baseline may be "Baseline" or another name) and
says which are marked for calculation. Then:

- **Out of date**: step one above.
- **Identical in every year, or blank**: the scenario is not marked for calculation
  (`includedInResults: false`, `hasResults: false` in `get_area`). It has no results of its own;
  the user ticks it in Manage Scenarios and calculates.
- **Same as the baseline in the base year**: always true; every scenario starts from Current
  Accounts.
- **Same as the baseline in the first years, then different**: the measure starts later. Read the
  policy expression: `Interp(2022, 0, 2027, 7, ...)` is zero until 2022; a First Sales Year or a
  growth that begins in a later year has the same effect. Confirm with one `get_values` call for
  both scenarios and name the first year they differ.
- **Zero or missing at one branch**: read the same result at a neighboring branch. A neighbor with
  a number means this branch is genuinely zero (no fuel burned, no stock, measure not started); a
  neighbor that also returns nothing means the variable does not live at this level or results are
  not there.
- **Off by a round factor** (1000, 1,000,000, 3.6, 41.868): a scale or unit. Compare the unit
  `get_values` returns with what the user expects; convert explicitly.
- **Same in every scenario in a later year**: the scenario inherits the cell and the change was
  made elsewhere, or not at all. `get_expression` says where the expression comes from.
- **Changed where nothing was changed**: a parent scenario or Current Accounts was edited.
  `get_changes` lists only what AI assistants changed on this computer (it is for "who changed
  this", not for a results puzzle); the user's own edits are in the area's versions.
- **A Key Assumption change did nothing**: nothing refers to it. Follow Activity Level
  expressions upward with `get_expression` to find what actually drives the number.
- **Demand result missing a fuel**: the technology has no fuel, or the result was filtered to
  another fuel name (`list_fuels` for the exact names).

## Transformation: no generation, shortfalls, imports

Follow the checklist in leap-transformation: `Requirements` zero → nothing upstream needs the
fuel; `Outputs` zero at one process → dispatch rule, capacity, availability, First Simulation Year;
unexpected `Imports` → shortfall rule set to import; a plant that stops after the base year →
Historical Production no longer applies. The Diagnostics tab lists module-order and fuel problems
after a calculation; the user can double-click a line to go to the branch.

## Emissions missing or wrong

- "No results available" under Environment: energy effects switched off in Settings: Scope &
  Scale, or no emission factors below the technologies that burn fuel. The user adds IPCC Tier 1
  defaults with the green double-plus button in the Analysis view, or a factor for one effect.
- The results to read: `Pollutant Loadings` (shown in LEAP as "Environmental Effects (Emissions)
  in Physical Units") is the direct emissions at a branch; add `filter` `Effect=Carbon Dioxide`
  for one gas. The global warming totals have longer names that include the time horizon and
  whether indirect emissions are allocated to demands; `get_branch` lists the exact names at the
  branch.
- A technology using electricity, heat or hydrogen correctly has no effect branches and zero
  direct emissions. Its emissions are counted at the Transformation processes that make the fuel,
  and appear at the demand branch only in the "direct and indirect, allocated to demands" results.
  Say so before suggesting factors be added.
- Emissions where none expected, or none where expected: effect branches sit below the
  technology, one per pollutant, with the factor per unit of energy (or per distance in
  transport). `get_branches` below the technology with `depth` 0 shows them; `get_branch` on an
  effect branch lists its variables and `get_expression` reads the factor.
- Global warming totals differ from the sum of gases: the GWP factors and time horizon in
  General: Effects.

## Optimization

Infeasible or solver failure means the constraints cannot all be met: Maximum Capacity, Maximum
Capacity Additions, Minimum Utilization, Minimum and Maximum Production, Renewable Targets,
Emission Constraints. Suggest the FAQ's method: revert to the last version that solved and
reintroduce changes one at a time, or loosen constraints until it solves and tighten them one by
one. Optimization needs NEMO installed and does not run in a LEAP started by another program.

## A tool refused

- The answer says why. Quote it. Typical: scenario not editable by assistants, access level, an
  invalid expression with LEAP's reason, `Call` in an expression, results out of date, LEAP busy.
- Do not look for another route around a refusal (for example `api_set` where `set_expression`
  was refused). Tell the user what it said and what they can change in LEAP.
- Refusals that are about the call, not the model: `get_values` refuses a `filter` on Branch or
  Year and, for an unknown fuel, effect or other item, names the ones LEAP has (a result in
  percent is read with unit `Percent`); a variable `get_branch` does not list may exist only in
  another scenario (a user variable visible in Current Accounts only), and the refusal says which,
  so call again with that `scenario`; `show_in_leap` refuses a time-sliced result (Energy
  Generation, Power Requirements, load shapes) with Years alone on the X axis: put time slices on
  the X axis, or chart `Outputs by Output Fuel` for yearly generation.

## Slow calculations

The FAQ's advice, for the user to apply in LEAP: calculate only the scenarios they need (Manage
Scenarios), switch off parts of the analysis they do not need in Settings: Scope, temporarily
shorten the End Year, and check that parallel calculation is on in the area's settings. Many
scenarios inheriting from one changed parent all recalculate; that is expected.

## Reporting a problem you cannot solve

Give the user, in plain words: what was asked, what LEAP said (quoted), the cell it points to, what
you checked and found, and what you did not change. If it looks like a fault in LEAP rather than
the model, suggest Help: Check for Updates and the LEAP forum, as the FAQ does, and that they keep
the area as it is so the problem can be reproduced.

## Rules

- Never "fix" by trying expression variations until one is accepted.
- Never change Current Accounts or the user's scenarios to make an error go away without asking.
- Never start a calculation to see whether a problem is still there without telling the user.
- Say what you verified and what you inferred.
