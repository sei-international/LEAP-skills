# LEAP expression functions used most often

Taken from the LEAP help (section Expressions). Each function has its own topic there; read it
with `read_help_topic` before using a form not shown here. Syntax in square brackets is optional.

## Time series

**Interp**(Year1, Value1, Year2, Value2, ..., YearN, ValueN [, GrowthRate])
Straight-line interpolation between year/value pairs. After the last year, flat unless a growth rate
is given. In a scenario the base-year value is implicit and overrides any pair for that year.
Also: Interp(ExcelFile, Range [, GrowthRate]) or Interp(ExcelFile, YearsRange, ValuesRange
[, GrowthRate]); Interp(LCDS, DataSet, ...) for the LEAP Cloud Data Server; Interp(Branch:Variable)
where that variable holds a Data(...) series. The same forms apply to Step, Data, Smooth and the
forecast functions.
Example: `Interp(2000, 10, 2010, 16, 2020, 30, 2%)` → 2005 = 13, 2021 = 30.6.

**InterpFSY**(same arguments)
As Interp, but the implicit starting point is the year before the first scenario year, not the base
year. Use when Current Accounts holds several historical years.

**Step**(Year1, Value1, ..., YearN, ValueN)
Holds each value from its year until the next pair. Same implicit base-year rule.

**Data**(Year1, Value1, ..., YearN, ValueN)
Raw year/value pairs, no interpolation; unlisted years are zero. For historical data in Current
Accounts, and as the source for Interp(Branch:Variable).

**Smooth**(Year1, Value1, ... ) — polynomial through at least three points.

**LinForecast / ExpForecast / LogisticForecast**(Year1, Value1, ...) — regression forecast from
historical pairs. ExpForecast(FirstYear, LastYear) in a scenario forecasts from the Current
Accounts data between those years. Use with care; check the fit.

**Cycle**(Year, Value1, Value2, ...) — repeats the list of values from Year on, one per year.

## Growth

**Growth**(Rate) or Growth(Rate1, Year2, Rate2 [, Year3, Rate3 ...]) up to five periods.
Compound growth from the base-year value. Scenarios only. `Growth(5%)`; `Growth(5%, 2015, 2%)`.

**GrowthAs**(Branch:Variable [, Elasticity])
Grows at the rate of the named variable, optionally raised to an elasticity.
`GrowthAs(Key\GDP, 0.9)`.

**GrowthFromYear**, **GrowthFromValue**, **AnnualGrowth**, **HistoricalGrowth** — see the help.

## Values of other cells, years, scenarios

**Value**(Year) or Value(Branch:Variable, Year) — the value in a given year.
**PrevYearValue** [(Branch:Variable)] — last year's value. `10 + PrevYearValue` adds 10 a year.
**LaggedValue**(Years) or LaggedValue(Branch:Variable, Years).
**BaseYearValue** [(Branch:Variable)].
**BaselineValue** [(Branch:Variable)] — the value in the baseline scenario (the one just below
Current Accounts that this scenario descends from). Not in Current Accounts or a baseline itself.
`BaselineValue * Interp(BaseYear, 1, EndYear, 1.5)`.
**ScenarioValue**(Scenario [, Year]) — the current cell in another scenario, by name or abbreviation.
**ScenarioValueOf**, **RegionValue**, **RegionValueOf** — another branch in another scenario or region.
**Parent** [(VariableName)] — the value at the parent branch.
**Sum** / **Total** — alone: sum of the neighboring branches (excluding this one). Sum(Branch:Variable
[, FirstYear] [, LastYear]) sums over years. **TotalChildren**, **MeanChildren**, **MaxChildren**.
**Share**(Branch:Variable) — that cell's percent share of its neighbors. Not of the current cell's
own neighbors (circular).
**Remainder**(Total) — Total minus the sum of the neighbors. In one neighbor only.
**CumulativeValue**, **ChangeIn** — see the help.

## Logic and arithmetic

**If**(Test1, Result1 [, Test2, Result2 ...], ResultIfAllFalse) — evaluated left to right.
`If(Year < 2005, 0, Year < 2010, 10, Year < 2020, 15, 20)`.
Operators: `+ - * / ^`, `= <> < > <= >=`, `And Or Not`. True is 1, false is 0.
**Constrain**(Value, Lower, Upper); **Min**, **Max**, **Abs**, **Round**, **Floor**, **Ceil**, **Int**,
**Sqrt**, **Ln**, **Log**, **Exp**.
**Lookup**(Linear|Step, Branch:Variable, IV1, DV1, IV2, DV2, ...) — table lookup on another
variable; independent values ascending. **StepLookup**.
**Between**, **InList**, **Choose** — see the help.

## Year words

`Year`, `BaseYear`, `FirstScenarioYear`, `LastHistoricalYear`, `EndYear`, `PrevYear`.

## Units and fuels

**ConvUnits**(From, To) — conversion factor between units of the same class.
`ConvUnits(GWh, GJ)` = 3600.
**ConvFuelUnits**(Fuel, From, To) — energy to mass or volume for a fuel.
Fuel properties at the current branch: **EnergyContent**, **CarbonContent**, **Density**,
**SulfurContent**, **MoistureContent**, **FractionOxidized**, and others.

## Links outside LEAP

**Excel**(FileName, Range) — a permanent link to one cell. The workbook must be saved on the user's
computer; the file path is as LEAP sees it.
Interp/Step/Data/Smooth/...(ExcelFile, Range [, GrowthRate]) — one contiguous range, two columns
(years, values) or two rows.
Interp/Step/Data/Smooth/...(ExcelFile, YearsRange, ValuesRange [, GrowthRate]) — two separate
ranges of equal size, one column or one row each. See SKILL.md section 10.
Interp(LCDS, DataSet [, Series] [, Dim1 [, Dim2]] [, ISO3] [, GrowthRate]) — the LEAP Cloud Data
Server. See SKILL.md section 11 and the leap-lcds skill.
**ReadFromExcel**(file, range) or (file, years, slices, values) — time-sliced data.
**ReadFromFile** — see the help.

## Not available through the assistant tools

**Call**(Script) — runs a user script. Expressions using it are refused by set_expression.

## Reserved words

Function names and scale words (Thousand, Million, Billion, Crore, Lakh, %) cannot be part of a
branch, fuel or region name. The full list is the help topic "Reserved Words".
