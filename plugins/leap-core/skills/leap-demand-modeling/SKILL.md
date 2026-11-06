---
name: leap-demand-modeling
description: Understand, build or change the Demand part of a LEAP model through the LEAP MCP tools. Use when the user asks how demand is calculated, why a demand result is what it is, how to add a sector, end use or technology, or which method to use (activity analysis, useful energy, stock turnover, transport). Covers activity levels, shares and saturations, energy intensities, useful energy with device efficiencies, stock and sales with survival profiles, vehicles with mileage and fuel economy, and the checks that catch the usual mistakes.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: get_branches, find_branches, get_branch, get_expression, get_values, get_notes, set_expression, set_expressions, api_describe, api_call, search_help, read_help_topic
  tested-on: Freedonia (sample area)
  status: draft for review
---

# Demand modeling in LEAP

Demand is a tree: sectors, subsectors, end uses, technologies. Energy is calculated at the bottom,
from an activity and an intensity, and summed upwards. Four methods exist and can be mixed in one
area. The branch's variables, which `get_branch` lists, tell you which method a branch uses. The
help topics "Demand Analysis", "Activity Analysis", "Useful Energy Demand Analysis",
"Stock Analysis" and "Transport Analysis" are the reference; read them with `read_help_topic`
before explaining a method.

How to lay out a demand tree in the first place (top-down by fuel, bottom-up by end use and
device, or a hybrid with historical and projection branches), and how to hold energy-balance data
in user variables, is the subject of the companion skill **leap-demand-structures**. This skill is
about how the methods calculate and how to read and change demand data.

## The four methods, and how to recognize them

| Method | Energy = | Variables you will see | Typical use |
|---|---|---|---|
| Activity analysis (final energy) | activity × final energy intensity | Activity Level at every level; Final Energy Intensity at the technology | Most sectors |
| Useful energy | useful energy demand ÷ device efficiency, by device share | Useful Energy Intensity (or Final Energy Intensity plus Fuel Shares and Efficiency in Current Accounts) at the end use; Activity Level (shares) and Efficiency at devices | Heating, cooling, cooking, industrial heat where fuel switching and efficiency are separate questions |
| Stock turnover | stock of devices × energy per device | Stock, Sales, Device Share, Lifetime or Survival Profile, intensity of new and existing devices | Appliances, equipment with standards for new sales |
| Transport (stock turnover) | vehicles × mileage × fuel economy | Stock or Sales, Mileage, Fuel Economy, Survival Profile; emission factors may be per distance | Vehicle fleets where standards for new vehicles matter |

**Transport is often plain activity analysis**, not the vehicle-stock method: passenger-km or
tonne-km per person at the mode level, mode shares below, and a Final Energy Intensity in liters or
megajoules per passenger-km at the technology. If `get_branch` shows Final Energy Intensity and
no Stock, Sales, Mileage or Fuel Economy, it is activity analysis. Read the method from the
variables, never from the sector's name.

## Activity analysis in detail

- One **absolute** activity near the top (households, tonnes of steel, floor area, passenger-km).
  Below it, **shares** (sum to 100% across neighbors) or **saturations** (penetration; may exceed
  100% across neighbors). The unit of Activity Level says which. LEAP checks that shares sum to
  100 within 0.2%, in every Current Accounts year, the first scenario year, the end year and every
  year divisible by 5; a set that fails stops the calculation with an error, or gives a warning in
  the Diagnostics tab when the setting "Do not check that share values sum to 100%" is ticked.
- The product of the activity levels down the path, times the Final Energy Intensity at the
  technology, is the energy. `Total Activity` holds the product; `get_branch` lists it among the
  data variables with the expression `<Calculated>`, because LEAP computes it.
- A share is a share of the branch directly above, not of the sector: Cars at 33% of Road, with
  Road at 80% of Passenger, is 27% of passenger travel. When one share rises, the `Remainder(100)`
  neighbor falls by the same amount.
- To project energy directly, without an activity, the Activity Level unit is "No data".
- Intensity is energy per unit of the activity above it. The unit returned may be a physical unit
  alone ("Liter"), the "per" part being the parent's activity unit; LEAP converts physical units
  to energy with the fuel's energy content. Read it before changing it.
- **Finding a technology's fuel**: the fuel is not a variable; `get_branch` reports it in its
  `fuel` field (for a demand technology, a fuel branch or an effect branch under one). Do not
  infer it from the intensity unit. `list_fuels` gives the exact fuel names for filters.
- Drivers that are easy to miss: `GrowthAs(Key\Income, 1.1)` ties a level to another series with
  an elasticity (here travel grows 1.1 times as fast as income); an `Interp` on a share shifts
  activity between neighbors without changing the total.

## Useful energy in detail

- The end-use branch carries the useful energy intensity; the devices below it carry efficiencies
  and activity shares. Energy for a device = useful demand × device share ÷ efficiency.
- In Current Accounts the user may instead have entered final intensity, fuel shares and
  efficiencies; LEAP derives the useful intensity. In scenarios, project useful intensity,
  shares and efficiencies.
- Fuel share (share of final energy) is not activity share (share of the activity). Do not mix them.

## Stock turnover and transport in detail

