---
name: leap-build-scenario
description: Build a policy or sensitivity scenario in a LEAP area and compare it with its baseline, through the LEAP MCP tools. Use when the user asks to "create a scenario", "model a policy", "what if" questions (efficiency standards, fuel switching, electrification, a renewable target, a carbon price, faster growth), or to compare scenarios. Covers choosing the parent scenario, deciding which cells to change, entering the changes, calculating, and reporting differences against the baseline.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: leap_status, get_area, add_scenario, get_branches, find_branches, get_branch, get_expression, get_notes, set_expression, set_expressions, calculate, get_values, show_in_leap, read_view, get_changes, search_help, save_area, save_version
  tested-on: Freedonia (sample area)
  status: draft for review
---

# Building a scenario

A scenario in LEAP is a story about the future that differs from its parent scenario only where you
enter a different expression. Everything else is inherited. A good scenario therefore changes few
cells, each for a stated reason, and is compared against the scenario it inherits from.

This skill assumes you know the area (leap-orientation) and how to write expressions
(leap-expressions).

## Step 1: Agree what the scenario is

Before touching LEAP, restate the policy in LEAP's terms and confirm with the user:

- **Which quantities change**: a share of sales, an efficiency, an energy intensity, a capacity, a
  growth rate, a Key Assumption. Name the branches and variables you will change.
- **By how much and by when**: the target values and years. Where the user gives a direction but no
  number ("more efficient"), propose a number and say it is your assumption.
- **From which baseline**: the scenario it will inherit from, usually the one `get_area` shows as
  the first child of Current Accounts, or the one the user names.
- **What stays the same**: say it. A scenario about cooking fuels does not touch transport.

When the request names the quantities, numbers and years clearly, state your reading in one
sentence and go on; ask only where the model does not match the words (they talk about "cars" and
the model has only "Passenger Road"). Check `get_area` for an existing scenario on the same
policy (areas often hold single-measure scenarios); read its expressions with `get_branch` and
tell the user it exists.

## Step 2: Check access and results

`leap_status`: `assistantAccess` must allow adding scenarios. If results are out of date, the
baseline numbers you compare against later will need a calculation too; say so.

If the user wants a safety net before a batch of changes, `save_version` with a comment makes a copy
they can go back to. Ask before calling it: it saves the area.

## Step 3: Create the scenario

`add_scenario` with a clear `name`, `based_on` the baseline, and a short `abbreviation` (up to 8
characters; it appears in chart legends). The new scenario is empty: every cell inherits from the
parent until you enter one. It is marked as one you may edit.

Do not edit an existing scenario the user built unless they ask. Do not put a policy into Current
Accounts.

## Step 4: Find the cells and read them first

For each quantity from step 1:

1. `find_branches`, then `get_branch` with the **baseline** scenario (the new scenario inherits
   everything, so reading it tells you only what the baseline says) to see the branch's variables,
   units and expressions.
2. `get_values` for the baseline over the whole period (one call returns every year), so you know
   the starting point and its shape.
3. Decide the expression. Common forms:
   - A target share reached in a year: `Interp(2035, 80)` runs from the base-year value (often 0
     for a new technology) in a straight line to 80 in 2035 and holds 80 after; to start the ramp
     later, `Interp(2025, 0, 2035, 80)`. Adjust the neighbors or rely on a `Remainder(100)` among
     them so the set still sums to 100.
   - A change relative to the baseline: `BaselineValue * Interp(2030, 1, 2050, 0.8)` keeps the
     baseline's own shape and scales it. Use it for intensities and efficiencies.
   - A faster or slower driver: `Growth(4%)` in place of `Growth(3%)` on the Key Assumption that the
     demand expressions actually refer to. Check with `get_expression` that they do.
   - New capacity: an `Exogenous Capacity` series at a Transformation process, as `Interp` or `Step`
     in the unit the process uses.
   - A standard for new devices in a stock-turnover branch: change the Sales Share or the new-device
     intensity (Fuel Economy, energy per device), not the stock average.

## Step 5: Enter the changes

One cell: `set_expression`. A set that must stay consistent (a full set of shares, several
technologies of one end use): `set_expressions` in one call, scenario set to the new scenario; if
any one change is invalid, nothing is entered and the answer says what is wrong. Fix and resend.

Read back with `get_values` in the new scenario over the whole period and check the shape: where
the ramp starts (the base-year value, not the first scenario year), where it ends, and that it
holds after the last year. Check the neighbors too.

