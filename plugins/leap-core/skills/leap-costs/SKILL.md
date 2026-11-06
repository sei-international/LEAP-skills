---
name: leap-costs
description: Cost and cost-benefit analysis in LEAP through the LEAP MCP tools. Use when the user asks what a policy or scenario costs, for a cost-benefit comparison, net present value (NPV), the discount rate, abatement cost or a marginal abatement cost curve (MACC), investment costs, levelized cost, social costs by category, or "how much does this policy cost". Covers which cost data exist and where, the settings that switch costing on (costing boundary, discount rate, monetary year), how to read cost results with get_values and the Cost-Benefit, MACCs and Affordability views, the usual order of work, and the checks that catch double counting and mismatched currencies.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: leap_status, get_area, get_branch, get_branches, find_branches, get_expression, get_values, set_expression, set_expressions, show_in_leap, read_view, api_get, api_call, search_help, read_help_topic
  tested-on: Freedonia sample area, LEAP 2026.9
  status: draft for review
---

# Costs and cost-benefit analysis in LEAP

LEAP does social cost-benefit analysis: it adds up the costs of every part of the energy system in
each scenario and compares scenarios. These are costs to society (resource costs), not prices paid
by consumers or the finances of a company. LEAP's help says it plainly: cost-benefit analysis in
LEAP is not a test of financial viability. Keep that distinction in every answer.

Cost results exist only when costing is switched on in the area, the costs have been entered, and
the scenarios have been calculated. Costs are calculated for every year, so costing is unavailable
when the area calculates only some years.

## Step 0: Is costing on, and are the results valid?

1. `leap_status` → `resultsUpToDate`, and what you may change.
2. `api_get` with `AreaSetting("ShowCosts")` → whether costing is on (the Costs box on the Scope
   tab of General: Settings). Off means no cost variables and no cost results. Switching it on is
   a settings change: ask the user, and expect a recalculation.
3. `api_get` with `AreaSetting("DiscountRate")` → the discount rate in percent.
4. `get_area` → base year, end year, scenarios. The monetary year (the year the currency is in
   and the year costs are discounted to) is on the Years tab of Settings; it is normally the base
   year. Read it, with the discount rate and the currency, from the header line of the
   Cost-Benefit table (`show_in_leap` with `view` "Cost-Benefit", then `read_view`), which reads
   for example "Discounted at 5.0% to year 2020". There is no `AreaSetting("MonetaryYear")`.
5. Costing boundary, externality costs on or off, the capital cost annualization method and the
   last year to count costs are area settings too, but `AreaSetting("CostingBoundary")` and
   `AreaSetting("ShowExternalityCosts")` do not exist, and `api_describe` does not list setting
   names. The user reads them in LEAP (Settings: Costs), unless the user allows `api_call`
   `AreaSettingNames()`, which returns the real names to use with `api_get`.

## Which cost data exist, and where

All are ordinary variables: find them with `get_branch` (which lists the variables a branch has)
and read them with `get_expression` or `get_values`. Names below are LEAP's; confirm them at the
branch, since cost variables appear only when costing is on and, in Transformation, only in
modules whose Cost box is checked in Module Properties.

