---
name: leap-emissions
description: Model emissions and air pollution in LEAP through the MCP tools: greenhouse gas and CO2 or CO2e totals, emission factors and pollutant loadings at technologies and processes, IPCC Tier 1 defaults, global warming potentials (GWP) and time horizons, non-energy sector emissions, and the IBC (Impact Benefits Calculator) add-on for air pollution, PM2.5 concentrations and health impacts. Use when the user mentions emissions, greenhouse gas, GHG, CO2, CO2e, carbon, emission factor, pollutant, air pollution, PM2.5, black carbon, health impacts, premature deaths, IBC or GWP.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: leap_status, get_area, get_branch, get_branches, find_branches, get_expression, get_values, set_expression, set_expressions, api_get, api_call, api_describe, show_in_leap, read_view, search_help, read_help_topic
  tested-on: "Freedonia, LEAP 2026.9.0.18, 2026-11-06"
  status: draft for review
---

# Emissions and air pollution in LEAP

LEAP calculates emissions by multiplying energy flows by emission factors that the user has entered
in the tree. No factor, no emissions. This skill says where the factors live, how to read and change
them, how LEAP turns gases into CO2 equivalent, how non-energy sources are added, and what the IBC
add-on does with the result. Read the help with `read_help_topic` when in doubt: "Environmental
Loadings", "Effects", "Environmental Results", "Non Energy Sector Effect Loading", "Introduction to
IBC", "Using IBC", and the FAQ section "Emissions" and "Using IBC".

## Words LEAP uses

- **Effect**: a pollutant or other direct environmental impact (CO2, CH4, N2O, PM2.5, NOx, SO2,
  black carbon, but also solid waste, deaths). The area's list is on the General: Effects screen.
  `api_get` `Effects` lists ids and names only, and only the first 100 of about 390. For GWPs read
  one effect at a time: `api_get` `Effects("Methane (Combustion and Biogenic)")` gives GWP20,
  GWP100, GWP500, Category and UsedInArea. There is no quick way to list only the effects used in
  the area.
- **Environmental loading** (emission factor): an effect per unit of energy consumed, per unit of
  energy produced (output fuels), or per unit of vehicle distance (Transport Analysis only). It is
  held on an **effect branch** (the cloud icon in the tree), one per pollutant.
- **Pollutant Loadings**: the result, in the effect's own mass unit.
- **GWP**: global warming potential, tonnes of CO2 equivalent per tonne of the gas, at 20, 100 or
  500 years. CO2 is 1 at every horizon.

## Where emission factors live

Effect branches sit one level below the branch that burns or produces the fuel:

- Demand: below each technology (the branch with a fuel and an energy intensity).
- Transformation: below feedstock fuels, auxiliary fuels and output fuels of a process.
- Resources: Primary: factors here are the optional extraction-based accounting (emissions
  attributed to the producing area wherever they occur), not the standard territorial results.

The fuel is defined on the parent, not on the effect branch, but `get_branch` reports it in its
`fuel` field for the effect branch as well as for the technology or fuel branch above it.

Reading them:

1. `find_branches` or `get_branches` with `parent` set to the technology or process and `depth` 0:
   the effect branches are listed with their effect name.
2. `get_branch` on one effect branch: its variables (the loading factor, with numerator and
   denominator units; the FAQ calls the variable "Avg Environmental Loading"; take the exact name
   from `get_branch`) and, after a calculation, its results.
3. `get_expression` for the factor in Current Accounts and in a scenario. A factor linked to the
   Technology and Environmental Database (TED) is shown as a formula or a reference, often in terms
   of the fuel's carbon or sulfur content, and is protected in Current Accounts; scenario values
   can always be edited.

In a Stock Analysis or Transport Analysis, a scenario factor is read as the factor of **newly added**
devices or vehicles; LEAP works out the stock average itself. Elsewhere it is the stock average.

## How factors are added

In LEAP (the user does this; tell them where):

- Select a technology in the Analysis view and click the green **double-plus** button to add a set
  of IPCC Tier 1 default factors for it from TED (the user should review the ones LEAP picks; the
  help notes that TED does not hold every effect for every technology, and that its factors are
  direct, not life-cycle).
- Click the single green **plus** button to add one effect, chosen from the area's effects list,
  and type the factor. New effects are made on General: Effects.
- Delete an effect branch in the tree, or with the delete button on the loadings screen.

Through the tools (needs "edit anything" access; `leap_status` says what you may do):

- Change a factor: `set_expression` on the effect branch's loading variable, in the scenario where
  the change belongs. Several at once: `set_expressions`.
