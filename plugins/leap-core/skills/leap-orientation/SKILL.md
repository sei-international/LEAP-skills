---
name: leap-orientation
description: Get to know a LEAP model (area) before doing anything else with it, or explain one to the user. Use when the user opens a conversation about a LEAP area, asks "what is in this model", "summarize this area", "how is this model built", "what scenarios are there", "where does demand come from", or before any task that changes a model you have not yet read. Works through the LEAP MCP tools (leap_status, get_area, get_branches, get_branch, get_notes, get_values).
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: leap_status, get_area, get_notes, get_branches, find_branches, get_branch, get_expression, get_values, list_fuels, search_help
  tested-on: Freedonia (sample area)
  status: draft for review
---

# Orientation in a LEAP model

Before you change, calculate or explain anything in a LEAP area, learn how it is built. Every area is
different: branch, variable, fuel, scenario and region names differ, and may be in another language.
Never rely on what you remember about LEAP or about "typical" models. Read this area.

The result of this skill is a short written picture of the model that you can give the user and that
you keep in mind for the rest of the conversation.

## Step 1: Is LEAP ready, and what may you do?

Call `leap_status`. It tells you:

- whether LEAP is ready or busy (calculating, showing a message the user must answer);
- which area is open and which view the user is looking at;
- whether results are up to date;
- `assistantAccess`: read only, add and edit your own scenarios, or add and edit anything.

If LEAP is busy, wait and call it again. If access is read only, say so to the user before they ask
for a change, and do not look for another way around it.

## Step 2: The frame of the model

Call `get_area`. Note and keep:

| What | Why it matters |
|---|---|
| Base year, first scenario year, end year | Years before the first scenario year show Current Accounts in every scenario. Do not compare scenarios there. |
| Energy unit and currency | Results come in these unless you ask for another unit. |
| Scenarios, with `parentId` | Scenarios form a tree. A scenario inherits every expression from its parent unless it has its own. Draw the tree for yourself. |
| `includedInResults`, `hasResults`, `needsCalculation` | Only scenarios marked for calculation get results. A scenario with `hasResults: false` (and `lastCalculated: null`) cannot be read with get_values until it is marked in LEAP and calculated. Unmarked scenarios are often single measures that a combined scenario builds on. |
| `assistantMayEdit` per scenario, `selectedInLEAP` | Which scenarios you may change; which one the user is looking at. |
| Regions, with `includedInResults` | A multi-region area has one expression per region. A region named "Template" or similar is often a pattern, not a place. |
| `branches` count | The number of branches below the area branch, the same count `get_branches` gives for the whole tree. `get_branches` returns at most 200 branches per call (1000 with `limit`); a sector of a few hundred branches already needs `offset` or a lower `depth`. |

Match the user's words to this list before reading anything else: many areas have no scenario
called "Reference"; the baseline may be "Baseline" or another name. Say which one you took.

Then call `get_notes` with no branch. The area notes are where a modeler describes the model: its
purpose, sources, conventions. Read them first; they often answer the user's question directly.

## Step 3: The shape of the tree

Call `get_branches` with no parent and `depth` 2. This gives the top-level branches and their first
children:

- **Key Assumptions**: the user's own driver variables (population, GDP, prices, shares). They matter
  only where an expression refers to them.
- **Demand**: sectors, subsectors, end uses, technologies. The structure tells you the demand
  method (see step 4).
- **Transformation**: modules in calculation order (for example Transmission and Distribution,
  Electricity Generation, Charcoal Making, Oil Refining). Each module has processes and output fuels.
- **Resources**: primary and secondary supply, with reserves and yields where the user entered them.
- Others, present only in some areas: Stock Changes, Statistical Differences, Non Energy (non-energy
  sector effects), Indicators. The tree also holds Effects and Load Shapes branches that are
  settings rather than model structure.

Some of these top-level branches have negative IDs (Non Energy, Effects, Load Shapes,
Indicators); `get_branch` reads them by ID or full name and lists their children. A module's
Output Fuels branch is read the same way (`Transformation\Electricity Generation\Output Fuels`),
and the fuel branches under it hold the Shortfall Rule, Surplus Rule and Import Target.

For a large tree, go down one branch at a time with `get_branches` and a `parent`, rather than asking
for every level at once. Use `find_branches` when the user names something. Under each technology
there is usually one Environmental Effect branch per pollutant (CO2, CH4, N2O, ...): they hold
emission factors, and you can skip them when describing structure.

Call `list_fuels` once. Fuel names are used in result filters (for example `Fuel=Electricity`), and
the list tells you whether the area uses electricity, biomass, charcoal, hydrogen and so on.

## Step 4: How demand is modeled

Pick two or three demand branches that matter to the user's question and call `get_branch` on each,
with the scenario the user cares about. Look at the branch type and its data variables:

- **Activity Level** at every level, with **Final Energy Intensity** at the lowest branch beside its
  fuel: this is the common activity-analysis method. Activity levels multiply down the tree
  (households × share urban × share with a refrigerator). The unit of Activity Level says whether a
  level is an absolute number, a share of its parent (must sum to 100% across neighbors), or a
  saturation (may add to more than 100%).
- **Activity Level** in passenger-km or tonne-km with a **Final Energy Intensity** in a volume or
  energy unit per km: transport by the activity method (no vehicle stock).
- **Stock**, **Sales**, **Device Lifetime**, vintages: stock-turnover method (vehicles, appliances).
- **Useful Energy Intensity** with an efficiency: useful-energy method.
- **Transport** branches with **Mileage** and **Fuel Economy**: transport stock-turnover.