| Where | Variable | What it is |
|---|---|---|
| Demand branch, usually a technology | Demand Cost | Non-fuel cost by one of four methods: cost per activity (default), cost per device sold (stock and transport branches), total cost, or Cost of Saved Energy (CSE). CSE is a cost per unit of energy saved against a counterfactual scenario; it is zero in the base year by definition. In Freedonia the demand costs are entered per unit of activity as `AnnualizedCost(capital, lifetime)`, for example `AnnualizedCost(100, 10)`. |
| Optimized demand technology only | Capital Cost, Fixed OM Cost, Variable OM Cost, Interest Rate, Lifetime | Used by energy system optimization; Variable OM Cost must not include fuel, which the optimizer adds itself. A device is costed either by Demand Cost or by these, never both. |
| Transformation process | Capital Cost | Total (overnight) cost per unit of capacity, not annualized. LEAP annualizes it over Lifetime at the process Interest Rate using the method set on the Costs tab (capital recovery factor by default; required for optimization). Endogenous capacity is replaced after each lifetime and incurs the cost again; exogenous capacity is not. |
| Transformation process | Fixed OM Cost, Variable OM Cost | Fixed per unit of capacity; variable per unit of output, input or losses. A module without capacity data has only variable O&M. |
| Transformation process | Salvage Value | Net value at the end of life, same unit as capital cost; negative for decommissioning. Enters the capital cost stream. |
| Transformation process | Legacy Capital Payments (formerly Stranded Costs) | Remaining payments on existing plant. Counted in the Module Cost Balance, not in social costs: a sunk cost and a transfer payment, by design. |
| Transformation module | Module Costs | Costs for a whole module that are not per process, capacity or energy. |
| Transformation feedstock and auxiliary fuel branch | Fuel Cost | Used for module cost balance, costs of production and optimization dispatch. Not used directly in social costs; defaults to the resource's production cost. |
| Resources branch for each fuel | Production Cost, Import Cost, Export Benefit, Cost of Unmet Requirements | The fuel side of social costs. Imports at CIF, exports at FOB. Unmet requirements is the damage from unserved demand (blackouts); zero means not quantified. With a restricted boundary the production cost is read as the delivered cost of the fuel. |
| Effects (General: Effects screen) | Externality Cost | Damage cost per unit of a pollutant, times emissions in each year. Counted only when Environmental Externality Costs is checked on the Costs tab. Not applied to extraction emissions, which is deliberate. |
| Affordability branches (optional) | Fuel Price, Customer Costs, Ann Income | A separate consumer-price view, not part of social costs. |

For a comparison of scenarios you only need costs where scenarios differ physically. The help says
so for demand, Transformation and resources alike.

## The costing boundary, and why it stops double counting

Every fuel is paid for once, at the point where it crosses the costing boundary. With the default
full-system boundary, fuel costs are the production cost of indigenous resources, the import cost
of imported fuels and the export benefit of exported fuels. The cost of electricity or refined
products made inside the area is NOT counted, because the fuels that made them already were. This
is why a saved kWh is valued through the fuel, capital and O&M it avoids, never through an
electricity price.

A restricted boundary names a Transformation module. Capital and O&M of modules upstream of it
are ignored; fuels delivered to it are costed at the delivered cost entered on the resource
branch (the help calls these Delivered Costs); imports and exports count only downstream of the
boundary. Use it when the model has delivered fuel prices but no refinery or mining costs. Under
this boundary the reported import cost can be less than import cost times total imports, because
some imports fall outside the boundary; say so when a user notices.

All cost calculations run in real (constant) currency of the monetary year. Discounting is only a
way of displaying results.

## Cost results

Read with `get_values` (variable names from `get_branch`, never from memory) or through the
Cost-Benefit, MACCs and Affordability views. The help topics are in Results Categories;
`search_help` "Social Costs"; the view's topic is "Cost-Benefit Report".