- Add an effect branch: `api_call` `AddBranch(Parent, "", "Effect", "Effect=Methane")`. The name may
  be blank, as the branch takes its effect's name; below a demand technology or a transformation
  fuel the branch type may also be left out. Set units with `EffectDataNumUnit=...;
  EffectDataDenomUnit=...` in the same Properties text (`api_describe` `Branch` and
  `Branch.PropertyNames` for the exact names). Then set the factor with `set_expression`.
- Add an effect that the area does not have: `api_call` `Effects.Add(Name, Abbreviation,
  [Category], [Unit])`; its GWPs start at 0 and should be set (`api_set` `Effects("X").GWP100` and
  the others) if it is a greenhouse gas. The default category is Local air pollutants; 0 is Major
  GHGs. Check `Effects.Exists` first; many effects exist already but are hidden until Complex
  Effects is ticked in Settings: Scope & Scale.
- Nothing is saved until the user saves; every change appears in `get_changes`.

Always say what you are about to add and get agreement: adding Tier 1 defaults to a whole model is
a modeling decision, not a repair.

## Fuels with no combustion emissions

A technology using electricity, heat or hydrogen (and a solar, wind or hydro plant) correctly has
no effect branches and zero direct emissions. Its emissions are counted at the Transformation
processes that make the fuel. They show at the demand branch only in the "Direct and Indirect ...
Allocated to Demands" results. Say so before anyone adds factors to such a branch. (A user may
still choose to enter an emission factor per kWh of grid electricity at a demand branch, as the FAQ
mentions; it is a shortcut, not the standard accounting.)

## Non-energy sector effects

With "Non Energy Sector Effect Loadings" ticked in Settings: Scope & Scale, a top-level **Non
Energy** branch appears. Under it the user builds categories and effect branches; each effect
branch holds the **total annual loading** (tonnes per year, as an expression), not a factor times
energy. The variable is **Non Energy Effect Loading** (an annual mass per year) at Non Energy
branches, beside Avg Environmental Loading at energy effect branches (take the exact name from
`get_branch`). Typical uses: agriculture, livestock methane, waste, industrial processes, land use. Through
the tools: `api_call` `AddBranch(Parent, Name, "Non Energy Category")` and `AddBranch(Parent, Name,
"Non Energy", "Effect=...")`, then `set_expression`. Non-energy branches have an effect cost
variable too (mitigation cost, counted in cost-benefit results). Their emissions are in the
"Direct at Point of Emissions" GWP results but NOT in the "Allocated to Demands" ones.

## GWP sets, horizons, and CO2 versus carbon

- General: Effects holds the GWP20, GWP100 and GWP500 of every effect. The IPCC Assessment button
  swaps in the whole set from an IPCC assessment report (AR1 to AR6; AR5 with or without climate
  carbon feedbacks). Single values can be edited; an "edited" label then shows.
