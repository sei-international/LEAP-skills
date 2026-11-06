---
name: leap-model-review
description: A structured, read-only review (audit) of a whole LEAP area before it is used for a report or shared, through the LEAP MCP tools. Use when the user says "review my model", "check the model", "audit this area", "quality check", "is this model ready", "find errors", "before I submit", "sanity check my scenarios", or asks whether a model can be trusted. Covers the frame (years, scenarios, regions, units), structure, data (shares, saturations, scales, growth rates, Remainder, Key Assumptions), supply, emissions, results and base-year calibration, documentation, how to sample a large model, and a findings list ordered by severity. Changes nothing.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: leap_status, get_area, get_notes, get_branches, find_branches, get_branch, get_expression, get_values, list_fuels, get_changes, show_in_leap, read_view, api_get, api_describe, search_help, read_help_topic
  tested-on: "Freedonia, LEAP 2026.9.0.18, 2026-11-06 (read-only)"
  status: draft for review
---

# Reviewing a LEAP model

A review reads a whole area with a checklist and gives the user a list of findings, ordered by how
much each one matters. It is what a careful colleague would do before a model goes into a report,
a submission or another person's hands. It changes nothing: no expression, no scenario, no note, no
save. The user decides what to fix, and how.

Run it when the user asks for one, before a report or hand-over, after a large import of data, or
when results look wrong and the user does not know where to start. If you have not read the area
yet, do the leap-orientation steps first; the review builds on them.

**What it produces:** a findings table in four severities, each finding naming the branch, the
variable, the scenario, the region, what you saw, and what to check in LEAP:

| Severity | Meaning | Examples |
|---|---|---|
| 1 Error | Stops the calculation or distorts results | Shares that do not sum to 100; a technology with no fuel; a demand fuel nothing produces; capacity in MWh |
| 2 Likely mistake | Probably not what the modeler meant | Saturation where a share was meant; Growth(5%) for 30 years with no source; a scenario cell copying the parent |
| 3 Documentation gap | The model works but cannot be checked by others | No area notes; sectors without sources; undated data; scenarios without a description |
| 4 Suggestion | Would make the model clearer or more robust | A Key Assumption nothing refers to; Remainder(100) missing from a share set that still sums to 100 |

## Rules for the whole review

- Read only. Never call `set_expression`, `set_expressions`, `add_scenario`, `set_notes`,
  `save_area`, `save_version`, `api_set`, `api_call` or `open_area` during a review, even when the
  fix is obvious and the user's access would allow it. Describe the fix; let the user make it.
- `calculate` only when the user agrees, and say first that LEAP is blocked while it runs.
  `show_in_leap` starts a calculation by itself when results are out of date, so do not call it
  until `leap_status` says results are up to date or the user has agreed to a calculation.
- Use the names the tools return, exactly. Match the user's words ("Reference", "BAU") to the
  scenarios `get_area` lists and say which you took.
- Say for each finding whether you verified it (read the cell or the number) or inferred it (from a
  sample, a name, a pattern). Never report an inference as a fact.
- Look things up before calling them wrong: `search_help` and `read_help_topic` for any variable or
  function you are not sure of. The Frequently Asked Questions topic (section Technical Support)
  and the Diagnostics topic (section Views) answer most "is this an error" questions.
- Review through the tools, not through an Excel export of expressions: the export can list
  variables a branch no longer has after its analysis method changed.
- `get_branch` names in `variablesFor` the scenario its variable list belongs to: the one you
  asked for, or else the one selected in LEAP. Name a simulated scenario when you want dispatch
  variables, even while an optimization scenario is on the user's screen. Its answer also gives
  `fuel` (technologies, fuel branches) and, for a process, `feedstockFuels` and `auxiliaryFuels`.

## Sampling a large model

Reading every cell of a model with a few thousand branches is not possible and not needed. Sample
with intent and say what you sampled:

- **Every** top-level branch, every sector under Demand, every Transformation module and its
  process list, every Key Assumption, every scenario in `get_area`, every region.
- **One full path per sector** from the sector down to a technology and its effect branches, chosen
  where the energy is: with up-to-date results, `get_values` `Final Energy Demand` at each
  subsector and follow the largest; without results, follow the first child at each level and one
  more that the notes or names mark as important (electricity, transport fuels).
- **Every share set on a sampled path** (all neighbors, not just the one you reached). `get_values`
  reads one branch per call, so checking every neighbor in every scenario and year is beyond the
  budget. For shares, read the expressions with `get_branch` and check that one neighbor holds
  `Remainder(100)` and the others are plain numbers or `Interp`; use `get_values` only for one or
  two sets in one year.