- **Social Costs** (result type Costs): the cost-benefit total, split by cost category: demand
  costs (device costs and costs of saved energy), Transformation capital, module and fixed and
  variable O&M, fuel costs at the boundary (production, import, export), externalities, unmet
  requirements. `get_values` at the root branch (the area's name) gives the annual total for the
  whole system. One category at a time: `filter` `Cost Category=<name>`, for example
  `Cost Category=Capital` at the root. The names are Demand Activity, Demand Cost of Saved
  Energy, Demand Other, Demand Vehicles, Demand Other Stocks, Capital, Fixed O&M, Variable O&M,
  Transformation Module, Fuel Production, Fuel Imports, Fuel Exports, Fuel Secondary Production,
  Unmet Fuel Requirements, Environmental Externalities and Non Energy Sector; an unknown name is
  refused with the list. For the split by sector, `get_values` Social Costs at the Demand branch,
  a Transformation module or the Resources branch; for the whole table at once (every category,
  discounted, against the reference) read the Cost-Benefit view with `read_view`.
- `get_values` Social Costs returns real (undiscounted) annual values in the currency named in
  the `unit` field. The Cost-Benefit view gives cumulative discounted values against the
  reference scenario, the greenhouse gases avoided and the cost per tonne avoided, all in one
  table. Never compare a discounted number with an undiscounted one.
- **Investment Costs**: total non-annualized capital spending in each Transformation process and
  year (capacity added times unit capital cost); exogenous and endogenous parts; real, nominal or
  discounted.
- **Module Cost Balance**, **Costs of Production**, **Sales Revenue** (result type Costs): the
  producer's view of one module, using Fuel Cost, and including legacy capital payments. Not the
  social cost.
- **Levelized Cost of Energy Production** (result type Transformation): cost per unit of energy
  produced at a module, including capital, O&M, fuel and optionally externalities. Named by the
  help; its variable name in `get_branch` is unverified.
- **Cost-Benefit table** (help topic "Cost-Benefit Report"): `show_in_leap` with `view`
  "Cost-Benefit", then `read_view`. Its header line carries the discount rate, the year costs are
  discounted to (the monetary year) and the currency, for example "Discounted at 5.0% to year
  2020". It shows, for each calculated and up-to-date scenario against a chosen reference
  scenario, the cumulative costs over all study years discounted to the monetary year at the
  discount rate, by demand sector, Transformation module and resource (production, imports,
  exports), optionally externalities, plus rows "Unmet Requirements", "Other Costs" and "Non
  Energy Sector Costs", the system total, the benefit/cost ratio, cumulative greenhouse gases
  avoided in CO2 equivalent and the cost per tonne avoided (with and without co-benefits from
  other pollutants). Costs relative to the reference are positive; benefits are negative. The Net
  Present Value (NPV) of a scenario is the sum of all discounted costs and benefits in that
  scenario minus the reference, summed over all years. The discount rate can be changed on this
  screen for a what-if, which does not change the area setting. Which `select` options
  `show_in_leap` accepts for the reference scenario and discount rate is unverified.
- **MACC reports** (`view` "MACCs"): one bar per scenario marked Include in MACC Report in Manage
  Scenarios, against a counterfactual scenario; cumulative abatement on the x axis, cost per tonne
  on the y axis. Calculated either by the partial approach (one pass, each scenario against the
  baseline, interactions ignored) or the retrospective approach (repeated passes, cheapest first).
  MACC results do not refresh with the rest of the results: they need the Refresh MACC button in
  LEAP. Do not include a package scenario together with the scenarios it inherits from; LEAP stops
  with an error. Whether `show_in_leap` can trigger the refresh is unverified; tell the user when
  a MACC may be stale.
- **Affordability reports** (`view` "Affordability") and the Consumer Energy Cost results: fuel
  bills and device costs per customer against income, only at branches marked as affordability
  branches. A "Decomposition" view also exists.

## The usual order of work for "what does this policy cost?"

1. Agree what "cost" means: the social cost difference against a baseline over the study period
   (LEAP's answer), or something narrower such as investment in power plants or consumer bills.
2. `leap_status`, then Step 0 above: costing on, discount rate, monetary year, boundary.
3. `get_area` for the scenarios. Pick the policy scenario and its baseline; they should share the
   same population and GDP assumptions, or the comparison is not about the policy.
4. Find where the two scenarios differ physically (the expressions the policy scenario has of
   its own, with `get_expression`), and check with `get_branch` and
   `get_expression` that every branch that differs carries a cost: a Demand Cost at changed
   demand technologies, Capital Cost and O&M at added processes, production, import and export
   costs at the fuels whose flows change. Missing unit costs are the usual reason a scenario
   differs physically but shows no cost difference. `get_branches` on Demand with `depth` 0
   returns every effect branch; use `depth` 2 or 3. In a package scenario such as Freedonia's
   Mitigation most cost expressions show `inherited: true`, because the package inherits from
   the single-measure scenarios; `get_expression` per scenario says which one.
5. If results are stale, say so; a calculation runs only when the user wants it.
6. `show_in_leap` with `view` "Cost-Benefit", the baseline as reference; `read_view` for the
   discounted cumulative table by sector, module and resource, the NPV, the GHG avoided and the
   cost per tonne of CO2 equivalent avoided.
7. Drill down with `get_values` Social Costs at the root for both scenarios, all years, then at
   Demand, each Transformation module and Resources to see where the annual difference comes
   from.
8. Present: the NPV (sign and meaning), the undiscounted annual costs in two or three years, the
   categories that drive the result, the discount rate and monetary year used, and the boundary.
   A negative net cost is a saving; say which way the sign runs in the table you read.

## Entering costs

Only within the user's access setting, with `set_expression` or `set_expressions`. Cost data that
describe the technology (a plant's capital cost per MW) belong in Current Accounts so every scenario
inherits them; costs that are the measure (a program's total cost) belong in the policy scenario.
Give every value in the currency of the monetary year and in the unit shown at the variable
(`get_expression` reports unit and scale). Use `AnnualizedCost(...)` in a Total Cost or CSE
expression to turn a capital cost and lifetime into an annual cost; `LoanPayment(...)` for legacy
payments. Read `references/functions.md` in the leap-expressions skill for the function forms.

## Checks and common mistakes

- Costing off: no cost variables, no cost results. Check `AreaSetting("ShowCosts")` before
  concluding that a model has no costs.
- Counting a fuel twice: a Demand Cost that includes the fuel bill, or a Variable OM Cost that
  includes fuel, on top of the fuel costs LEAP counts at the boundary. Demand and O&M costs are
  non-fuel costs.
- Counting electricity as a fuel cost under the full-system boundary. It is not; its inputs are.
- A demand device costed both by Demand Cost and by the optimizer's Capital Cost and O&M. A
  branch converted from simulation to optimization can keep an old Demand Cost expression that
  LEAP no longer shows. `get_expression` on Demand Cost at the technology still returns it; look
  at Social Costs by category to see an activity cost that should not be there.
- Costs entered in one scenario only. A Capital Cost entered in the Mitigation scenario but not in
  Baseline makes the baseline's plants free. `get_expression` says which scenario an expression
  comes from; compare both.
- Mixed currency years: capital costs in 2015 dollars, fuel costs in 2023 dollars, monetary year
  2020. LEAP does not convert; ask which year each source is in and convert before entry.
- Discount rate ignored or assumed: read `AreaSetting("DiscountRate")`, and say it with the NPV.
  A 10 percent rate and a 3 percent rate can reverse a ranking.
- Comparing a discounted cumulative number from the Cost-Benefit table with an undiscounted
  annual Social Costs number, or cumulative with annual. Name real, discounted or nominal, and
  annual or cumulative, every time.
- Comparing scenarios with different population or GDP: the difference is not the policy's cost.
- Expecting the sign in the Cost-Benefit table to match the Results view: in the table, costs
  against the reference are positive and benefits negative.
- Calling legacy capital payments or Fuel Cost "missing" from social costs. Both are excluded by
  design; they appear in the Module Cost Balance.
- Expecting an externality cost on extraction emissions. LEAP does not cost them; do not propose
  adding it.
- A MACC read after the data changed: it does not refresh itself.
- Presenting LEAP's social cost as a financial return or a budget figure.

## Example (illustrative: numbers invented, structure as in the Freedonia sample area)

User: "How much does the Mitigation scenario cost compared with Baseline?"

1. `leap_status` → results up to date. `api_get` `AreaSetting("ShowCosts")` → on;
   `AreaSetting("DiscountRate")` → 5. `get_area` → base year 2020, end year 2050, scenarios
   Baseline and Mitigation.
2. `show_in_leap` `view` "Cost-Benefit", reference Baseline; `read_view`. The header reads
   "Discounted at 5.0% to year 2020" in US dollars: that is the discount rate, the monetary year
   and the currency. The table gives the cumulative discounted cost by demand sector, module and
   resource, the GHG avoided and the cost per tonne avoided.
3. Where they differ: `get_expression` in Mitigation at the efficient lighting and refrigeration
   technologies (Demand Cost per unit of activity as `AnnualizedCost(100, 10)`, mostly
   `inherited: true` from the single-measure scenarios) and at the wind and solar processes in
   Electricity Generation (Exogenous Capacity, Capital Cost, Fixed OM Cost, Lifetime).
   `get_branch` on Resources: Primary: Coal and Natural Gas shows Production Cost and Import
   Cost. Every changed branch carries a cost, except one new process whose Capital Cost is
   empty: report that gap first.
4. Drill down: `get_values` Social Costs at the root, scenarios "Baseline, Mitigation", 2020 to
   2050 (read the `unit` field back: real annual Million US Dollar); then at Demand, Electricity
   Generation and Resources.
5. Answer: "Against Baseline, Mitigation has a net present value of about USD 320 million over
   2020 to 2050 at a 5 percent discount rate in 2020 dollars: a net cost. Demand-side costs add
   about USD 410 million and new generation capital about USD 650 million, partly offset by
   USD 740 million of avoided coal and gas costs. It avoids about 14 million tonnes of CO2
   equivalent, at about USD 23 per tonne. Undiscounted, the extra spending is around USD 35
   million a year in 2030 and the fuel savings around USD 30 million a year by 2040. Costs are
   counted at the full-system boundary; externalities are not included." Offer the discount-rate
   what-if on the Cost-Benefit screen and a chart of annual costs by category.
