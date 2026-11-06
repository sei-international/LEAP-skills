---
name: leap-optimization
description: Set up, run and read least-cost optimization in a LEAP model through the LEAP MCP tools, using NEMO (the open-source Next Energy Modeling system for Optimization that LEAP calls). Use when the user says optimization, least cost, least-cost expansion, NEMO, optimize capacity expansion, optimized capacity, solver (HiGHS, Cbc, GLPK, Gurobi, CPLEX, MOSEK, Xpress), infeasible or unbounded, renewable target or renewable portfolio standard, emission cap or emission constraint, maximum capacity addition, storage or batteries, energy system optimization, limited foresight. Covers when optimization is the right tool, the two modes (one module, or the whole energy system), what must be installed, the data it needs, the constraints and how they cause infeasibility, storage, reading optimized results, and the routine when NEMO reports infeasible.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: leap_status, get_area, get_branch, get_branches, get_expression, get_values, set_expression, set_expressions, calculate, api_get, api_describe, show_in_leap, read_view, search_help, read_help_topic
  tested-on: "a large single-region model with an energy-system-optimization scenario, LEAP 2026.9.0.18, 2026-11-06 (read-only; nothing run)"
  status: draft for review
---

# Optimization in LEAP with NEMO

In an optimized scenario LEAP hands a Transformation module (or the whole energy system) to NEMO,
which chooses the capacity to build in each year and how to dispatch it in each time slice so
that the total net present value of system costs over the whole period is lowest, subject to the
constraints the user has set. LEAP writes NEMO's input files, runs it, and reads the results back
into the Results View, the Energy Balance and the cost reports; the user never touches NEMO.
The help section "Optimization" (Introduction to Optimization, Setting Up Optimization, Solvers
Supported by LEAP and NEMO, The Optimization Monitor) is the reference; `read_help_topic` before
explaining a setting. leap-transformation covers simulation dispatch and is assumed here.

## Is optimization the right tool?

| The user wants | Use |
|---|---|
| To state what is built and when | Exogenous Capacity (simulation) |
| LEAP to time additions of plants the user chooses, to hold a reserve margin | Endogenous Capacity, Addition Size and Order, Planning Reserve Margin (simulation) |
| The cheapest mix and timing, with policy limits such as a renewable share or an emission cap | Optimization |
| To see how robust a plan is to fuel prices or capital costs | Several optimized scenarios with different assumptions, compared |

Optimization costs more data (every cost of every candidate process) and more time (a solver
run per scenario). Simulation and optimization can live in different scenarios of one area, which
is the usual way to compare them. Say this before proposing to switch a model to optimization.
Storage processes and the Renewable Target act only in optimized scenarios.

## The two modes

- **Partial optimization**: the `Optimize` variable at ONE Transformation module, set to `Yes` in a
  scenario. Every other module is simulated as before. Setting `Optimize` to Yes at more than one
  module makes the calculation stop with an error.
- **Full energy system optimization**: the `Energy System Optimization` variable at the top-level
  (area) branch, set to `Yes` in a scenario. Every Transformation module is optimized together,
  constraint variables appear at Resources branches too (reserves, minimum and maximum production,
  imports and exports), useful-energy demand branches gain `Optimize Devices`, and in a
  multi-region area transmission lines can be modeled (Settings: Optimization).
- They cannot be combined in one scenario: with Energy System Optimization = Yes the module-level
  `Optimize` variable disappears and anything in it is ignored, and so do the module's Dispatch
  Rule, Merit Order, Process Share and Endogenous Capacity and the output fuel's Shortfall and
  Surplus rules. Different scenarios may use different modes.
- Both variables exist only in scenarios, never in Current Accounts. Both take the `Yes` function
  with options: `Yes` (fastest installed solver, perfect foresight), `Yes(HiGHS)`, `Yes(2030, 2040)`
  (limited foresight: years grouped up to 2030, 2031–2040, after 2040, each group solved in turn),
  `Yes(Gurobi, presolve, HSD, extra NEMO parameters, years...)`. The `NEMO(...)` function is the
  deprecated older form. Prefer plain `Yes`: a model that names a solver is less portable, and a
  named commercial solver that is missing is replaced by the best installed one, HiGHS last.
- If `get_branch` on a module shows no `Optimize` variable in a scenario, either Energy System
  Optimization is on in that scenario, or NEMO is not installed (the variables are hidden then).

## What must be installed, and the traps

- NEMO (free, from the LEAP web site), which brings Julia and the free solvers GLPK, Cbc and
  HiGHS. Gurobi and MOSEK ship with NEMO but need a purchased license file; CPLEX and Xpress are
  installed separately. Help: About in LEAP lists what was found. HiGHS is the sensible default.