- Current Accounts: the existing stock and its average intensity (or fuel economy). Scenarios:
  sales of new devices from the First Sales Year, with a survival profile that retires them, and
  the intensity of new devices. The stock average improves gradually as old devices leave.
- A standard for new devices changes the **new-device** intensity or fuel economy and the **sales
  share**. Changing the stock-average value overwrites the turnover logic.
- Stocks and sales may be entered at the technology or top-down at the branch under Demand, with
  device shares below. `get_branch` shows which.
- Transport allows emission factors per vehicle-km as well as per unit of energy.

## Reading a demand result

1. `get_values` on the branch for `Final Energy Demand` (or `Energy Demand Final Units` where the
   user wants fuel units), with `filter` by fuel if needed.
2. Walk up: `get_branch` with the scenario at the branch and each parent (one call per level
   gives every variable and whether it is inherited). An inherited scenario expression such as
   `Interp(2050, 75)` says nothing about the starting value: read Current Accounts too
   (`get_branch` with scenario "Current Accounts", or `get_expression`). Follow Key Assumption
   references.
3. Check intensity: `get_values` for Final Energy Intensity at the technology.
4. For "why does it grow": compute, for each factor in the chain (population, activity per person,
   each share, intensity), the ratio of the end-year value to the base-year value. Their product
   must equal the ratio of the energy result; report the factors in that form.
5. Check the base year by arithmetic: activity × intensity × the fuel's energy content should
   reproduce the base-year `Final Energy Demand`. It is the strongest check there is.
6. Read `get_notes` on the branch and its parents: the modeler's sources and assumptions are there.
   Comments left inside expressions are a sign the notes were skipped; suggest moving them.

The `variablesFor` field in a `get_branch` answer names the scenario its variables and expressions
are for: the one you gave, or else the one selected in LEAP (give `scenario` for another). Which
variables a branch has can differ by scenario. When a number is off by a round factor (1000,
1,000,000, 3.6), suspect a scale or unit, not the model. Read only the help topic for the method
the branch actually uses.

## Changing demand data

- Scenario or Current Accounts: see leap-expressions. A base-year error belongs in Current
  Accounts; a projection belongs in a scenario.
- Changing a share: enter the full set of neighbors in one `set_expressions` call, or make sure one
  of them is `Remainder(100)`.
- Changing an activity at a high level changes every branch below it. Say so.
- Intensity in a scenario relative to the baseline: `BaselineValue * Interp(2030, 1, 2050, 0.7)`.

## Adding branches

Adding a sector, end use or technology is a structural change: it works only when the user lets
assistants edit anything, and it needs the right branch type and, for a technology, a fuel.

1. `api_describe` with object `Branch` and filter `AddBranch` to read the method and its arguments;
   `api_call` `BranchTypeNames()` lists the types. Categories and technologies have different
   types; a technology below a useful-energy end use has its own.
2. Mixed neighbors (a technology beside a category) are refused in some places and allowed in
   others; when LEAP refuses, tell the user why and do not force it.
3. After adding, `get_branch` to see the variables the new branch has, then enter Current Accounts
   data first (activity, intensity, fuel) and only then scenario data.
4. Give each new branch notes with `set_notes`: what it is, where the numbers came from.
5. For many branches from a table, the user's own Tree: Create Branches from Excel in LEAP is
   faster and safer than one `api_call` per branch; suggest it.

## Checks before you say demand is right

- Every technology has a fuel and an intensity greater than zero, and base-year activity ×
  intensity × energy content reproduces the base-year energy.
- Shares sum to 100% in every year; saturations are between 0 and 100.
- Units: the activity unit at each level matches what the intensity below is "per".
- No Key Assumption is changed that nothing refers to.
- After a calculation, the Diagnostics tab of the Results view (the user can see it; `api_get` on
  the diagnostics is not available) lists demand branches with no fuel and fuels no module produces.

## Common mistakes

- Entering a saturation where a share was meant, so the shares never sum to 100.
- Setting the intensity in a scenario when the Current Accounts value is the wrong one.
- Treating `Total Activity` as data; it is a result.
- Changing a stock-average value in a stock-turnover branch instead of new-device sales and
  intensity.
- Changing a share at one technology and leaving the neighbors, so the calculation stops.
- Confusing fuel share with activity share under a useful-energy end use.

## Example

User: "Why does household electricity demand triple by 2040 in the Reference scenario?"

1. `get_values` `Demand\Household`, `Final Energy Demand`, Reference, filter `Fuel=Electricity`,
   2010 to 2040 → ×3.1.
2. `get_branches` parent `Demand\Household` depth 0 → Urban/Rural, then end uses, then devices.
3. `get_expression` Activity Level at Household → `Key\Households`; at Key\Households →
   `Growth(2.5%)` (×2.1 over 30 years). At Urban → `Interp(2040, 70)` from 45% (×1.56).
4. Electrification: at Urban\Lighting, Electric share `Interp(2040, 100)` from 60.
5. Explain: 2.1 × 1.56 ≈ 3.3 of the growth is households and urbanization; the rest is the
   lighting electrification; intensities are flat. Give the user the branch names so they can see
   it in the Analysis view.
