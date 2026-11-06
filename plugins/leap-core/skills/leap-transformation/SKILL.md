---
name: leap-transformation
description: Understand or change the Transformation (supply) part of a LEAP model through the LEAP MCP tools: electricity generation, transmission and distribution, refining, charcoal making and other modules. Use when the user asks why a plant does or does not generate, how to add capacity, what a dispatch rule does, how imports and shortfalls arise, how the reserve margin works, or what optimization changes. Covers modules and their order, processes, feedstock and output fuels, efficiency, capacity (exogenous, endogenous, optimized), dispatch rules, load shapes and the checks that find the usual problems.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: get_branches, get_branch, get_expression, get_values, set_expression, set_expressions, show_in_leap, read_view, api_get, search_help, read_help_topic
  tested-on: Freedonia (sample area)
  status: draft for review
---

# Transformation in LEAP

Transformation converts and delivers energy. It is driven by Demand: each module receives
requirements for its output fuels, dispatches its processes to meet them, and creates requirements
for its feedstock fuels, which the next module down must meet. The help section "Transformation"
is the reference; read the topic of any variable before explaining it.

## Structure

- **Modules** sit under Transformation in calculation order, from closest to demand (Transmission
  and Distribution) to closest to resources (Oil Production, Coal Mining). Order matters: a module
  can only see requirements created above it. `get_branches` with `parent` Transformation,
  `depth` 1, gives the order.
- Each module has an **Output Fuels** branch and a **Processes** branch. A process has one or more
  **feedstock fuels** (converted, counted in efficiency) and optional **auxiliary fuels** (own use).
- Module properties, set by the user in LEAP, decide which variables exist: whether capacities and
  costs are entered, how efficiency is expressed (efficiency, heat rate or losses), whether the
  module is simulated or optimized. `get_branch` on a process shows what is there; do not assume.
  Its answer also names the process's `feedstockFuels` and `auxiliaryFuels` (and `fuel` for a
  technology or fuel branch), and `variablesFor` says which scenario the variable list belongs
  to: the one you named, or else the one selected in LEAP. Name a simulated scenario to see
  Dispatch Rule, Merit Order and Historical Production even while an optimization scenario is on
  the user's screen.

## The variables that matter most

| At | Variable | Meaning |
|---|---|---|
| Process | Exogenous Capacity | The total capacity in place in each year, as the user plans it (not additions): `Step(2028, 300)` means 300 MW from 2028 on. Retirements are a lower total. |
| Process | Endogenous Capacity | The size of each block LEAP may add on its own to keep the reserve margin (500 means 500 MW blocks; 0 means never). The order in which candidate processes are tried goes with it; `get_branch` shows what this area has. |
| Process | Maximum Availability | Percent of the year the capacity can run. |
| Process | Capacity Credit (Capacity Value) | Share of capacity that counts toward the reserve margin. |
| Process | Process Efficiency (or Heat Rate, or Losses) | Output over feedstock energy. |
| Process | Dispatch Rule | How the process is run from the First Simulation Year: PercentShare, ProportionalToCapacity, FullCapacity, MeritOrderDispatch, RunningCost. |
| Process | Merit Order, Process Share, Historical Production | Inputs to the dispatch rules; Historical Production rules before the First Simulation Year. |
| Process | Lifetime, Capital Cost, Fixed and Variable O&M Cost | Needed for cost results and optimization. |
| Module | Planning Reserve Margin | Percent above peak load that capacity must reach; triggers endogenous additions. |
| Module | First Simulation Year | Year from which dispatch rules replace Historical Production. |
| Module | Optimize | Yes switches the module to NEMO optimization in that scenario. |
| Output fuel | Shortfall Rule, Surplus Rule, Import Target | What happens when processes cannot meet requirements, or produce too much. Read them with `get_branch` on the module's Output Fuels branch (for example `Transformation\Electricity Generation\Output Fuels`, by name or by the child ID listed at the module) and then on the fuel branch under it, with `scenario` for the expressions, or `get_expression` there. In LEAP before 2026.9.0.19 that read was refused with "not visible at region" while the Results view was on screen; `api_get` `Branches("...\Output Fuels\Electricity").Variables("Shortfall Rule").Expression` is the fallback. |
| Output fuel | Output Shares | How a multi-fuel module splits its output. |
| Fuel (system) | System Load Shape | The load curve used for peak and dispatch. Belongs to the fuel, not to demand branches. |

