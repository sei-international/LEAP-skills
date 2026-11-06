---
name: leap-expressions
description: Write, read and fix LEAP expressions correctly through the LEAP MCP tools (get_expression, set_expression, set_expressions). Use whenever a task means entering or changing data in a LEAP area: a growth rate, a target share, a time series, a formula that refers to another branch or a Key Assumption, a link to an Excel range or to the LEAP Cloud Data Server (LCDS); or when the user asks what an expression means, where a value comes from (which scenario or region it is inherited from), why a value is what it is, or why LEAP refused an expression. Covers Interp, Growth, Step, Data, Remainder, If, BaselineValue, GrowthAs, references, units and scales, shares, Current Accounts versus scenarios, the expression search order (scenario tree, packages of scenarios, region inheritance), Excel range layouts, LCDS references, and the common mistakes.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: get_expression, get_branch, get_values, set_expression, set_expressions, search_help, read_help_topic, help_contents
  tested-on: Freedonia (sample area)
  status: draft for review
---

# Writing LEAP expressions

An expression is what the user types into a cell of the Analysis view. It gives a variable its value
in every year of the model (and every timeslice for timesliced variables): a number, a formula, a function, or a mix. One expression per variable,
per scenario, per region. This skill is about getting them right the first time.

Before you write an expression, you must already know the area's years, scenario tree and units
(the leap-orientation skill). Before you use a function you have not just looked up, read its help
topic with `search_help` and `read_help_topic`: every function has one, with syntax and examples.
Functions you use often are summarized in [references/functions.md](references/functions.md); the
help is still the authority.

## 1. Find the right cell first

An expression lives at a branch, in a variable, in a scenario, in a region. Get all four right.

0. **Scenario names**: `get_area` lists them. If the user's name does not exist ("Reference" in an
   area whose baseline is "Baseline"), say which one you used.
1. **Branch**: `find_branches` by name, then `get_branch` with the `scenario` to see its type and
   variables. With a scenario, `get_branch` returns every data variable's expression and whether it
   is inherited, so one call replaces a `get_expression` per variable; its `expressionsFor` field
   names the scenario the expressions belong to. Do not guess variable names from memory; the
   list `get_branch` returns is what exists.
2. **Variable**: read its unit and scale from `get_branch` or `get_values`. The unit decides what the
   number means (percent share, absolute level, intensity per unit of activity).
3. **Scenario**: `get_expression` with the scenario the user cares about says whether the expression
   is entered there or inherited from a parent scenario. Note which.
4. **Region** (multi-region areas): an expression may be entered in one region and inherited by
   others. Omit `region` to use the region LEAP is showing; name it when the user did.

Then read the current expression and, with `get_values`, the numbers it gives. **If the numbers do
not match what the user described** (they say "grows 3% a year" and you see 2.5%), you probably have
the wrong cell. Look further and ask. Do not change the one you found and mention the difference
afterwards.

## 2. Where to put the change: Current Accounts or a scenario

- **Current Accounts** holds the base year and other historical years. Change it only when the
  historical data are wrong, and only with the user's agreement: everything inherits from it.
- **A scenario** holds what differs from its parent from the first scenario year onwards. A policy
  assumption, a target, a different growth rate goes in a scenario.
- A scenario inherits each expression it does not have its own value for. Changing a parent
  scenario changes every child that inherits that cell. Prefer a new scenario (`add_scenario`,
  based on the baseline) to editing one the user built, unless they ask.
- Years before the first scenario year show Current Accounts in every scenario, whatever the
  scenario's expression says. Functions that need the base year (Growth, BaselineValue,
  ScenarioValue) are not usable in Current Accounts.

## 3. The base-year value is implicit

In a scenario, time-series functions such as `Interp`, `Step` and `Smooth` implicitly start from the
value in the base year, which comes from Current Accounts. A year/value
pair you give for the base year is ignored. So:

- `Interp(2030, 50, 2050, 80)` in a scenario runs from the inherited base-year value to 50 in 2030
  and 80 in 2050.
- To not include an implicit base year value use `InterpNIV`. (NIV stands for No Implicit Value)
- To start the series from the last historical year rather than the base year, use `InterpFSY`.
- After the last year you give, `Interp` and `Step` hold the last value flat unless you add a growth
  rate as the final argument: `Interp(2030, 50, 2050, 80, 1%)`.

## 4. Choosing the form