- A scenario can override the set: the area's top branch has an **IPCC GWP Values** variable
  (0 = use the General: Effects table; otherwise a report's values), also settable on General:
  Scenarios. `api_get` `Effects("Methane (Combustion and Biogenic)").GWP100` reads the table
  value; it applies only where the scenario setting is "none" (0).
- To name the GWP set in use, read the 100-year values of CH4 and N2O:

  | Set | CH4 | N2O |
  |---|---|---|
  | SAR | 21 | 310 |
  | AR4 | 25 | 298 |
  | AR5 | 28 | 265 |
  | AR6 | 27.9 | 273 |
- Results exist for 20, 100 and 500-year horizons; the 100-year one is the usual total.
- GWP results are in CO2 equivalent. LEAP can also show them as carbon equivalent; CO2 figures are
  44/12 times the carbon figures. If a user's number is off by 3.67, that is why.

## The environment results

Take result names from `get_branch`; the help describes them but does not spell the names:

| Result | What it is |
|---|---|
| `Pollutant Loadings` (in LEAP: "Environmental Effects (Emissions) in Physical Units") | Direct emissions at a branch, in the effect's mass unit. `filter` `Effect=Carbon Dioxide` for one gas; `Fuel=Diesel\|Effect=...` for one fuel too. The filter takes the effect's name (`Effect=Carbon Dioxide`), not the branch name (Carbon Dioxide Non Biogenic). Carbon Dioxide Biogenic is a separate effect, left out of the GWP totals by convention. |
| `One_Hundred Year GWP Direct At Point of Emissions` (also `Twenty Year`, `Five_Hundred Year`) | Direct GHG emissions in CO2e where they occur: demand, transformation and non-energy branches. Can include sinks (negative). |
| "Direct and Indirect ... Allocated to Demands" (100-year) | Demand branch emissions plus the Transformation emissions caused by that demand. Excludes non-energy. Only present if enabled in General: Results to Save. |
| "Indirect ... Allocated to Demands" (100-year) | The Transformation part alone. Same conditions. |

Notes: the area's root branch (named after the area) gives the whole-system total; the `Demand`
branch, a module or a process gives that part. Results exist only when Energy Sector Effect
Loadings is ticked in Settings: Scope & Scale and after a calculation (`leap_status`,
`resultsUpToDate`). Request single years (`first_year` = `last_year`) when only a few years are
wanted. The fixed top branches Non Energy, Indicators, Effects and Load Shapes have negative IDs
but are read like any other: `get_branch` by ID or full name, `get_branches` with one as `parent`.
Non-energy categories are read by full name (for example `Non Energy\Agriculture and Other Land
Use`); a whole-area total is the root branch (the area's name). LEAP accounts territorially, like a national inventory: emissions from making
an exported fuel count, emissions from burning an exported primary fuel abroad do not. The FAQ says
"Direct + Indirect" may differ from Direct plus Indirect by a few percent because the allocated
result treats imported energy as carrying emissions. Externality costs (a social damage cost per
unit of pollutant, on the effect's loading screen) are multiplied into cost-benefit results; they
are not applied to extraction-based factors, by design.

For a chart on screen: `show_in_leap` with the Results view, the Environment result and the branch,
then `read_view` to check what is shown.

## Coverage audit

To find where emission factors are missing:

1. Page through the tree with `get_branches`, `limit` about 150 and `offset` (depth 0 on the whole
   tree is too large to read at once), or use `find_branches` per effect name.
2. List every Demand Technology and Transformation feedstock-fuel branch that has no Environmental
   Effect children.
3. Classify electricity, heat, hydrogen, wind, hydro and solar as correct (no combustion); the rest
   are gaps. Charcoal Production and Oil Refining are commonly missed.

Freedonia's energy factors are IPCC Tier 1 defaults written as formulas such as
`18.9 * FractionOxidized * (CO2/C)` in tonnes per TJ, the same in every scenario.

## IBC: the Impact Benefits Calculator

What it adds: from LEAP's emission scenarios it estimates population-weighted PM2.5 (and ozone)
concentrations in the country, then premature deaths and illness from them, crop yield loss (wheat,
maize, rice, soy, from ozone), and global temperature change, with economic damages. Results can be
split by source (in-country, natural background, rest of world), by contributing pollutant (NOx,
black carbon, organic carbon ...), and by gender and age group. It runs in seconds because the
atmospheric model (GEOS-Chem Adjoint) was run in advance, country by country.

What it needs:

- A **national** or multi-national area with a supported country chosen in Settings: Scope & Scale
  (or General: Regions); 161 countries are supported. Not cities or provinces. `api_get`
  `AreaCountry` gives the area's country; it is "Fictitious or Example Data" for sample areas,
  which rules IBC out.
- Emissions of all the major climate and air pollutants: **CO2, methane (CH4), black carbon,
  organic carbon, PM2.5, NMVOCs, nitrogen oxides (NOx), sulfur dioxide (SO2), ammonia (NH3)**, and
  carbon monoxide (CO) where ozone impacts are wanted. PM2.5 in the air forms largely from NOx, SO2
  and NH3, so GHGs plus PM2.5 alone are not enough. Freedonia's factor sets lack black carbon,
  organic carbon, PM2.5 and NH3.
- **Both energy and non-energy sources**: crop residue burning, livestock and manure methane,
  fertilizer ammonia, waste, industrial processes. With Base Year PM Scaling the accounting must be
  comprehensive (and the base year 2010, first scenario year 2011); without it, at least the
  majority of national emissions, because the relative risk functions are not linear.
- Branches under Key Assumptions (Demographics, Disease Mortality Rates, Disease Morbidity Rates,
  Crop Production, AP Scaling, Rest of World Mitigation Effort) and under Indicators, where IBC
  writes its results; Indicators must be on (`find_branches` "Indicator" returning nothing means
  Indicators are switched off in Settings: Scope). The menu option Area: Check Area for IBC Compatibility
  (the FAQ calls it Advanced: Check for IBC Compliance) adds what is missing. The help recommends a
  category named IBC under each.
- The template is the **Asiana** area shipped with LEAP (Area: Revert to Version gives a version
  with factors and blank activity data); its structures and factors can be copied into an existing
  model. SEI's default factors are also in two Excel workbooks on the IBC page of the LEAP web site.
- Methods per scenario via Key Assumption branches `Key\IBC Settings\Relative Risk Version`
  (0 = GBD 2010, 1 = GBD 2015), `PM Scaling` (0 or 1) and `ECLIPSE` (5 or 6), else the IBC tab of
  Settings decides. IBC's own data (coefficients, rest-of-world scenarios, relative risk functions)
  download the first time an IBC area is calculated.

Where results appear: as Indicators results (concentrations, mortality, morbidity, crop loss,
climate impacts, damages); read them with `get_branch` on the Indicators branches and `get_values`.
Indoor (household) air pollution from cooking is a separate method that uses user variables at the
cooking branch and a `CALL(IndoorDeaths)` function from Asiana's functions.vbs; its results sit
beside the ambient ones. Expressions can also call `PollutionRelRiskMean("PM2.5", "COPD", conc)`
and `PollutionRelRisk(...)` directly (diseases COPD, LC, ALRI, STROKE, IHD; age group for IHD and
stroke). Only the GBD 2010 and 2015 functions have data; a 2019 choice falls back to 2015 with a
warning (unverified in the help; from LEAP's own notes).

Say plainly: IBC answers are estimates with known limits (linear coefficients, dose-response
functions from North America and Europe, no yield benefit above 90 ppb ozone); the help topic
"Uncertainties and Limitations in Using IBC" lists them.

## Checks and common mistakes

- "No results available" under Environment: energy effects off in Settings: Scope & Scale, or no
  factors; see leap-troubleshooting.
- A GWP total that is not the sum of the gases: the time horizon, the GWP set, or a scenario
  override of the set. Compare `Pollutant Loadings` per effect times the effect's GWP100.
- Emissions at an electricity-using technology: either a factor was added where none belongs, or
  the user is reading an "Allocated to Demands" result. Name which.
- Factors in the wrong denominator: per unit energy produced versus consumed at a process, or per
  distance at a vehicle; the units are in `get_branch`.
- A scale slip: the effect's mass unit is per effect (often kilograms or tonnes); read the unit
  `get_values` returns before comparing with an inventory.
- Changed factors in a scenario of a Stock or Transport Analysis apply to new devices only; the
  stock average moves slowly. Expected, not a bug.
- Non-energy missing from a "demand" emissions total: by design; use the root or the Non Energy
  branch.
- IBC results missing: wrong scale (not national), country not chosen or unsupported, Indicators
  off, required branches missing (LEAP lists them before calculating), or pollutant coverage too
  thin to mean anything.

## Worked example (Freedonia)

User: "How much CO2 does the Mitigation scenario save by 2040, and where does it come from?"

1. `leap_status`: ready, Freedonia open, results up to date. `get_area`: base year 2020, scenarios
   Baseline and Mitigation.
2. `get_branch` "Freedonia" (the root): among the results `Pollutant Loadings` and
   `One_Hundred Year GWP Direct At Point of Emissions`.
3. `get_values` root, `Pollutant Loadings`, `filter` `Effect=Carbon Dioxide`, Baseline and
   Mitigation, a single year (`first_year` = `last_year` = 2040), unit Million Tonnes: the saving
   is Baseline minus Mitigation.
4. `get_values` the same at `Demand`, at the `Transformation\Electricity Generation` module (name
   from `get_branches`) and at each Non Energy category by full name (for example
   `Non Energy\Agriculture and Other Land Use`). Demand plus Electricity Generation is not the
   total; the remainder is Non Energy (Freedonia: about 3 to 5 Mt CO2e).
5. If the user asks about all gases, repeat with `One_Hundred Year GWP Direct At Point of
   Emissions` (CO2e) and say which horizon and GWP set apply (`api_get`
   `Effects("Methane (Combustion and Biogenic)").GWP100`, the table above, and the area's IPCC GWP
   Values setting).
6. To show it: `show_in_leap` Results view, the GWP result at the root, both scenarios; `read_view`
   to confirm.
7. Report the two totals, the difference, where it arises, and that electricity-using demands show
   zero direct CO2 by design.

## Rules

- Never add emission factors to a model without agreement; say which effects and which source.
- Take a factor's fuel from the `fuel` field of `get_branch`; never infer it from the effect's
  name or the factor's unit.
- Give emissions with the effect, the horizon or GWP set where CO2e is involved, and the unit.
- Do not promise IBC results for an area that is not national or lacks the pollutant coverage.
- Do not change General: Effects GWP values to make a total match a published figure; explain the
  set and horizon instead.