- NEMO does not run in a LEAP that another program started (a script, COM automation, a test
  harness): such a LEAP reports "Julia plugin for ... not found" and optimizes nothing. Ask the
  user whether they started LEAP themselves before relying on an optimized result.
- After a LEAP update that changes the dictionary, the first start must be the LEAP window
  itself; an automated first start leaves NEMO switched off until a normal start happens.
- LEAP's check for Julia packages needs a folder it can write to under the NEMO install
  (`C:\ProgramData\NEMO\depot`). On a locked-down PC the check can report every package missing
  while NEMO itself would load. LEAP 2026.9 retries with a temporary folder and writes Julia's
  errors to LEAP.log; "Reset NEMO" on Settings: Optimization re-scans the packages.
- Costs must be in scope: `api_get` `AreaSetting("ShowCosts")` true, `AreaSetting("DiscountRate")`
  positive, and the annualization method Capital Recovery Factor (the help asks for it). The
  other settings are `ShowEmissionConstraints`, `InsufficientCapacityHandling`,
  `KeepIntermediateResults`, `OptimizationMonitorMode`. `AnnualizationMethod` and
  `InsufficientCapacityHandling` come back from `api_get` as bare numbers with no mapping to
  their choices (unverified which number is which): ask the user to read the choice on Settings:
  Costing and Settings: Optimization. `api_describe` does not list setting names; `api_call`
  `AreaSettingNames()` does. Ask before changing an area setting.

**Finding the data.** Processes: `get_branches` with `parent` the module's Processes branch and
`depth` 1, then `get_branch` per process. Never `depth` 0 at a module: it returns hundreds of
effect branches. The Effects and Load Shapes top-level branches are read like any other:
`get_branch` by name, or `get_branches` with one as `parent`; `find_branches` with a pollutant
or shape name also finds the emission constraint and the System Load Shape branches.

## The data optimization needs

Read every candidate process with `get_branch` in the optimized scenario; the list differs from a
simulated scenario. Required (per process unless noted):

| Variable | Why |
|---|---|
| Capital Cost, Fixed O&M Cost, Variable O&M Cost | The objective. A process with no capital cost is free to build and will swamp the result. |
| Fuel costs (feedstock fuel cost at the process, or resource costs at Resources) | Running cost per unit of output. |
| Lifetime, Interest Rate (or the area Discount Rate) | Annualization of capital. |
| Process Efficiency (or Heat Rate, Losses) | Fuel per unit of output. |
| Maximum Availability (time-sliced) | Capacity factor ceiling per slice. |
| Exogenous Capacity | Existing and committed plants; the optimizer adds on top of it. |
| Maximum Capacity, Maximum Capacity Addition | Realistic limits; without them the solver builds any amount of the cheapest process in one year. Default is Unlimited. |
| System Load Shape of the output fuel; time slices | Dispatch by slice. A flat shape removes the need for peaking plant. |
| Emission factors and externality values (if emissions matter) | Needed for an emission constraint or a pollutant price. |

Ignored in an optimized module (hidden in LEAP): Dispatch Rule, Merit Order, Process Share,
Endogenous Capacity and its Addition Size and Order, Planning Reserve Margin for additions,
Shortfall and Surplus Rules on the output fuel (surplus is treated as waste under optimization).
Do not try to set them. Historical Production still rules years before the First Simulation Year
(unverified: whether NEMO respects it exactly).

Zero-cost traps (from support cases): a supply chain with no cost anywhere (free renewable, free
import, free transmission) gives the solver many equally cheap answers; results then change from
one calculation to the next and imports can exceed demand. A token variable O&M cost (for example
$1/MWh on solar) makes the answer unique. An import cost equal to the production cost has the same
effect: the solver is indifferent and flips between the two. An existing process with Capital
Cost 0 ("none built") and Maximum Capacity Unlimited can be expanded for free: set its Maximum
Capacity to the existing fleet. LEAP 2026 writes a Diagnostics note listing zero-cost elements
under full energy system optimization.

**Is a cap deciding the answer?** Compare `Capacity Added` with `Maximum Capacity Addition` year
by year. Equality in every year means the cap, not cost, is choosing the expansion; a placeholder
cap on wind and solar with no cap on gas or coal gives a result that says nothing about costs. Say
so, and ask the user for defensible figures.

## Constraints, and how each makes a problem infeasible