- **Ten to twenty technologies** in all for a model of a few hundred branches; more only where the
  first findings cluster. In a multi-region area, read two regions in full and spot-check the rest
  for the share sets and the base-year totals.
- **Years:** sample the base year, the first scenario year, a middle year divisible by 5, and the
  end year. These are the years LEAP itself checks shares in, plus the ends of the horizon.
- Budget: 40 to 80 tool calls for a model of a few hundred branches. Stop when a section repeats
  the same finding; report the pattern once with the branches you saw.

## The checklist

Work through the sections in order. Each line says which tool to call and what to look at.

### (a) Frame

1. `leap_status`: ready; which area; `resultsUpToDate`; `assistantAccess`. Note the access level
   in the report; it does not change what a review does.
2. `get_area`: base year, first scenario year, end year, energy unit, currency; the scenario tree
   with `parentId`, `includedInResults`, `hasResults`, `needsCalculation`; regions with
   `includedInResults`; the `branches` count. Findings: a scenario the user names as part of the
   report but not marked for calculation (error for the report); a policy scenario whose parent is
   not the baseline the user describes (likely mistake); a horizon that ends before the target year
   the user mentions; years between the base year and the first scenario year (those show Current
   Accounts in every scenario). `api_get` on `Scenarios("name")` shows the additional scenarios a
   scenario inherits from first; a package scenario missing a member the user expects is a finding.
3. `get_notes` with no branch: area notes present, naming purpose, base-year sources and the date
   of the data. Absent or one line: documentation gap.
4. `list_fuels`: the fuel names you will see in filters and in the Energy Balance.
5. `get_changes`: edits made by assistants on this computer. On a working machine the list can
   be long. Ignore scenarios and edits the user says are tests. Report the rest as "recent
   assistant edits, confirm they are intended"; they are not a fault in themselves. Test
   scenarios still marked for calculation are a likely mistake before a report.

### (b) Structure

1. `get_branches` with no parent, `depth` 2, then one sector at a time with `depth` 0 for the full
   list. Top-level branches with negative IDs (Non Energy, Indicators, Effects, Load Shapes) are
   read with `get_branch` by ID or full name, which lists their children; then `get_branch` on
   each child.
2. **Every technology has a fuel.** `get_branch` on each sampled technology: a technology branch
   with no fuel is an error (LEAP's Diagnostics lists these as demand branches not fully defined).
3. **Mixed neighbors.** At each sampled level, the branch types of the children: a technology beside
   a category is allowed in some places and refused in others; report it as a suggestion to check,
   not an error, unless `get_branch` shows that the odd branch has no intensity or fuel.
4. **Effect branches under combustion technologies.** `get_branches` below a sampled technology,
   `depth` 0: one effect branch per pollutant with its factor. A technology burning a fuel with no
   effect branches is a likely mistake when the area reports emissions. A technology using
   electricity, heat or hydrogen correctly has none; do not flag it.
5. **Module order.** `get_branches` parent Transformation, `depth` 1: Transmission and Distribution
   above Electricity Generation, conversion modules above extraction modules (Oil Refining above
   Oil Production, Coal Mining last). Wrong order is an error.
6. **Every demand fuel produced or imported.** For each fuel in `list_fuels` that a sampled
   technology uses: a module whose Output Fuels branch includes it, or a Resources branch that
   allows imports. Read the module's Output Fuels branch with `get_branch` (by full name, for
   example `Transformation\Electricity Generation\Output Fuels`, or by the child ID listed at the
   module); its children are the fuels, each readable with `get_branch`. A fuel
   nothing produces and nothing imports is an error (requirements stay unmet). A primary fuel
   (hydro, nuclear, wind) with no branch under Resources: Primary shows up as an import in the
   Energy Balance; likely mistake (see the FAQ on nuclear, hydro or hydrogen shown as imports).

### (c) Data

For each sampled path, `get_branch` with the baseline scenario (every variable, its unit, scale,
expression and whether it is inherited) and `get_values` for the sample years. Then repeat
`get_branch` for each other calculated scenario and, in a multi-region area, for a second region.