| The user says | Write |
|---|---|
| A fixed value | `12.5` |
| Grows by x% a year from the base year | `Growth(2%)`; with periods: `Growth(2%, 2030, 1%)` |
| Reaches a target in a year | `Interp(2030, 50)` (straight line from the base-year value) |
| Several targets | `Interp(2030, 50, 2040, 65, 2050, 80)` |
| Jumps to a value and stays | `Step(2030, 50)` |
| Historical series, nothing in between | `Data(2010, 100, 2015, 110, 2019, 118)` in Current Accounts |
| Follows another series | `GrowthAs(Key\GDP)` or with an elasticity `GrowthAs(Key\GDP, 0.8)` |
| Same as the baseline plus a change | `BaselineValue * Interp(2030, 1, 2050, 0.8)` (20% below baseline by 2050) |
| Depends on a condition | `If(Year < 2030, 10, 20)` |
| The share that is left over | `Remainder(100)`, in exactly one neighbor |
| Linked to a spreadsheet cell | `Excel(file, range)` or `Interp(file, range)` (needs the file saved on the user's computer) |
| Refers to another variable | `Key\Population[Million People]` or `Demand\Households:Activity Level` |

Arithmetic is `+ - * / ^`; comparisons `= <> < > <= >=`; logic `And Or Not`. `Year`, `BaseYear`,
`FirstScenarioYear`, `EndYear` are available as values. Percent signs are allowed: `5%` is 0.05.

## 5. References to other variables

Syntax: `Path\Branch:Variable[Scale Unit]`.

- Same variable at a neighbor or parent: the branch name alone is enough (`Cooking`). Further away:
  the full path (`Demand\Household\Urban\Cooking`). Another variable at the same branch: the
  variable name alone.
- `Key\Population` reaches a Key Assumption. A reference to a higher-level branch sums the variable
  over all branches below it.
- LEAP appends the unit and scale in square brackets. Write the scale you mean
  (`[Thousand Household]`), or LEAP converts to the referenced variable's own scale and unit.
- A reference to the current variable's own neighbors through `Share` or to itself is circular and
  refused.
- Data references to tagged branches: `Demand\Household:Total Activity[Household, Tag=clean]`.

Read the referenced variable with `get_expression` before relying on it. A Key Assumption only
matters where an expression refers to it; the same quantity may be entered directly elsewhere.

Time series functions such as `Interp`, `Step` and `Smooth` can also take their year/value pairs
from an Excel range (section 10) or from the LEAP Cloud Data Server (section 11).

## 6. Shares, saturations and scales

- A set of neighbors whose Activity Level unit is a **share** (percent of parent) must sum to 100%
  within 0.2% in the years LEAP checks (Current Accounts years, the first scenario year, the end
  year and every fifth year); otherwise the calculation stops with an error, or warns when the
  area's share-check setting is relaxed. When you change one share, change the others too, or put
  `Remainder(100)` in one of them. Enter the whole set in one `set_expressions` call so LEAP checks
  them together and nothing is half changed.
- A **saturation** (percent of households that own something) may sum to more than 100 across
  neighbors. The unit tells you which you have: it reads like `% Share/Household` or
  `% Saturation/Household`, with the word Share or Saturation inside it.
- The **scale** is part of the number. A variable in "Million People" with value 51.2 is 51.2
  million; write `51.2`, not `51200000`. Share and saturation units carry the percent scale, so
  `35` means 35%; a percent scale with a real unit (percent of tonnes) is refused or warned about.
  Read what `get_expression` shows for a neighbor and match its form.
- To enter a value in another unit, use `ConvUnits(from, to)`: `250 * ConvUnits(GWh, GJ)`.

## 7. Entering and checking

1. Write the expression in the form `get_expression` shows for similar cells in this area.
2. One cell: `set_expression` with `branch`, `variable`, `scenario`, `expression` (and `region`).
   Several cells that belong together: `set_expressions` with a JSON array; if any one is invalid,
   none is entered and the answer says what is wrong with each.
3. LEAP checks the expression. If it is refused, read the reason, look the function up, and
   correct it. Do not try variations blindly.
4. Read back with `get_values` for a few years (the first scenario year, a middle year, the end
   year) and confirm the numbers are what the user asked for. Say what the values are.
5. Results of that scenario and of every scenario inheriting from it are now out of date.
   Tell the user; `calculate` only when they want results.
6. Nothing is saved until the user saves or agrees to `save_area`. Say what you changed, in which
   scenario, and that it is not yet saved.

## 8. Reading an expression for the user

When asked what an expression means or why a value is what it is:

- Say where it is entered (this scenario, or inherited from which parent, or Current Accounts).
- Translate it to plain words with the actual years and numbers: "from the 2019 value it rises in a
  straight line to 50% in 2030 and 80% in 2050, then stays at 80%."
- Follow each reference one step with `get_expression` and report what it refers to.
- Give the numbers for two or three years from `get_values`, with their unit.
- When the help explains a function, give the user the topic's link; if the link is a file path
  rather than a web address, give the topic's title and address instead.

**"What drives this result?"** Read the chain from the top: the absolute activity at the sector,
then each share and saturation down the path, then the intensity at the technology (`get_branch`
with the scenario at each level). Read the result itself with `get_values`, adding `filter`
(`Fuel=Electricity`) and a `unit` where the user asked for one fuel. Say which parts of the chain
are entered in this scenario and which are inherited, and whether any Key Assumption is referenced
at all. Report the growth as the product of its parts: households × urban share × electrification
× appliance saturation × intensity.

## 9. How LEAP finds an expression: inheritance

Every cell is searched for, not stored, when LEAP needs a value. Knowing the search order tells you
where a value comes from and where a change must go. The help topic "Understanding Expression
Inheritance" (section Concepts) has worked examples; `get_expression` reports where the expression
it returns was found.

**Search order for a branch, variable, scenario and region:**

1. The scenario itself. A non-blank expression here ends the search.
2. The scenarios listed in the scenario's **First Inherits From** box (Manage Scenarios screen),
   in the order listed. This is how a scenario is built as a *package* of others: a Mitigation
   scenario that inherits first from Industry, Buildings and Transport measures.
3. The scenarios that those scenarios in turn inherit from (a package of packages), each in order.
4. Up the main scenario tree: the parent scenario, its parent, and so on to Current Accounts.
5. If nothing is found, the variable's default (usually zero).

So for Mitigation inheriting first from Industry, Buildings and Transport, where Transport is
itself a package of Cars, Buses and Rail, the full order is: Mitigation, Industry, Buildings,
Transport, Cars, Buses, Rail, Baseline, Current Accounts, default.

**Regions.** In a multi-region area each region has its own cell for every scenario. A region may
be set (General: Regions screen) to inherit from a parent region. Then at *each* step above LEAP
looks first in the active region and then in its parent region, before moving to the next scenario:
Mitigation (B), Mitigation (A), Baseline (B), Baseline (A), Current Accounts (B), Current
Accounts (A), default. A region such as "Template" in some areas exists only to be inherited from.

**What this means in practice:**

- The same expression can reach a scenario by several routes. Ask `get_expression` for the
  scenario and region the user cares about and report the source it names; do not assume "the
  parent".
- A change in a package member (Transport) reaches every scenario that lists it, directly or
  through another package. Say which scenarios are affected; `get_area` gives the main tree, and
  `api_get` on `Scenarios("name")` shows the additional scenarios it inherits from.
- A cell entered in the scenario itself hides everything below it in the order. To let a scenario
  take the package's value again, the cell in the scenario must be blank, not a copy.
- In a region that inherits from a parent region, entering a value in the parent region changes
  every child region that has no value of its own in that scenario. To change one region only,
  enter it in that region.
- Results views compare scenarios; inheritance explains why two scenarios show the same number in
  a cell neither of them changed.

## 10. Data from Excel ranges

Time-series functions (`Interp`, `InterpFSY`, `Step`, `Smooth`, `Data`, `LinForecast`,
`ExpForecast`, `LogisticForecast`) can take their year/value pairs from a workbook, and `Excel`
links one cell. The help topic "Specifying Excel File and Range Parameters" is the reference.

**File.** A file name alone is looked for in the area folder (the recommended place, so the
workbook travels with the area); otherwise give the full path as the user's LEAP sees it. The file
must exist on the user's computer and be saved; LEAP cannot link to an unsaved workbook, and the
assistant cannot supply a file. Both .xls and .xlsx work.

**Range.** A named range (`Population`) or an address (`Sheet1!B2:C15`; without a sheet name the
first sheet is used).

**Layouts for a time series.** The range must hold pairs of years and values, years in
chronological order, no duplicate years, years between 1900 and 2200. Four layouts are allowed:

| Layout | Shape | How to write it |
|---|---|---|
| Two columns, years then values | X rows × 2 columns, contiguous | one range: `Interp(Data.xlsx, B2:C15)` |
| Two rows, years then values | 2 rows × X columns, contiguous | one range: `Interp(Data.xlsx, B2:S3)` |
| Two separate columns | each 1 column wide, same number of rows | two ranges, years first: `Interp(Data.xlsx, B2:B15, E2:E15)` |
| Two separate rows | each 1 row high, same number of columns | two ranges, years first: `Interp(Data.xlsx, B2:S2, B15:S15)` |

The two-range forms suit a data table where the year header is not next to the row of values.
Both ranges must have the same size and orientation. Blank value cells are treated as missing
years. An optional growth rate can follow the range(s) in `Interp`:
`Interp(Data.xlsx, B2:C15, 1%)`.

**A single value.** `Excel(Data.xlsx, Sheet1!C7)` or a named single cell. The cell may hold a
number, a formula that yields a number, or a LEAP expression as text (then LEAP evaluates it as if
typed into the cell).

**Time-sliced data.** `ReadFromExcel(file, range)` with three vectors (years, time-slice names,
values) in one contiguous range or three equal ranges; see its help topic.

**Behavior.** LEAP reads the workbook when the expression is first evaluated and again whenever
the workbook is saved; the user can press F9 in LEAP to refresh. Values are cached, so calculations
do not reopen the file every time. Links slow calculations a little and make the model depend on
the file; typed values are more transparent. When the user asks you to "link" data, say which
trade-off they are choosing.

**Through the assistant tools.** `set_expression` accepts these forms like any other expression.
You cannot see the workbook: ask the user for the sheet, range and layout, or for the numbers, and
read back with `get_values` to confirm LEAP found the data. A refused expression naming a file
usually means the path is wrong for the user's computer or the range shape is not one of the four.

## 11. Data from the LEAP Cloud Data Server (LCDS)

The LCDS is SEI's online store of open national statistics (U.N. population and urbanization,
U.N. energy statistics, World Bank development indicators, EDGAR emissions, degree days, Global
Data Lab, GDP with SSP projections, JRC-IDEES for EU countries). A time-series function can read
a series from it:

```
Interp(LCDS, DataSet [, Series] [, Dim1 [, Dim2]] [, ISO3] [, GrowthRate])
```

The arguments after `LCDS` follow the data set's own structure, in this order: the data set
name; its series code if the set has series; its first and second extra dimensions if it has them;
the three-letter country code, which may be left out when the area is set as national with a
country chosen, or multi-national with regions mapped to countries; and, for `Interp`, a growth
rate after the last data year. Examples:

- `Interp(LCDS, UNPopulation, Medium, GHA)` (series: none; Dim1: variant)
- `Interp(LCDS, WDI, EN.CO2.TRAN.ZS, USA)` (series: indicator code)
- `Interp(LCDS, UNEnergy, Energy, 015EE, EL, KEN)` (series Energy/Physical/Share; Dim1 flow code,
  here main-activity electricity plants; Dim2 product code, here total electricity)
- `Interp(LCDS, GDP, SSP2, CHN)` (Dim1: scenario)

The values arrive in the data set's own unit and scale (for example Thousand Person,
Billion U.S. Dollar), so the LEAP variable's unit must match or the expression must convert.
Data are cached on the user's computer, so a linked model calculates without an internet
connection, and LEAP checks for newer data. When the link is made through LEAP's Time-Series
Wizard, the source notes are added to the branch's notes; through `set_expression` check with
`get_notes` and add them if missing.