## Reading what a module did

Use result variables with `get_values` at the module or process, scenario named, unit named.
Take the exact names from `get_branch` at that branch; the ones below are as Freedonia lists them:

- `Requirements` at the module: what it was asked to produce. If zero, nothing upstream needs the
  fuel, and nothing will be generated. `Peak Power Requirements` for the peak.
- `Energy Generation` (and `Power Generation`) at the module and each process; `Outputs by Output
  Fuel` and `Outputs by Feedstock Fuel` for the split by fuel. `Energy Generation` and `Power
  Generation` are time-sliced results: `get_values` reads them by year or by slice (`filter`
  `Time Slice=<name>`), but `show_in_leap` needs time slices on the X axis (`Time Slices`, `Years
  & Time Slices`, `Scenarios & Time Slices` or `Regions & Time Slices`); with Years alone it
  refuses and points to `Outputs by Output Fuel` for yearly generation.
- `Capacity`, `Capacity Added`, `Actual Availability` at processes. `Actual Availability`,
  `Maximum Availability` and other percent-type results come back from `get_values` without a
  `unit`, as percentages with unit `Percent`. `Maximum Availability` is both a data variable
  and a result of the same name: `get_values` and `show_in_leap` take the result in the Results
  view and the data variable elsewhere.
- `Imports` and `Exports` at the module: gap filling and surplus.
- `Inputs` (feedstock use) at processes, by fuel with `filter` such as `Fuel=Coal Bituminous`.
- `Module Energy Balance` for the whole picture in one table; `show_in_leap` with view Energy
  Balance and `read_view` for the system-wide picture in a year.
- Emissions of the module: `One_Hundred Year GWP Direct At Point of Emissions` at the module
  branch, unit `Million Metric Tonnes`.
- The module's reserve margin: `get_values` `Reserve Margin` (and `Planning Reserve Margin`,
  `Load Factor`) at the module, no `unit`; the answer is a percentage with unit `Percent`. To
  explain it, `Capacity` ÷ `Peak Power Requirements` gives the margin before capacity credits.
- To put one process on screen with `show_in_leap`: for a result that is not stacked (`Actual
  Availability`, `Capacity Factor` and the like) name the process as `branch`; it is shown alone
  and the answer's `branchShown` confirms it. For a stacked result (`Capacity`, `Outputs`,
  `Energy Generation`) the tool refuses a single process: put Branches on the `legend` or
  `x_axis` and `select` `Branches=<process name>` instead.

## Why a plant does not generate (the FAQ checklist)

1. Requirements on the module are zero or met before this process is reached: read
   `Requirements`, then `Outputs` of the other processes, imports and the shortfall rule.
2. Before the First Simulation Year (including the base year of every scenario), output follows
   Historical Production; after it, the dispatch rule. A visible jump at the first scenario year
   is the rule taking over, not a data error. A plant that runs in the base year and stops later
   is one the rule does not call on: under MeritOrderDispatch it is behind plants that already
   cover the load; under PercentShare its share is zero; under ProportionalToCapacity its capacity
   or availability is zero.
2a. Output flat while demand grows: fixed capacity in a shared merit order. Plants with the same
   Merit Order number form one group, and LEAP splits the group's output among them in
   proportion to Capacity × Maximum Availability. A hydro or wind plant in the same group as
   thermal plants that keep being added gets a shrinking slice and runs below its availability.
   To make a plant run first, give it a lower Merit Order number than the others.
3. Capacity: Exogenous Capacity retired, or never entered in this scenario or region; Maximum
   Availability zero.
4. The feedstock fuel is not available: a module further down produces none and its shortfall rule
   leaves requirements unmet.
5. A storage process is ignored unless the module is optimized.

Report what you found with the variable names, and point the user to the Diagnostics tab in LEAP,
which lists module-order and unproduced-fuel problems after a calculation.

