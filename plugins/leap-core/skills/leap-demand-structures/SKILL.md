---
name: leap-demand-structures
description: Choose and build the structure of the Demand part of a LEAP model through the LEAP MCP tools. Use when the user asks how to structure a demand model, how detailed the model should be, top-down versus bottom-up, sectors broken down by fuel versus end uses and devices, final versus useful energy, how to put energy balance data into LEAP, how to use several historical years in Current Accounts, how to calibrate a bottom-up projection to the energy balance in the last historical year, how to set technology shares, or how to organize demand in a multi-region model with a template region. Covers the spectrum of structures, branch types, historical balance data in user variables, the hybrid Historical/Projections pattern and its calibration, and how to choose.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: leap_status, get_area, get_branches, find_branches, get_branch, get_expression, get_values, get_notes, api_get, api_describe, api_call, set_expression, set_expressions, search_help, read_help_topic
  tested-on: "pattern studied on a live hybrid model and the skill tested read-only on it, 2026-11-06"
  status: draft for review
---

# Structuring a demand analysis in LEAP

This skill is the companion of `leap-demand-modeling`, which explains the calculation methods and
how to read a demand result back to its drivers. This one is about the shape of the tree and
where the data go. Expression rules are in `leap-expressions` (sections 3, 4, 6 and 9); regions
in `leap-multi-region`. The help topics "Demand Analysis", "Final Energy Demand Analysis",
"Useful Energy Demand Analysis", "Demand Branch Properties" and "LEAP Data Requirements" are the
reference: read the relevant one with `read_help_topic` when you recommend a structure or a
change of branch type; for describing an existing model the tools below are enough.