Which data sets, series and dimension values exist, and how to query the server directly to find
them, is the subject of the **leap-lcds** skill. Use it before writing an LCDS expression: the
codes must be exact, and `set_expression` will refuse a code the server does not know.

## Common mistakes

- Using a function from memory with the wrong argument order or an argument it does not take.
  Look it up.
- Entering a year/value for the base year in a scenario and expecting it to count. It does not;
  the base-year value is implicit.
- Changing a share without adjusting its neighbors, so the set no longer sums to 100%.
- Writing an absolute number into a percent variable, or a scaled number without the scale.
- Fixing a wrong base-year number in a scenario instead of in Current Accounts, or the reverse.
- Changing a parent scenario when the user wanted one scenario changed, and so changing them all.
- Using `Growth` or `BaselineValue` in Current Accounts, where they are not allowed.
- Changing a Key Assumption that nothing refers to and expecting demand to move.
- Using a name from another model, or an English name in an area whose names are in another
  language.
- Expressions that call scripts (`Call`) are refused through the assistant tools; say so.
- Assuming a value comes from the parent scenario when it comes from a package scenario listed in
  First Inherits From, or from a parent region.
- An Excel range with years and values side by side given as two ranges, or two ranges of
  different sizes, or values before years.
- An LCDS code guessed from memory (series codes and flow codes must be exact).

## Example

User: "In the EV scenario, make electric cars 30% of new car sales by 2035 and 60% by 2050."

1. `find_branches` "car" → `Demand\Transport\Passenger\Cars` with children by technology.
2. `get_branch` on the parent, scenario "Passenger Electric Vehicles" → children Gasoline, Diesel,
   Electric; variable `Sales Share`, unit percent; shares entered as plain numbers.
3. `get_expression` for each child → Electric: `Interp(2030, 5)` entered in the scenario; Gasoline
   `Remainder(100)` inherited; Diesel `Step(2025, 20)` inherited.
4. `set_expression` Electric, scenario "Passenger Electric Vehicles",
   `Interp(2035, 30, 2050, 60)`. Gasoline keeps `Remainder(100)`, so the set still sums to 100.
5. `get_values` Sales Share for the three children in 2035 and 2050 → 30/10/60 and 60/20/20.
6. Tell the user: what was entered, that Gasoline absorbs the difference through Remainder, that the
   scenario's results are out of date, and that nothing is saved yet.