## Adding or changing capacity

- Planned plants: `Exogenous Capacity` at the process, in the scenario, as `Step` or `Interp` in
  the unit shown (MW is usual for electricity). It is the total capacity in each year, so adding
  300 MW to a plant that has 100 means `Step(2028, 400)`. Read the existing series first. The
  help topic "Specifying Capacity Data" explains the choices. A new scenario needs a name and an
  abbreviation of up to 8 characters (`add_scenario`; see leap-build-scenario).
- A new kind of plant: a new process branch (structural change, "edit anything" access; see
  leap-demand-modeling for the AddBranch route), then feedstock fuel, efficiency, availability,
  capacity, dispatch rule and costs, in Current Accounts first.
- Let LEAP decide timing: endogenous capacity with Addition Size and Addition Order at the
  candidate processes and a Planning Reserve Margin at the module. LEAP adds the next unit in the
  year the margin would otherwise fall below the target.
- Least-cost choice: optimization (`Optimize` = Yes at one module in a scenario, or full energy
  system optimization in Settings). It needs complete cost data and NEMO installed. NEMO does not
  run in a LEAP started by another program; check with the user that their LEAP can optimize.

## Dispatch and load shapes

- MeritOrderDispatch and RunningCost dispatch on time slices against the System Load Shape of the
  output fuel: merit group 1 fills the bottom of the load curve up to its combined available
  capacity, group 2 the next band, and so on; within a group, output is shared in proportion to
  available capacity. PercentShare and ProportionalToCapacity dispatch on annual energy only.
- Load shapes belong to fuels (System Load Shape) or are built from demand-side shapes. The
  `ShapeFromDemand` value is for the System Load Shape of a fuel only, never for a demand branch.
- Peak load, load factor and reserve margin come from the shape; a flat shape makes peaking plants
  unnecessary.

## Checks

- Module order: Transmission and Distribution above Electricity Generation above fuel production.
- Every demand fuel is produced by some module or has an import rule; every module output has a
  requirement.
- Efficiency greater than zero and in the form the module expects (33% is typical for steam
  plants; losses are percent lost, not kept).
- Capacity units and scale (MW versus GW, cumulative versus additions).
- Shares used by PercentShare sum to 100 across processes.

## Common mistakes

- Reading `Outputs` when the question is what the module was asked for (`Requirements`), or the
  reverse.
- Entering capacity in a scenario where the module has capacities switched off, so the variable
  does not exist.
- Changing Historical Production to change future generation; it stops mattering at the First
  Simulation Year.
- Putting a load shape on a demand branch to change dispatch.
- Expecting a storage process or a renewable target to act in a simulated (non-optimized) module.
- Assuming a shortfall means total supply fails; another module or imports may be covering it.

## Example

User: "Add 500 MW of solar PV in 2030 and another 500 in 2035 and tell me how coal generation
changes."

1. `get_branches` parent Transformation depth 1 → module order; `get_branch`
   `Transformation\Electricity Generation\Processes\Solar PV` scenario "Baseline" → variables
   include Exogenous Capacity (MW), Maximum Availability, Dispatch Rule MeritOrderDispatch.
2. `get_expression` Exogenous Capacity → `100` (total MW, inherited). New scenario (see
   leap-build-scenario), `set_expression` `Step(2030, 600, 2035, 1100)` (totals).
3. `calculate`; `get_values` `Energy Generation` at Coal Steam and at Solar PV, both scenarios,
   2030 to 2040, unit GWh; `Capacity Added` at the candidate processes; `Reserve Margin` at the
   module (unit `Percent`); the module's `One_Hundred Year GWP Direct At Point of Emissions` in
   Million Metric Tonnes. To show generation in LEAP, `show_in_leap` `Outputs by Output Fuel`
   with `x_axis` Years, or `Energy Generation` with `x_axis` `Years & Time Slices`.
4. Report the change in coal generation, whether endogenous additions fell as a result, and, if
   solar shares a merit order with thermal plants, that it is dispatched proportionally and so runs
   below its availability unless given a lower Merit Order number.