| Variable (where) | Meaning | Infeasible when |
|---|---|---|
| Maximum Capacity (process) | Cap on total capacity in a year | Caps across all processes cannot cover peak load |
| Maximum Capacity Addition (process) | Cap on capacity built in one year | Demand grows faster than the sum of allowed additions |
| Minimum Capacity, Minimum Capacity Addition (process) | Floors | Conflict with a Maximum of the same process |
| Minimum Production, Maximum Production (process) | Floor and cap on annual output | Floors sum above requirements; caps sum below them |
| Minimum Share of Production, Maximum Share of Production (process) | Floor and cap as a percent of the module's output of the fuel | Minimum shares sum above 100; a minimum above its own maximum |
| Minimum Utilization (process, time-sliced) | Fraction of available capacity that must run in each slice | Must-run output exceeds load in low-load slices with nowhere to go |
| Renewable Target (module) with Renewable Qualified (process, 0–100%) | Minimum percent of the fuel from qualified processes | Qualified processes are capped below the target; nothing is marked Renewable Qualified |
| Annual Emission Constraint (Effects branch; needs Settings: Optimization, Emissions Constraints) | Cap on a pollutant for the whole system, in each year | Emissions from parts the optimizer does not control (demand, simulated modules) already exceed the cap |
| Resource constraints (Resources, full ESO only) | Reserves, production, import and export limits | Fuel needed cannot be produced or imported |

`Unlimited` is the expression for "no constraint". A constraint that looks generous can still bind
through its interaction with the others; the help's FAQ says so and it is the usual case.

## Storage processes

A process marked as storage in its Process Properties (battery icon) is optimized only; a
simulated module ignores it. `get_branch` on a battery process showed Full Load Hours (hours at
full output from a full charge) and Minimum Charge (marked "under development" in the help) as
its extra variables. The help also describes Starting Charge (percent of full at the start of the
base year) and Daily, Seasonal and Annual Storage Carryover (daily on by default; the seasonal
and annual ones appear only when the time slices have that detail); where they are set in this
LEAP version is unverified (Process Properties screen, most likely). Storage needs time slices with within-day structure to do anything useful (unverified
beyond what the carryover topic implies).

## Reading optimized results

- `Optimized New Capacity` at each process is the variable LEAP writes during the calculation.
  The help says its text carries a tag such as `(NEMO/HiGHS)` naming the solver used; in a test
  on a calculated area `get_expression` showed `0`, inherited, so do not rely on it (unverified
  when it is filled). The Optimization Monitor tab in LEAP names the solver; `Capacity Added` is
  the result to read.
- `get_values` at the process, scenario named: `Capacity`, `Capacity Added`, `Energy Generation`,
  `Actual Availability`; at the module: `Requirements`, `Outputs by Output Fuel`, `Imports`,
  `Module Balance`. Result names are the same as in a simulated scenario; `get_branch` lists them.
  To chart generation with `show_in_leap`, `Energy Generation` is time-sliced and needs time
  slices on the X axis; for generation by year chart `Outputs by Output Fuel` at the module.
- Costs: the cost result categories (capital, fixed and variable O&M, fuel, externalities) at the
  process and module, and the Summaries view (cost-benefit against a baseline) through
  `show_in_leap` and `read_view`. The objective NEMO minimized is the discounted total of those
  costs; the solver's last lines in the Optimization Monitor report the objective value
  (unverified: whether LEAP exposes it as a result variable).
- The Optimization Monitor tab in the Results View keeps the solver log per scenario; `read_view`
  on it is unverified. Ask the user to open it when a log is needed, or to right-click a pane,
  Copy All Text, and paste it.
- Under limited foresight each group of years is solved on its own; a plant that would be
  built early under perfect foresight may appear later or not at all.

## When NEMO reports infeasible or unbounded

Infeasible: no solution meets every constraint. Unbounded: the constraints leave the cost free to
fall without limit (usually a missing cost or a negative one). Either is a problem in the model's
data, not in LEAP or NEMO. The routine, from the FAQ:

1. Read the message LEAP gave, and ask the user for the last lines of the Optimization Monitor
   pane (OPTIMAL, INFEASIBLE, UNBOUNDED, or no status at all, which means the run was interrupted,
   most often by the solver time limit on Settings: Optimization or by a problem starting Julia).
2. If the model solved before a change, revert to the last version that solved (Area: Revert to
   Version in LEAP; `get_changes` lists recent edits) and reintroduce the changes one at a time.
3. Otherwise loosen constraints until it solves, then tighten one by one. Order: Maximum Capacity
   Addition, Maximum Capacity, Minimum Utilization, Minimum and Maximum Production and Shares,
   Renewable Target, Emission Constraint, resource limits. Set each to `Unlimited` (or 0 for a
   floor) with `set_expression` in the scenario, calculate, read.