**Reading an inherited model, in this order:** `get_area` for the years (base, first scenario,
and from Current Accounts' data the last historical year); `get_branches` under Demand with
`depth` 2, looking for Historical and Projections pairs; `get_branch` on a sector, its Historical
branch and one fuel branch, each in Current Accounts and in the baseline; one end use and one
device on the Projections side; `get_values` Final Energy Demand for Historical and Projections
and two fuels across the boundary years; then the notes on the end uses, where calibration
sources usually sit (sector notes are often empty).

LEAP's own words: "LEAP provides a lot of flexibility in how you structure your demand data",
from "highly aggregate" to "highly disaggregated end-use oriented structures", and the level of
detail can differ from sector to sector in one area. No structure is the right one for every
study; the right one answers the user's questions with the data the user has.

## 1. The spectrum of structures

Energy is always calculated at the lowest branch as activity times intensity (or by stock
turnover) and summed upward. What differs is how many levels there are and what they mean.

| Structure | Tree | Data needed per year | Questions it can answer | Questions it cannot |
|---|---|---|---|---|
| (a) Top-down, sector by fuel | `Sector` → one technology per fuel | Energy use per fuel from the energy balance; optionally an activity (value added, households) and the implied intensity | Totals by sector and fuel; trend and elasticity projections; supply and emissions downstream | Anything about end uses or equipment: efficiency standards, fuel switching inside an end use, device costs |
| (b) Sector, subsector, fuel | `Sector` → `Subsector` → fuel technologies | The same, by subsector (industry branches, transport modes, building types) plus a subsector activity (tonnes of cement, passenger-km) | Structural change between subsectors; intensity targets per subsector | Still nothing about devices |
| (c) Bottom-up | `Sector` → `Subsector` → `End use` → `Device` | An absolute activity at the top; shares or saturations below; per device a fuel and an intensity (or useful intensity at the end use with efficiencies at devices); for stock turnover, stocks, sales, lifetimes | Efficiency programs, fuel switching, electrification, device costs, least-cost choice of devices | Nothing more, but it costs ten to a hundred times the data and time, and the device data rarely come from the balance |

Rules:
- A top-down branch set can be projected directly: Activity Level unit "No data" and the
  energy per fuel entered as the intensity, or an activity with the intensity derived from
  balance divided by activity (section 3). Both are legitimate LEAP structures.
- A sector can be (a) while its neighbor is (c). The help says so and the calculation does not
  mind. Put the detail where the policy questions are.
- The depth of the tree is not the quality of the model. A four-level household tree with
  invented saturations is worse than a two-level one with the balance in it.

## 2. Branch properties, and telling them apart

The Demand Branch Properties screen (help topic of that name) sets a demand branch's type:

| Type | Holds | How `get_branch` shows it |
|---|---|---|
| Category | Activity Level, costs, user variables; organizes the tree | `type` "Demand Category"; data variables Activity Level, Demand Cost, no intensity |
| Category with Energy Intensity | An intensity one level above the technologies: Final Energy Intensity with Fuel Share at the technologies below, or, with "useful energy analysis" ticked, Useful Energy Intensity with Efficiency and Activity Level shares below | `type` "Demand Category" with a Final Energy Intensity or Useful Energy Intensity variable; may show Optimize Devices |
| Technology with Energy Intensity | A fuel and a Final Energy Intensity per unit of the activity above | `type` "Demand Technology"; Final Energy Intensity; effect branches below |
| Technology with Total Energy | A fuel and the total energy, ignoring Activity Level | "Demand Technology" with a total energy variable (**unverified** name) |
| Stock Analysis, Transport Analysis | Stock, Sales, Lifetime or Survival Profile, intensity per device or Mileage and Fuel Economy | "Demand Technology" with those variables |

- Technologies always sit at the bottom, each with one fuel. The fuel is not a variable:
  `get_branch` reports it in its `fuel` field (`leap-demand-modeling`).
- Below a Category with Energy Intensity only Technology with Energy Intensity branches may
  sit; only effects may sit below a technology; stock and transport technologies keep to
  themselves. Other neighbors may be mixed (a technology for a minor use beside subsectors).
  `leap-demand-modeling` section "Adding branches" covers what LEAP refuses.
- The type can be changed later (a category with only technologies below it can become a
  Category with Energy Intensity; the technologies then need Fuel Share in place of intensity).
  LEAP asks to confirm; data for variables that no longer apply are kept but unused.

## 3. Historical balance data in user variables

Energy balances give energy by sector and fuel for several years. Current Accounts may hold
several historical years (help: Scenarios); the base year is the first, the year before the
First Scenario Year is the last historical year (`LastHistoricalYear` in expressions), and
`get_area` reports `baseYear` and `firstScenarioYear`. The pattern that keeps the balance in
the model, rather than in a spreadsheet beside it:

1. **One user variable per fuel branch** (Analysis: User Variables; visible at demand
   technologies, Current Accounts only), say `FuelUseHistorical`, unit an energy unit, holding
   the balance series: `Interp(2010, 120, 2011, 124, ..., 2022, 150)` or a `Data` series, in
   thousand tonnes of oil equivalent or whatever the balance uses. A user variable visible in
   Current Accounts only is read by `get_branch`, `get_expression` and `get_values` with
   scenario "Current Accounts", whatever LEAP's screen shows; asked for in another scenario,
   the tool refuses and says where it exists. `api_get` `UserVariables("FuelUseHistorical")`
   gives its definition and note.
2. **A user variable at the parent** summing them, say `HistTotalEnergy`:
   `TotalChildren(FuelUseHistorical[Thousand TOE])`.
3. **An activity at the sector** in Current Accounts, from a Key Assumption: value added for
   services and manufacturing (`Key\GDP[Billion USD] * Key\VA Share\Services[%] / 100`),
   physical production for cement, steel, fertilizer (tonnes), households for the residential
   sector, passenger-km and tonne-km for transport. Enter these in Current Accounts as
   historical series too.
4. **The intensity, derived.** Make the sector (or subsector) branch a Category with Energy
   Intensity and write, in Current Accounts:
   `Final Energy Intensity = HistTotalEnergy[TOE] / Total Activity[Billion USD]`
   (`Total Activity` is the product of the activities down the path; LEAP calculates it).
5. **Fuel shares, derived.** At each fuel technology, in Current Accounts:
   `Fuel Share = 100 * FuelUseHistorical[TOE] / Parent:HistTotalEnergy[TOE]`
   (or, with the branch named, `Sector\Historical:HistTotalEnergy`). One of them may be
   `Remainder(100)` instead. Shares must sum to 100% in every Current Accounts year.
6. **Projection, in scenarios.** Project the activity (the Key Assumption grows), the intensity
   (`Growth(-1%)`, `Interp`, or `Growth(HistoricalGrowth)` to continue the historical trend) and
   the fuel shares (section 6). LEAP then computes demand by fuel for every year.

Then base-year demand by fuel reproduces the balance exactly, every number has its source in
the tree, and a new balance year is one more pair in each `Interp`. Variants seen in practice:
the Final Energy Intensity written per fuel technology instead (`FuelUseHistorical / Total
Activity`) with no shares; or the sector activity set to "No data" and the energy entered
directly. The user-variable topic (help: User Variables) says they can be read-only, hidden in
scenarios, limited to a branch type or tag, and given a default expression such as `0`.

Give the sector branch notes (`set_notes`) naming the balance, its edition and its units.

## 4. Final versus useful energy

- **Final energy analysis**: the intensity is fuel per unit of activity at the device. Right
  when the question is total consumption and the devices are not substitutes for one another.
- **Useful energy analysis** (Demand Branch Properties: Category with Energy Intensity, tick
  "useful energy analysis"): the end use carries a Useful Energy Intensity (the heat delivered,
  not the fuel burnt; energy units only), the devices carry Efficiency and Activity Level
  shares. Right when fuel switching and device efficiency must move separately from the service
  demand: heating, cooling, cooking, industrial heat, kilns.
- **Two ways to fill Current Accounts for useful energy** (help: Useful Energy Demand Analysis):
  - tick "Final Energy Intensities in Current Accounts": enter the final intensity at the end
    use, Fuel Share and Efficiency at the devices; LEAP derives the useful intensity and the
    device activity shares. Use this when the balance gives you fuel use and you do not know
    the useful demand;
  - leave it unticked: enter the useful intensity directly (when a building study gives heat
    demand per square meter). Then the devices get Activity Level shares and Efficiency.
  In scenarios you always project useful intensity, device shares and efficiencies, whichever
  way Current Accounts was filled. Fuel share (share of final energy) is not activity share
  (share of the service): with a 90% boiler and a 300% heat pump each serving half the floor
  area, the boiler's fuel share is far above 50%.
- Switching an existing end use to useful energy is a Properties change in LEAP; the
  technologies below lose their intensities and need Fuel Share or shares and Efficiency. Tell
  the user what will be asked for before suggesting it. **Unverified** whether the useful-energy
  check box can be set through `api_set`; `api_describe` with object `Branch` lists what exists.

## 5. The overall methods, in one paragraph each

`leap-demand-modeling` has the calculation detail and the variables to recognize each one.

- **Activity analysis**: one absolute activity near the top, shares or saturations below, an
  intensity at the bottom. The default and the right choice for most of the tree.
- **Stock turnover** (Stock Analysis branches): stocks of devices, sales, a survival profile,
  intensity of existing and new devices. For long-lived equipment where a standard on new
  sales takes years to reach the stock.
- **Transport stock turnover** (Transport Analysis branches): vehicles, mileage, fuel economy;
  emission factors may be per vehicle-km. For fleets where new-vehicle standards matter.
- **Activity-based transport**: ordinary activity analysis with passenger-km or tonne-km at the
  mode level (or vehicles per person times km per vehicle), mode and technology shares below,
  and an intensity in megajoules per passenger-km or per vehicle-km at the technology. Much less
  data than a fleet model and enough for mode shift and electrification questions.

## 6. How technology shares within an end use are set

The devices under an end use share its activity. Three ways to set the shares, and one area may
use a different way in different scenarios (`Optimize Devices` is shown in every scenario,
Current Accounts included, as 1 or 0, and its value may differ by scenario; help: Optimize
Devices):

(a) **Exogenous, in a simulation scenario.** `Interp(2030, 25, 2050, 60)` on every technology
    but one, `Remainder(100)` on the last. Enter the set in one `set_expressions` call.
    `Interp` starts from the Current Accounts value implicitly (`leap-expressions` section 3).

(b) **Interrelated variables.** Shares driven by something else: a Key Assumption
    (`Key\Heat Pump Uptake[%]`), a price ratio, income, or a logistic curve written out
    (`100 / (1 + Exp(-0.3 * (Year - 2035)))`). Keep the result inside bounds with
    `Constrain(expression, 0, 100)`, and keep one neighbor `Remainder(100)`. A share held in an
    unscaled user variable and normalized afterward,
    `100 * ShareUnscaled[%] / Total(ShareUnscaled[%])`, avoids the sum-to-100 error when
    several shares move independently. `Maximum Annual Share Change` exists only for optimized
    technologies and the help marks it "not yet operational".

(c) **Endogenous, under energy system optimization.** At the end use (a Category with Energy
    Intensity, useful energy analysis on) set `Optimize Devices` to Yes in the optimization
    scenario; the technologies then show capital, O&M, lifetime and unit-capacity variables and
    the constraints `Minimum Share`, `Maximum Share` (help: "not yet operational") and device
    number and addition limits. Costs are required; `Demand Cost` is ignored there so equipment
    is not costed twice. The value is the same in every region. `leap-optimization` has the rest.

Say which way the area uses before changing a share: `get_branch` on the end use with the
scenario shows `Optimize Devices`; the technology's Activity Level expression shows (a) or (b).

## 7. The hybrid approach: top-down history, bottom-up scenarios

National balances give fuel by sector for many years; device data exist, if at all, for one
recent year. The hybrid keeps both without double counting.

**Structure.** Under a sector (or a subsector or end use), two sibling categories:

```
Sector                      Activity Level: the sector driver (value added, households, tonnes)
  Historical                Category with Energy Intensity; fuel technologies below
    Fuel A, Fuel B, ...     FuelUseHistorical user variable, Fuel Share
  Projections               Category; the bottom-up tree below
    Subsector\End use\Device ...
```

**The switch.** Both siblings have share units. In Current Accounts:
`Historical: Activity Level = Step(BaseYear, 100, FirstScenarioYear, 100)` (or simply `100`),
`Projections: Activity Level = Remainder(100)` → 0. In the baseline (and so in every scenario
below it): `Historical: Activity Level = Step(BaseYear, 100, FirstScenarioYear, 0)`, Projections
still `Remainder(100)` → 100 from the first scenario year on. So the balance supplies every
historical year and the bottom-up tree supplies every scenario year, and the sector total is
one continuous series. In a one-year-per-row variant the same is written as
`If(Year < FirstScenarioYear, 100, 0)`. The `Step` form is the one seen in practice.

**The Historical side** is section 3: `HistTotalEnergy = TotalChildren(FuelUseHistorical)`,
intensity = total over activity, fuel shares from the balance. In the baseline its intensity can
stay `Growth(0%)` and its fuel shares can continue the historical trend,
`Growth(Constrain(HistoricalGrowth(2010, LastHistoricalYear), -5%, 5%))` normalized as in 6(b),
so that a sector with no Projections branch (agriculture, non-energy use) still projects.

**The Projections side** is section 1(c) or 4, with its own activity chain below the shared
sector driver: floor area per unit of value added, households by location, vehicles per person
times km per vehicle, tonnes of product. Its Current Accounts data (useful intensities,
shares, efficiencies) are entered for the last historical year even though its activity is
zero then, because scenario functions start from the Current Accounts value.

**Calibration.** In the last historical year the bottom-up tree's final energy by fuel must
equal the balance's. Two ways:

- *Outside LEAP*: build the device shares and intensities in a workbook that already sums to
  the balance, and paste the numbers into Current Accounts. Simple and common; the link to the
  balance lives in the workbook, so record it in the notes.
- *Inside LEAP, with a factor per fuel*: a user variable or Key Assumption,
  `Calibration\Fuel A = Sector\Historical\Fuel A:FuelUseHistorical[TOE, LastHistoricalYear]
  / Sector\Projections:Final Energy Demand[Fuel=Fuel A, LastHistoricalYear]` (**unverified**
  that a result reference in Current Accounts data resolves this way; a safer form divides by a
  user variable `UncalibratedUse` that holds the bottom-up sum written out as data), and then
  every device of that fuel: `Final Energy Intensity = 0.8 * Key\Calibration\Fuel A` (or the
  useful intensity scaled, when all devices of an end use share one fuel). A factor far from 1
  (below 0.7 or above 1.4) means the device data or the activity are wrong, not that the factor
  should be larger.

**What to check after calibration** (`get_values`, baseline, one call per fuel with `filter`
`Fuel=...`, and the Historical and Projections branches separately):
- Historical by fuel in the last historical year equals the balance; Projections is zero there.
- Compare intensities, not energy, across the boundary: Projections' Final Energy Demand divided
  by `Total Activity` in the first scenario year should be within a few percent of Historical's
  in the year before. Energy itself may step up by the activity growth between the two years
  (several percent in a fast-growing economy), and that is not an error.
- The sector total shows no step beyond that activity growth at the first scenario year; by fuel,
  a fuel that steps more than the others points at its device data.
- Calibration is often done in a workbook rather than in the tree; then the notes on the end
  uses name the balance figure and the workbook. Say where the evidence is.
- Shares under every end use sum to 100 in the last historical year and the first scenario year.
- `Total Activity` at Projections is 0 in historical years and the full driver afterward.

## 8. Demand in multi-region models

- The tree is the same in every region; only expressions differ (`leap-multi-region` section
  1). Build the demand structure once, at the level of detail the poorest region's data allow,
  and let richer regions add detail with user variables rather than extra branches.
- Good practice: a non-calculating **template region** (often the first region; `get_area` →
  `includedInResults` false) that holds the equations and shared assumptions (the hybrid
  switch, the derived intensity and share expressions, the calibration formulas, default
  device efficiencies), with the real regions inheriting from it and entering only what differs
  (their balance series in `FuelUseHistorical`, their activities). The template's own numbers
  are placeholders and mean nothing.
- Expressions that must work in every region use relative references: `Parent`,
  `TotalChildren`, `Total`, `Remainder`, and `Branch:Variable` references to branches that
  exist everywhere. `RegionValue` reaches another region's value when needed.
- To see what a region overrides: `get_expression` with `region` names the scenario and
  region the value was found in ("found in Template" means inherited). `get_branch` with
  `scenario` and `region` does it for every variable of a branch. A stray number in a child
  region hides every later template change in that cell (`leap-multi-region` section 5).

## 9. Choosing a structure

Ask, in this order, and write the answers into the area notes:

1. **Purpose.** A national plan, a mitigation assessment, an electricity demand forecast, a
   teaching model? Which three results must the report show?
2. **Policies to represent.** Appliance or vehicle standards, building codes, fuel switching,
   electrification, modal shift, industrial process change, carbon prices or least-cost device
   choice. Each named policy needs the level at which it acts (device, end use, subsector).
3. **Data.** Which balance years exist; by sector only or by subsector; any survey, census or
   vehicle registry with device data; which year.
4. **Time and people.** Sessions available for data work, and who maintains the model later.
5. **Regions.** One or several; are the same data available for each.

| Situation | Recommend |
|---|---|
| A balance by sector, a few weeks, totals and emissions wanted | (a) top-down by fuel, intensities derived from activity, trend projections |
| A balance by subsector, structural change matters | (b) sector, subsector, fuel |
| Standards, fuel switching or device costs in one or two sectors, device data for one year | Hybrid (section 7): top-down everywhere, bottom-up where the policies act |
| Long-lived equipment and new-sales standards | Stock turnover or transport stock turnover under the bottom-up branch |
| Least-cost choice of devices | Useful energy end uses with Optimize Devices, costs on every device |
| Several regions with uneven data | Template region, shallow common tree, detail by user variables |

Say plainly when the user's ambition exceeds the data: a bottom-up tree without device data is
a top-down model with more cells to fill.

## 10. Common mistakes

- Building the tree first and finding the data later; the data decide the tree.
- Fuel branches under a top-down sector given an intensity in "No data" form and a sector
  activity as well, so the activity does nothing; choose one.
- Several historical years in Current Accounts but the fuel shares entered as one number, so
  the base-year check passes and the later balance years are wrong.
- In the hybrid, forgetting the baseline override of the Historical switch, so both sides are
  on from the first scenario year (demand doubles) or Projections never turns on.
- Setting Current Accounts data on the Projections side only in the base year while the
  calibration year is the last historical year; `Interp` in a scenario then starts from the
  wrong value.
- Calibrating by changing the balance to match the devices.
- Mixing fuel shares and activity shares under a useful-energy end use.
- Changing the type of a branch through Properties without telling the user which variables
  go away.
- In a multi-region area, writing the balance series into the template instead of the region.
- A tree so deep that the Analysis view needs a page per sector and nobody can audit it.

## Example (generic names; not run against an area)

User: "We have the services sector in the national balance for 2010 to 2022 by electricity,
natural gas and fuel oil, a 2022 building survey with heating and lighting equipment, and want
a heat-pump scenario. How should we structure it?"

1. `get_area` → base year 2010, first scenario year 2023. Activity for services:
   `Key\Services Value Added[Billion USD]`, a historical series in Current Accounts.
2. Structure (recommend the hybrid, section 7):
   ```
   Demand\Services                         Activity Level = Key\Services Value Added
     Historical                            Category with Energy Intensity
       Electricity | Natural Gas | Fuel Oil   FuelUseHistorical, Fuel Share
     Projections                           Category, Activity Level share
       Buildings                           Floor area per unit of value added
         Space Heating                     Useful energy end use, Activity Level 100% saturation
           Gas Boiler (Natural Gas, 85%) | Oil Boiler (Fuel Oil, 80%)
           | Electric Heater (Electricity, 100%) | Heat Pump (Electricity, 300%)
         Lighting                          Final energy end use
           Fluorescent (Electricity) | LED (Electricity)
   ```
3. Current Accounts, Historical: `FuelUseHistorical` per fuel from the balance
   (`Interp(2010, 300, ..., 2022, 360)` in thousand TOE); at Historical
   `HistTotalEnergy = TotalChildren(FuelUseHistorical[Thousand TOE])`,
   `Final Energy Intensity = HistTotalEnergy[TOE] / Total Activity[Billion USD]`,
   `Activity Level = 100`; at each fuel `Fuel Share = 100 * FuelUseHistorical[TOE] /
   Parent:HistTotalEnergy[TOE]`, the last `Remainder(100)`. Projections `Remainder(100)`.
4. Current Accounts, Projections: floor area from the survey; Space Heating useful intensity
   and device shares from the survey's equipment counts and the balance's 2022 gas, oil and
   heating electricity, worked out so that `share ÷ efficiency × useful intensity × floor area`
   sums to each fuel's 2022 use; Lighting intensity per square meter and the fluorescent/LED
   split likewise against the rest of 2022 electricity. Notes on each branch name the survey
   sheet.
5. Baseline: `Historical: Activity Level = Step(BaseYear, 100, FirstScenarioYear, 0)`; value
   added grows; useful intensity flat; device shares `Interp` with Gas Boiler `Remainder(100)`;
   LED share rising.
6. Heat-pump scenario (child of the baseline): only `Heat Pump: Activity Level = Interp(2035,
   30, 2050, 60)`; the `Remainder(100)` boiler falls. Nothing else changes.
7. Checks: `get_values` `Demand\Services`, `Final Energy Demand`, baseline, `filter`
   `Fuel=Natural Gas`, 2021 to 2025: 2022 equals the balance, 2023 within a few percent of 2022,
   no step; repeat for the other two fuels; shares sum to 100 under both end uses. Then hand
   the user the branch names to look at in the Analysis view.