1. **Shares sum to 100.** Where the Activity Level unit reads `% Share/...`, read the neighbors'
   expressions with `get_branch` (one `Remainder(100)`, the rest plain numbers or `Interp`) and
   `get_values` one or two sets in one year to add them up. LEAP allows 0.2% either way; outside that is an error (a warning only if the area has "Do not
   check that share values sum to 100%" ticked, and then results are distorted silently). Other
   share-type variables (Sales Share, Process Share under PercentShare, Output Shares, Fuel Share)
   follow the same rule.
2. **Saturations within 0 to 100.** Where the unit reads `% Saturation/...`, each value is between 0
   and 100 in every year; above 100 stops the calculation. The sum across neighbors may exceed 100
   by design. Share and saturation units cannot be mixed among immediate neighbors.
3. **Scale and unit sanity.** Read unit and scale with every value: a Final Energy Intensity of 1000
   GJ per household per year for lighting, a population of 51,200,000 in a cell scaled Million, a
   capacity of 500 in a variable whose unit is GW. Off by a round factor (1000, 1,000,000, 3.6,
   41.868) is a likely mistake; compare against the notes or the user's statistics before calling
   it an error. A percent scale on a variable with a real unit (GJ, tonnes) is reported by LEAP at
   calculation; flag it.
4. **Growth rates over long horizons.** `Growth(x%)` over the horizon: compute the factor
   ((1 + x)^years; 5% over 30 years is ×4.3). Large factors with no note or Key Assumption behind
   them are a likely mistake to confirm with the user; they are not errors.
5. **Remainder in exactly one neighbor.** In each share set: no `Remainder(100)` is a suggestion
   when the set still sums to 100 and a likely mistake when scenario values move; two Remainders
   or a Remainder beside a saturation set is an error.
6. **Orphaned Key Assumptions.** `get_branches` parent Key Assumptions `depth` 0. While reading
   expressions, note every `Key\...` reference. A Key Assumption never referenced on any sampled
   path is a suggestion, reported as inferred ("not referenced in the branches I read"), with the
   usual sign: a Households Key Assumption beside a `Demand\Household` that grows by its own
   `Growth(3%)`.
7. **Scenario cells that only duplicate the parent.** `get_branch` with a policy scenario: for each
   variable not marked inherited, `get_expression` in the parent scenario. Identical text is a
   suggestion: the copy hides any later change to the parent. Many copies at once (a scenario
   created by copying) are a likely mistake.
8. **Current Accounts values in a scenario.** A scenario cell holding a plain number equal to the
   base-year value, or a `Data(...)` series of historical years, freezes that variable for the
   whole horizon: likely mistake. The reverse, `Growth` or `BaselineValue` in Current Accounts, is
   refused by LEAP, so you will not see it.
9. **Regions.** Where regions inherit from a parent region, a value entered only in the parent is
   fine by design; a value entered in one child region and not the others may be a mistake. Say
   which region each finding belongs to.

### (d) Supply

`get_branch` on each module and on each process of the modules that matter (electricity
generation always; others on the sampled fuels), in the baseline and in one policy scenario.

1. **Capacity.** Exogenous Capacity present and non-zero for processes with Historical Production
   (zero capacity with non-zero production is an error LEAP reports); unit MW, not MWh or GW
   unless the area says so; cumulative versus additions as the module is set up (the help topic
   "Specifying Capacity Data"). Capacity that ends (retires) with nothing replacing it and no
   endogenous candidates: likely mistake.
2. **Availability.** Maximum Availability between 0 and 100 and plausible for the kind of plant
   (solar and wind far below baseload plants); zero means the plant never runs.
3. **Efficiency.** Process Efficiency greater than zero and in the form the module expects
   (efficiency, heat rate or losses; losses are percent lost, not kept). Values above 100% for a
   plant, or below 10% for Transmission and Distribution efficiency, are likely mistakes.
4. **Dispatch rule versus data.** PercentShare needs Process Share summing to 100 across the
   processes; MeritOrderDispatch and RunningCost need a Merit Order (or costs) and a System Load
   Shape on the output fuel (`ShapeFromDemand` belongs to the fuel's shape, never to a demand
   branch); ProportionalToCapacity needs capacity. First Simulation Year after the base year
   needs Historical Production for the years before it.
5. **Reserve margin.** Planning Reserve Margin at the module (shown only when LEAP is not
   calculating it endogenously) and, if endogenous additions are expected, Addition Size and
   Addition Order at the candidate processes; without candidates the margin can only be reported,
   not kept.
6. **Shortfall and surplus rules.** These sit at each module's Output Fuels branch: `get_branch`
   on `Transformation\<module>\Output Fuels`, then on the fuel branch under it, for Shortfall
   Rule, Surplus Rule and Import Target. A shortfall rule set to import where the user expects domestic
   supply, or to leave requirements unmet, is a finding to raise. `Optimize` set to Yes in a
   scenario needs cost data and NEMO on the user's computer.
7. With results: `get_values` `Capacity`, `Capacity Added`, `Peak Power Requirements` and
   `Outputs by Output Fuel` at the module and `Capacity` at processes for the sample years.
   `get_values` `Reserve Margin`, `Load Factor` and `Maximum Availability` (and `Actual
   Availability`) with no `unit`: they come back as percentages with unit `Percent`. Capacity ÷
   Peak Power Requirements is the margin before capacity credits, useful to explain a gap between
   the two. Imports of a fuel the user says is produced at home, or a margin that collapses, are
   likely mistakes.

### (e) Emissions

1. Energy effects switched on: ask the user to confirm that Energy Sector Effects is on in
   Settings: Scope & Scale. The tools do not give the setting's name, and reading it would need
   `api_call`. The practical evidence is effect branches under fuel-burning technologies.
2. Global warming potentials: `api_get` `Effects("Carbon Dioxide")` and
   `Effects("Methane (Combustion and Biogenic)")` for GWP20, GWP100, GWP500 and UsedInArea.
   (`api_get` `Effects` alone returns every effect LEAP knows, about 390, names only.) The root
   variable `IPCC GWP Values` = 0 means the General: Effects table is in use. The CH4 and N2O
   100-year values name the IPCC set: SAR 21/310, AR4 25/298, AR5 28/265, AR6 27.9/273. A
   greenhouse gas with a GWP of zero, or an area whose notes name one IPCC assessment report while
   the values come from another, is a likely mistake. The user sets them in General: Effects.
3. Factors present: from (b) 4, every fuel-burning technology and process sampled has effect
   branches with non-zero factors (`get_expression` on the effect branch's loading variable).
4. Zero-emission fuels: biomass CO2 factors set to zero (biogenic convention), and solar, wind,
   hydro and electricity-using technologies with no effect branches, are design choices. Note
   them once in the report; do not list them as findings.
5. With results: `get_values` on the root branch (the area's name) for the GWP total whose exact
   name `get_branch` lists there (for example `One_Hundred Year GWP Direct At Point of
   Emissions`), unit `Million Metric Tonnes`, baseline and policy scenarios, sample years. A total
   of zero, or one that falls in the policy scenario before any measure starts, is a finding.

### (f) Results and calibration

1. `leap_status` `resultsUpToDate` and `get_area` `hasResults`. If results are out of date, report
   it and ask whether to `calculate`; do not call `show_in_leap` first. Without results, skip the
   rest of this section and say so in the report.
2. **Base-year Energy Balance against the user's statistics.** `show_in_leap` view
   `Energy Balance`, the base year, the unit of the user's source; `read_view`. Compare total
   final consumption by sector and fuel, transformation inputs and outputs, imports and
   production, with the figures the user gives or the notes cite. Differences above a few percent
   are likely mistakes with the branch to look at; a non-zero Unmet Requirements row is an error.
   Current Accounts has no stored results: read the base year of a calculated scenario.
3. **Scenario differences begin where expected.** `get_values` `Final Energy Demand` at Demand and
   at each sector, every calculated scenario, first scenario year to end year. The first year a
   policy scenario differs from its parent should match the start of its measures (a measure
   starting in 2027 is design, not a fault). Identical lines through the whole horizon mean the
   scenario inherits everything: likely mistake.
4. **No negative or exploding values.** From the same series: negatives are errors; a ratio
   end-year to base-year above what the activity drivers explain (from (c) 4) is a likely
   mistake; a jump in one year is usually a measure or a plant starting; say so and name it.
   **First-scenario-year step.** For each Transformation module, compare `Outputs by Output
   Fuel` and emissions in the base year and the first scenario year. A jump means Historical
   Production and the dispatch rule disagree: in Freedonia, emissions rise 23% in 2021 because
   coal and hydro share merit order 1 and dispatch replaces the historical shares. Report it as a
   likely mistake, naming the Merit Order and Maximum Availability cells to check.
5. **Diagnostics.** You cannot read the Diagnostics tab through the tools. Tell the user where it
   is: the Results view, Diagnostics tab, shown only when there are messages, with errors (which
   stopped a scenario), warnings and information, filtered by scenario, region and year; a
   double-click goes to the branch in the Analysis view. Messages for scenarios not marked for
   calculation are not shown. Ask the user to read it and tell you what it lists; add those lines
   to the findings.

### (g) Documentation

1. `get_notes` on each sector, each Key Assumption, each module and the sampled technologies.
   Findings: no notes on a sector or Key Assumption; sources without a date or a year; numbers in
   the notes that disagree with the expression beside them (likely mistake, not a gap).
2. Scenario descriptions: the tools do not return them (`api_get` `Scenarios("name")` gives no
   description). Ask the user to read them in Manage Scenarios. Each calculated scenario should
   say what it assumes and from when.
3. Tell the user that notes and names can be edited without making results out of date, so
   closing documentation gaps costs no recalculation.

## Reporting

Give the user, in plain words and LEAP's own terms:

1. One paragraph: the area, its years and scenarios, what you sampled (which sectors, paths,
   regions, years), whether results were current, and the counts of findings by severity.
2. The findings table, ordered by severity, then by sector:

   | # | Severity | Branch | Variable | Scenario | Region | What was found | What to check in LEAP | Verified or inferred |
   |---|---|---|---|---|---|---|---|---|

   "What to check in LEAP" names the place: the Analysis view at that branch and variable, with
   that scenario and region selected; the Energy Balance for a year; General: Effects; Manage
   Scenarios; the Diagnostics tab.
3. What you did not review (sections skipped, branches not sampled, the Diagnostics tab) and why.
4. A closing line: nothing was changed, calculated or saved by the review (or: one calculation was
   run with the user's agreement). Offer to go through the fixes one at a time with the user in
   control.

Keep it short. A model with no serious findings gets a short report that says so and still lists
what was checked.

## Common mistakes of reviewers

- Flagging designed behavior: a measure that starts later than the first scenario year; a policy
  line identical to the baseline until then; a plant that stops after the First Simulation Year
  because the merit order no longer needs it; a biomass CO2 factor of zero.
- Reading a saturation as a share and reporting that the neighbors do not sum to 100. The unit
  says which it is.
- Treating a different scale as an error: 51.2 Million People is right; so is a cost in Thousand
  dollars. Read the scale with every value before comparing.
- Calling a scenario "not calculated" when the user never meant it to be: single measures are often
  left unmarked and bundled into a combined scenario.
- Reporting "the Key Assumption is unused" as a fact after reading three branches. It is inferred.
- Assuming a value comes from the parent scenario when it comes from a package scenario or a
  parent region; `get_expression` says where it was found.
- Comparing scenarios in years before the first scenario year.
- Starting a calculation, or a `show_in_leap` that triggers one, without asking.
- Fixing a finding because access allows it. A review changes nothing.
- Writing the report in modeling jargon instead of the words the user sees in LEAP.

## Example (illustrative)

User: "Can you check this model before I send it to the ministry?"

1. `leap_status` → ready, area "Freedonia", results up to date, access: edit anything (ignored:
   the review is read-only). `get_area` → base year 2020, first scenario year 2021, end year 2050,
   one region, 390 branches; Current Accounts → Baseline → Mitigation calculated; six single-
   measure scenarios not marked. `get_notes` → a training model of an imaginary country, sources
   named, undated. `list_fuels`, `get_changes` (none).
2. Structure: `get_branches` depth 2; sectors Household, Industry, Transport, Commercial; modules
   Transmission and Distribution, Electricity Generation, Charcoal Production, Oil Refining, Coal
   Mining, in that order. Paths sampled: Household\Urban\Electrified\Cooking (all fuels),
   Industry\Iron and Steel, Transport\Passenger\Cars, Commercial\Lighting. Effect branches present
   under every fuel-burning technology read.
3. Data: cooking shares sum to 100 in 2020, 2021, 2035, 2050 in both scenarios; Rural electrified
   uses `Remainder(100)`. `Demand\Household` grows by `Growth(3%)` (×2.4 by 2050); the Households
   Key Assumption is not referenced on any sampled path. Mitigation holds its own copy of an
   Industry intensity identical to Baseline.
4. Supply: eight processes, MeritOrderDispatch, Planning Reserve Margin 35%, Optimize No; Maximum
   Availability and efficiencies plausible; Hydro has a Resources: Primary branch.
5. Results: Energy Balance 2020 read; Mitigation diverges from Baseline in 2022 (Efficient
   Lighting starts then: design). GWP total read for both scenarios, no negatives. User asked to
   read the Diagnostics tab: no messages.
6. Report: 0 errors; 1 likely mistake (duplicate Industry intensity in Mitigation, verified); 2
   documentation gaps (area notes undated; no notes on Key Assumptions); 1 suggestion (Households
   Key Assumption not referenced, inferred). Nothing changed or saved.