4. If the solver cannot build enough capacity to meet demand, suggest
   `InsufficientCapacityHandling` = "Carry On and Write a Warning to Diagnostics": the calculation
   then completes and the Diagnostics tab names the year and module of the shortfall. The third
   choice, "Stop and Report an Error in NEMO", gives the solver's own, more detailed, report.
5. A solver error rather than an infeasible status: run the scenario with `Yes(HiGHS)`. The CPLEX
   Community Edition is size-limited, Gurobi needs a supported version, MOSEK needs a license.
6. NEMO's own infeasibility finder and its SQLite files (kept when Keep Intermediate Results is
   on) are for the user with NEMO experience; point to the NEMO documentation.

## Calculating and runtime

- `leap_status` first: ready, area open, access. `calculate` starts the run; it returns when the
  calculation ends or reports that it is running, and `leap_status` is polled until
  `resultsUpToDate` is true. Do not start a second calculation.
- A solve can take seconds to hours. The solver time limit (default 60 minutes per run) stops a
  run and counts it as a failed scenario. Custom calculation years (Settings: Years) make
  optimization much faster, since the solver works only on calculated years.
- NEMO's own progress lines ("Started modeling scenario") reach the log only when NEMO exits, so
  during a long solve the Monitor shows solver output alone; this is normal, not a hang.
- Each optimized scenario is solved separately; parallel calculation runs them side by side.
- A scenario optimized on another PC may have used another solver; the result tag says which.

## Common mistakes

- Setting `Optimize` = Yes in Current Accounts (not available) or at two modules (error).
- Turning on optimization with no capital costs: the solver builds the free process without limit.
- No Maximum Capacity Addition on any process: all new capacity arrives in one year.
- Expecting the Renewable Target to act without marking processes Renewable Qualified, or in a
  simulated scenario.
- An Emission Constraint set at the level of the power sector alone, while the cap applies to
  the whole system's emissions; the uncontrollable part makes it infeasible.
- Reading Endogenous Capacity or the Dispatch Rule in an optimized scenario; they are not used.
- A fuel below an optimized useful-energy demand on a fixed System Load Shape instead of
  `ShapeFromDemand`: the two profiles contradict and the solver over-produces.
- Naming a solver that is not installed when portability matters; plain `Yes` is better.
- Trusting an optimized result from a LEAP that a script started.

## Example (illustrative, not yet run)

User: "Find the least-cost expansion of Freedonia's power sector with at least 40% renewable
generation by 2040."

1. `leap_status` → ready, area "Freedonia", access: edit anything. `get_area` → 2020–2050,
   scenarios Current Accounts → Baseline → Mitigation. `get_branch`
   `Transformation\Electricity Generation` scenario Baseline → `Optimize` = No, eight processes,
   merit-order dispatch. If `Optimize` is absent, stop: NEMO is not installed, say so.
2. `api_get` `AreaSetting("ShowCosts")`, `AreaSetting("DiscountRate")` → costs in scope, 5%;
   ask the user to confirm Capital Recovery Factor on Settings: Costing.
3. `add_scenario` "Least Cost RPS" based on Baseline (leap-build-scenario). `set_expression`
   `Optimize` = `Yes` at the module in the new scenario.
4. `get_branch` on each process in the new scenario: the constraint variables now appear. Check
   with `get_expression` that each has Capital Cost, Fixed and Variable O&M Cost, Lifetime,
   Process Efficiency, Maximum Availability and Exogenous Capacity; note any that are zero or
   missing and report them before calculating. Expect Freedonia's training data to have costs on
   its processes (unverified for every process).
5. `set_expressions`: `Maximum Capacity Addition` on each candidate (for example 500 MW a year),
   `Renewable Qualified` = 100 at Hydro, Wind and Solar PV, and at the module
   `Renewable Target` = `Interp(2025, 0, 2040, 40, 2050, 40)`.
6. `calculate`; poll `leap_status`. On INFEASIBLE, follow the routine above (first suspect: the
   addition cap on the renewable processes against the 2040 target).
7. `get_values` `Capacity` and `Energy Generation` at each process, scenarios Baseline and
   Least Cost RPS, 2030, 2040, 2050, unit MW and GWh; `get_expression` `Optimized Capacity` for
   the solver tag; the cost-benefit summary through `show_in_leap` Summaries and `read_view`.
8. Report what was built and when, the renewable share reached, the cost difference against
   Baseline, and the solver used; note that the plan depends on the cost assumptions and suggest
   a second optimized scenario with different fuel prices.