Describe the scenario in your reply (what changed, where, why). Notes belong to branches, not
scenarios, so there is no note to write for a scenario; the user can paste your description into
the Manage Scenarios screen. When the user wants nothing saved, say nothing more about notes.

## Step 6: Calculate

`calculate` runs only the scenarios whose results are out of date, usually just the new one. Tell
the user LEAP is calculating (seconds for a small area, minutes for a large one; the user cannot
use LEAP meanwhile), then `leap_status` every few seconds until it reports the calculation ended. If it failed, report the message as LEAP
gave it and stop; do not try to work around a calculation error by changing data.

Only scenarios marked for calculation in LEAP get results. A scenario you added is normally marked;
`get_area` shows `includedInResults`.

## Step 7: Compare and report

Read the same result for baseline and new scenario in one `get_values` call, `scenarios` set to
both, with the unit named:

- Demand: `Final Energy Demand` at the Demand branch, and at the sector the policy touches, with
  `filter` by fuel where fuel switching is the point. A readable unit helps: GWh for electricity.
- Emissions: the whole-system total is `One_Hundred Year GWP Direct At Point of Emissions` at the
  root branch (the area's own name, listed first by `get_branches`; `get_branch` on it lists the
  exact result names). The "Direct and Indirect ... Allocated to Demands" versions at a demand
  branch show the effect of that demand including the power plants behind it. Use a unit such as
  `Million Metric Tonnes`.
- Supply: `Outputs` or `Requirements` at the relevant Transformation module; `Capacity` at
  processes if capacity changed.
- Costs, only if the area has cost data switched on: social cost results at the root branch.

Before reporting, check the size of the effect by hand from the inputs (80% of lighting at 30% of
the energy leaves 0.2 + 0.8 × 0.3 = 44% of the baseline) and compare with the branch result.
Report differences as numbers with units and as percent of the baseline, in two or three years, in
a short table. State what drove the change in LEAP's terms. If a result moved that should not have,
say so and look for the cause before presenting the comparison. `read_view` may return a different
scale than the unit you asked for; say which you report.

To show the user, `show_in_leap` with `view` Results, the result variable, `x_axis` Years, `legend`
Scenarios, `select` both scenarios. Then `read_view` to confirm what is on screen. The user sees the
chart in LEAP; describe it in words in the conversation, or draw a chart from the numbers.

## Step 8: Leave it tidy

- Say exactly which cells you changed, in which scenario, and that nothing is saved until the user
  saves or agrees to `save_area`.
- `get_changes` lists everything you did; offer it if the user wants to check.
- If the user wants the scenario kept, ask before saving. If not, they can leave the area without
  saving.

## Rules

- One scenario per policy. A package scenario that combines several can be built on top later.
- Change the expression that actually gives the number, not a Key Assumption nothing refers to.
- Never change Current Accounts or the user's own scenarios without asking.
- Prefer relative forms (`BaselineValue * ...`) for efficiencies and intensities, absolute targets
  for shares and capacities.
- Years before the first scenario year are Current Accounts in every scenario: compare from the
  first scenario year on.
- Say which numbers are the user's, which are the model's, and which are your assumptions.

## Example

User: "Make a scenario where half of urban cooking is electric by 2040 and tell me what it does to
emissions."

1. `get_area` → baseline "Reference"; `leap_status` → access: own scenarios; results current.
2. `add_scenario` name "Electric Cooking", based_on "Reference", abbreviation "ECOOK".
3. `get_branch` `Demand\Household\Urban\Cooking` scenario "Electric Cooking" → children with
   Activity Level in percent share: Electricity 5, LPG 40, Charcoal 35, Wood `Remainder(100)`.
4. `set_expressions`: Electricity `Interp(2040, 50)`; LPG `Interp(2040, 25)`; Charcoal
   `Interp(2040, 15)`; Wood stays `Remainder(100)`. Read back 2040: 50/25/15/10.
5. `calculate`; wait on `leap_status`.
6. `get_values` root branch "Freedonia", `One_Hundred Year GWP Direct At Point of Emissions`,
   scenarios "Reference, ECOOK", 2025 to 2050, unit Million Metric Tonnes; also Final Energy
   Demand at Cooking with `filter` `Fuel=Electricity`, unit GWh.
7. Report: emissions down by X Mt (Y%) in 2040, electricity demand for cooking up Z GJ; note that
   grid emissions from the extra electricity are included because Transformation is calculated.
8. `show_in_leap` Results chart, Years × Scenarios. Nothing saved; ask.