`get_branch` with a `scenario` returns every data variable's expression at once and says whether
each is inherited (not from which scenario; `get_expression` per parent scenario tells you that
when it matters). Its `expressionsFor` field names the scenario the expressions belong to, and
`variablesFor` the scenario the variable list is for (the one you named, else the one selected
in LEAP). The answer also gives the branch's `fuel` and, for a Transformation process, its
`feedstockFuels` and `auxiliaryFuels`.

Read the notes of these branches with `get_notes`. Modelers put sources and assumptions there.

To learn what drives a result, read the Activity Level expression of the branch and of each branch
above it, and follow any Key Assumption it refers to. Check whether the Key Assumptions are
referenced at all: a model may hold a Households key assumption while the Household branch grows
by its own `Growth(3%)`. Change nothing yet.

## Step 5: How supply is modeled

Call `get_branches` with `parent` set to the Transformation branch and `depth` 1 for the module
order, then `depth` 2 under the module that matters (its Processes and Output Fuels branches and
what is under them). For the module the user cares about (usually electricity generation), call
`get_branch` on the module and on one or two processes and note the variables present: Exogenous
Capacity, Process Efficiency, Dispatch Rule, Merit Order, Maximum Availability, Capacity Credit;
at the module, Planning Reserve Margin and `Optimize` (expression Yes or No per scenario) say how
capacity is planned and whether optimization is on.

## Step 6: A few numbers to anchor the picture

Results are only readable when both hold: `leap_status` says results are up to date, and
`get_area` says the scenario has results. Do not start a calculation just to orient yourself; tell
the user results are out of date and let them decide.

With up-to-date results, three calls give a sense of scale:

1. `get_values` on the Demand branch, variable `Final Energy Demand`, for the baseline scenario,
   `first_year` and `last_year` set to the first scenario year and the end year.
2. The same with `filter` `Fuel=Electricity` (use a fuel name from `list_fuels`).
3. `get_values` on the root branch (the area's own name) for a greenhouse-gas total, with a `unit`
   such as `Million Metric Tonnes`. Take the exact variable name from the result variables that
   `get_branch` lists at that branch (for example `One_Hundred Year GWP Direct At Point of
   Emissions`, with the underscore); `search_help` does not give exact variable names.

Read the unit and scale returned with every value. A value of 5 with unit "Million Tonnes" is
five million tonnes.

## Step 7: Write the picture

Give the user a short summary in LEAP's own words (area, branch, variable, scenario, expression,
Current Accounts, region). Cover:

- What the model is for (from the area notes) and its years and units.
- The scenario tree: which scenario is the baseline, which policy scenarios hang off it, which are
  marked for calculation.
- How demand is structured, sector by sector, and which method each uses.
- What Transformation covers.
- Whether results are current, and two or three headline numbers if they are.
- Anything that looks unusual or that you could not read, stated plainly.

Point the user to where they can see each thing in LEAP (the Analysis view for the tree and data,
Results for charts, Notes for documentation), so they can check and do it themselves next time.

## Rules while orienting

- Read only. Orientation changes nothing, saves nothing and does not calculate.
- Use the names the tools return, exactly. Do not translate, shorten or "correct" them.
- When a name or a number does not match what the user said, you have probably found the wrong
  branch or variable. Look further and ask; do not assume.
- Look things up in the help (`search_help`, `read_help_topic`) before explaining how a LEAP feature
  works, and give the user the topic's link.
- Keep what you learned. Later skills (building a scenario, writing expressions) assume you know the
  scenario tree, the years, the units and the demand structure of this area.
- Budget: about 15 to 25 calls is enough for an orientation. Three demand branches, one module and
  one process give the picture; stop there unless the user's question needs more.
- When `search_help` returns a link that is a file path rather than a web address, give the user
  the topic's title and address instead of the path.

## Example

User: "Can you tell me what's in this model?"

1. `leap_status` → ready, area "Freedonia", results up to date, access: edit anything.
2. `get_area` → base year 2020, first scenario year 2021, end year 2050; one region; scenarios
   Current Accounts → Baseline → Mitigation (calculated) and six single-measure scenarios
   (Efficient Lighting, Efficient Refrigerators, CNG Buses, Gas and Renewables, Efficient Industry,
   Biogas Digestion) not marked for calculation.
3. `get_notes` (area) → a training model of an imaginary country, built for the LEAP exercises.
4. `get_branches` depth 2 → Demand: Household, Industry, Transport, Commercial. Transformation:
   Transmission and Distribution, Electricity Generation, Charcoal Production, Oil Refining, Coal
   Mining. Also Key Assumptions, Resources, Non Energy.
5. `get_branch` on `Demand\Household\Urban\Electrified\Cooking` scenario Baseline → Activity
   Level in `% Share/Household` across fuels, Final Energy Intensity at each technology: activity
   analysis with shares. `Demand\Household` grows by its own `Growth(3%)`; the Households key
   assumption is not referenced.
6. `get_branch` on `Transformation\Electricity Generation` → eight processes, merit-order
   dispatch, 35% planning reserve margin, Optimize = No.
7. `get_values` Demand, Final Energy Demand, Baseline, 2021–2050; the root branch "Freedonia",
   `One_Hundred Year GWP Direct At Point of Emissions`, Baseline and Mitigation, unit Million
   Metric Tonnes.
8. Summary to the user in six to ten sentences, with the scenario tree drawn as an indented list.
