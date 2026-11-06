---
name: leap-load-shapes
description: Understand, read or change how a LEAP model varies within a year through the LEAP MCP tools. Use when the user mentions a load shape, load curve, load duration curve, time slices, seasons or hourly or daily periods, peak load, load factor, a yearly shape, dispatch by time slice, capacity factor or availability by season, or asks why a plant's output or a fuel's demand looks the same in every slice. Covers the time slices of an area and what they cost in calculation time, the three kinds of shape (a fuel's System Load Shape, the Load Shape at demand branches, named yearly shapes), the functions that set them, how dispatch and the reserve margin use the shape, time-sliced results, LEAP's shape diagnostics, and the API for slices and shapes.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: leap_status, get_area, get_branch, get_branches, find_branches, get_expression, get_values, set_expression, api_get, api_set, api_call, api_describe, show_in_leap, read_view, search_help, read_help_topic
  tested-on: "a 96-time-slice single-region model, LEAP 2026.9.0.18, 2026-11-06 (read-only)"
  status: draft for review
---

# Time slices and load shapes in LEAP

Most of LEAP works in annual totals. Time slices divide each year into parts (seasons, kinds of
day, times of day) so that electricity demand, plant availability and dispatch can differ within
the year. A shape says how a value is spread over those slices. The help topics "Time Slices",
"Yearly Shapes", "System Load Shape", "Load Shape" (Demand) and "Dispatching Processes on a Load
Curve" are the references; read the topic (`read_help_topic`) before explaining a variable.

## Time slices

- One set of time slices per area, the same in every year. LEAP assumes 8760 hours a year, no
  leap years, every year starting on a Monday. The hours of all slices must add up to 8760.
- Set up on the **General: Time Slices** screen, normally with its Setup wizard: either a
  **simple** split (a set number of slices of a given length, enough for a load duration curve) or
  a **detailed** one built from seasonal or monthly groups, weekday/weekend groups and time-of-day
  groups. The **Time Slice Settings** screen (from that screen's toolbar) holds the season dates,
  weekend days and day/night hours; changing it means setting the slices up again, which erases
  every yearly shape.
- An area with no slices of its own has one built-in slice, "Whole Year", 8760 hours.
- Each slice has a Name, Hours, CumulativeHours (hours of this slice and all before it), an
  Abbreviation, Notes and a Dispatch Period 1 to 4 (unverified beyond the API text: each dispatch
  period has its own availability and merit order values for dispatch).
- Cost: calculation time and memory grow with the number of slices, because every time-sliced
  variable is evaluated and stored once per slice, and the dispatch runs per slice. LEAP warns when
  a configuration gives a very large number of slices; 32-bit LEAP can run out of memory. Suggest
  the fewest slices that still show the variation the question needs (two seasons by day/night is
  four slices; twelve months by weekday/weekend by four hourly periods is 96).
- Read them with `api_get` `TimeSlices.Count`, `TimeSlices(1).Name`, `TimeSlices(1).Hours`,
  `TimeSlices(1).CumulativeHours`, `TimeSlices(1).DispatchPeriod`. Check the hours sum to 8760
  yourself: LEAP's API does not.

## Where shapes are switched on

- **Settings: Scope & Scale**, option Load Shapes: off, all fuels, or selected fuels. With
  "selected", the Has Load Shape column of the **General: Fuels** screen says which fuels. A fuel
  without a load shape is not time sliced at all.
- When on, a top-level **Load Shapes** branch follows Demand in the tree, with one branch per
  fuel carrying the **System Load Shape** variable. `get_branch` reads `Load Shapes` itself (by
  full name or its ID, -8) and lists the fuel branches as its children; then `get_branch` on each
  `Load Shapes\<fuel>`. `find_branches` "Load Shape" finds them too. Whether the option is on is read from the tree (the branch exists) and
  from which fuels have a branch; there is no area setting for it that `api_get` can read.
- `get_branch` lists the variables the branch has in the scenario you name (its `variablesFor`
  field says which one; without a scenario it is the one selected in LEAP). Dispatch Rule, Merit
  Order, First Simulation Year and Historical Production exist only in simulated scenarios: name
  a simulated scenario to see them even while an optimization scenario is on the user's screen.

## The three kinds of shape

| Kind | Where | What it is |
|---|---|---|
| Yearly shape | General: Yearly Shapes screen (a library, not a branch) | A named set of values, one per time slice. Four types: Energy Load Shape (% of annual energy), Peak Load Shape (% of peak), Availability (% available), Merit Order (integers). Optimization needs load shapes as % of energy. |
| System Load Shape | `Load Shapes\<fuel>`, variable System Load Shape | The shape of the whole system's demand for that fuel, used for peak load, load factor, reserve margin and dispatch. Set by a function (below). |
| Load Shape at a demand branch | A demand technology, or a category with a useful energy intensity | The shape of one device's load. Visible only when the fuel's System Load Shape is ShapeFromDemand; otherwise LEAP ignores it. |

Other time-sliced variables take yearly shapes too: Maximum Availability and Merit Order at
Transformation processes (a hydro plant base load in the wet season, peaking in the dry), and the
time-sliced demand methods. Peak Load Ratio at a module links to a shape through
PeakLoadRatioFromYearlyShape.

## Functions that set a shape

| Function | Allowed at | Meaning |
|---|---|---|
| `ShapeFromDemand` | System Load Shape only | Build the fuel's shape by summing the Load Shape of every demand branch using the fuel. |
| `ShapeNone` | System Load Shape only | No time slicing for this fuel: its demand and exports go to the annual calculations. Not allowed at a demand branch. |
| `ShapeFlat` | System or demand Load Shape | Equal peak load in every slice. |
| `ShapeEqualEnergy` | System or demand Load Shape | Equal energy in every slice (unusual; ShapeFlat is normally wanted). |
| `ShapeDefault` | System or demand Load Shape | The first shape in the Yearly Shapes library by its Order (`api_get` `YearlyShapes(i).Order` = 0), which need not be index 1. Confirm which shape is in use by checking one slice's value against Power Requirements ÷ Requirements in that slice. |
| `YearlyShape(name)`, `YearlyShape(base, end)`, `YearlyShape(base, last historical, end)` | Any time-sliced variable | A named yearly shape; with two or three names LEAP interpolates slice by slice between the years. One name in a scenario is the end-year shape, interpolated from the Current Accounts shape. |
| `InterpYearlyShape(y1, s1, y2, s2, ...)` / `InterpYearlyShapeNIV(...)` | Any time-sliced variable | Up to ten year/shape pairs. The NIV form does not take the base-year shape from Current Accounts. |
| `TimeSliceValue(slice, v, ..., else)`, `TimeSliceGroupValue(group, v, ..., else)` | Any time-sliced variable | Values typed per slice or per group. |
| `SeasonalValue`, `DailyValue`, `HourlyValue`, `IsSeasonalGrouping(name)`, `IsDailyGrouping`, `IsHourlyGrouping`, `SeasonID`, `DayID`, `HourID` | Any time-sliced variable, when the area has that grouping | Values or tests by season, day type or hourly period, for formulas. |
| `TimeSliceHours`, `TimeSliceCumulativeHours`, `TS` | Any time-sliced variable | Hours, cumulative hours and index of the slice being evaluated. |
| `MaxTimeSlice(Branch:Variable)`, `MinTimeSlice(...)` | Any variable | The largest or smallest slice value of a time-sliced variable in each year. |
| `ReadFromExcel(file, range)` or `(file, years, slices, values)` | Time-sliced variables | Reads years, slice names and values from a workbook; missing years are interpolated. |

Using a yearly-shape function on a variable that is not time sliced is an error.

### The hard rule about ShapeFromDemand

`ShapeFromDemand` is a value for the **System Load Shape of a fuel**, under the Load Shapes
branch, and nothing else. Never write it, or offer it, at a demand branch's Load Shape, a useful
energy category or an export load shape. Say "the fuel must take its system load shape from
demand", not "set the branch to ShapeFromDemand". The presence of ShapeFromDemand on the fuel is
what makes the Load Shape variable appear at the demand branches that use it and what lets their
shapes count. In a multi-region area a fuel that uses it must use it in every calculated region
of the scenario.

## How dispatch and capacity use the shape

- Before the First Simulation Year, processes follow Historical Production. From then on the
  Dispatch Rule applies. **MeritOrderDispatch** and **RunningCost** dispatch on the load curve:
  LEAP sorts processes by Merit Order (or by variable plus fuel cost), cuts the load curve built
  from the System Load Shape into strips, and fills the strips from the bottom with each group's
  available capacity (Capacity x Maximum Availability), base load first, peaking plants last.
  Groups with equal merit order share in proportion to available capacity. **PercentShare**,
  **ProportionalToCapacity** and **FullCapacity** work on annual energy only; the shape does not
  change their output.
- Peak load on a module comes from its energy requirements and the load factor of the shape
  (the mean height of the load curve). **Peak Load Ratio** (0 to 100%) at the module corrects for
  the peak that a coarse set of slices misses; `PeakLoadRatioFromYearlyShape(name)` takes the
  value LEAP recorded when the shape was imported from 8760 hourly values.
- **Planning Reserve Margin (%) = 100 x (Module Capacity - Peak Load) / Peak Load**, with Module
  Capacity the sum of Capacity x Capacity Credit. Endogenous capacity is added to keep it. A
  flatter shape lowers the peak, so fewer plants are built; a flat shape makes peaking plants
  unnecessary.
- Maximum Availability and Merit Order may be yearly shapes, so a plant can be available or
  ranked differently by season.
- Under optimization (NEMO) the slices are the model's time structure; shapes must be % of
  energy, and storage processes only act there (Full Load Hours is their storage duration).

## Reading shapes and time-sliced results

**Reading a shape fast.** `api_get` `YearlyShapes("name")` returns the whole object, and its Notes
usually carry the shape's type, source file, the slice configuration it was imported under and the
hourly load factor. Compare that hourly load factor with the sliced curve's (Requirements ÷ peak):
averaging each hour over a season flattens the peak, so the sliced value is higher, and Peak Load
Ratio is what corrects it. The peak slice is the slice with the largest shape value, and Peak Power
Requirements equals Power Requirements in that slice: a way to verify the peak without a chart.

**Many slices.** With dozens or hundreds of slices do not read them one by one: `api_get`
`TimeSlices` for the count and names, `TimeSlices(1)`, the last one (its CumulativeHours is the
total), and one at each suspected group boundary; state the grouping from the names (for example
four seasons × 24 hours).

Inputs: `get_expression` on System Load Shape or a demand Load Shape gives the function;
`api_get` `YearlyShapes("name").Value("slice name")` gives one slice's value, and
`YearlyShapes("name").ProfileTypeDescription` says which of the four types it is. `get_values`
with `filter` `Time Slice=<name>` reads one slice of a time-sliced variable (unverified for input
variables; the tool description names the filter for results).

Results (variable names as `get_branch` lists them; the display names below are from the help):

| Display name | At | Note |
|---|---|---|
| Energy Load Shape | Demand branches | Energy per slice; slices add to annual consumption. Only when the fuel is ShapeFromDemand. |
| Power Load Shape | Demand branches | The same as a rate (power units); no "All Time Slices" because rates do not add. |
| Peak Power Requirements | Module | Peak load in the year, power units; needs capacity data at the module. |
| Load Factor | Module | Output / (Capacity x 8760), in %. Read it, Reserve Margin, Planning Reserve Margin and Maximum or Actual Availability with `get_values` and no `unit`: the answer is a percentage with unit `Percent`. The shape's own load factor (a different number) is Requirements (GWh) ÷ (Peak Power Requirements (MW) × 8.76), and Capacity ÷ Peak is the margin before capacity credits; both help explain the result. |
| Power Requirements | Module and processes | Dispatch per slice in power units; stack processes by merit order. |
| Energy Generation | Module and processes | The dispatch in energy units; slices add. |
| Inputs Time Sliced | Module | Fuel drawn per slice; follows Energy Generation; only for modules that dispatch by slice. |
| Primary Requirements Timesliced | Resources | Primary energy per slice; demand part follows the fuel's system load shape, Transformation part follows the plants. |

To show the profile in LEAP: `show_in_leap` with `view` Results, the branch and variable,
`x_axis` `Years & Time Slices` (or `Time Slices` alone for one year; `Scenarios & Time Slices`
and `Regions & Time Slices` also work), `legend` Branches, `select` `Time Slices=<names or
All>; Scenarios=...`, then `read_view` to confirm. A time-sliced result (Energy Generation,
Power Generation, Power Requirements, Curtailed Energy or Power Production, Inputs Time Sliced,
the load shapes) must have time slices on the X axis: with Years alone the tool refuses and
points to `Outputs by Output Fuel` for yearly generation. To show one process by itself, name
it as `branch` only for a result that is not stacked (Actual Availability, Capacity Factor); for
a stacked result put Branches on the `legend` or `x_axis` and `select` `Branches=<name>`. For a
chart in the conversation, draw it from `get_values` numbers and name the scenario, year and
unit.

## Diagnostics LEAP gives about shapes

After a calculation the Diagnostics tab in LEAP (the user opens it; say where it is) lists
Load Shape Checks:

- A demand device's slices were ignored because its fuel has a system-wide shape (not
  ShapeFromDemand): LEAP spread the device's annual total with the system shape. Remedy: set
  the fuel's System Load Shape to ShapeFromDemand, if device shapes are meant to count.
- A useful energy category's Load Shape conflicts with a fixed system shape of a fuel below it;
  LEAP names the fuels. Under optimization both profiles become constraints and the optimizer
  can only meet both by producing more useful energy than demanded, so act on it there.
- Calculation error "System Yearly Shape load fractions sum to 0.0000": a shape with no values,
  usually after time slices were changed (see below).

## Changing slices and shapes

Everything in this section needs "edit anything" access and is refused while LEAP calculates,
while a supporting screen is open, and in an area that cannot be saved. Prefer the user doing
slice setup on the Time Slices screen; the API is for scripted builds.

- A shape expression: `set_expression` on System Load Shape, a demand Load Shape, Maximum
  Availability or Merit Order, for example `YearlyShape(SystemShape)` in Current Accounts and
  `YearlyShape(Flatter)` in the scenario (read as end-year shape, interpolated from the base).
- A new yearly shape: `api_call` `YearlyShapes.Add("name", type)` (type 0 energy, 1 peak,
  2 availability, 3 merit order; default 0). It starts with 100 / number of slices in every slice,
  not weighted by hours, so set every value: `api_set` `YearlyShapes("name").Value("slice")`.
  Negative values are refused; values above 100 are not. `YearlyShapes.Delete` refuses while any
  expression uses the shape. Renaming keeps expressions valid (they store the ID).
- Time slices: `api_call` `TimeSlices.Add("name", hours)` (whole hours 1 to 8760, appended, dispatch
  period 1; in an area with only "Whole Year" it replaces that slice), `TimeSlices.Delete(name)`,
  `api_set` `TimeSlices(n).Hours`, `.Name`, `.Order`, `.DispatchPeriod`. `api_describe` with
  `TimeSlices(1)` or `YearlyShapes(1)` lists every member.
- **Warning: adding or deleting a time slice rebuilds every yearly shape** from its imported
  hourly data where it has any, and otherwise **erases its values**, exactly as the Time Slices
  screen does. A system load shape of zeros then fails every calculation with "System Yearly
  Shape load fractions sum to 0.0000", and a save (including `save_version`) writes the damage to
  disk. Before touching slices: record every `YearlyShapes(i).Value(slice)`; after: create all
  slices first, then restore or re-enter the shapes. Say this to the user before starting.
- The obsolete slice members (BeginHour, EndHour, BeginDate, EndDate, Monday..Sunday) answer 0,
  empty or false; use Hours and CumulativeHours.

## Common mistakes

- Writing ShapeFromDemand at a demand branch, or ShapeNone at a demand Load Shape.
- Entering a device Load Shape while the fuel's System Load Shape is a fixed shape, and expecting
  dispatch to change (it is ignored; Diagnostics says so).
- Expecting a PercentShare or ProportionalToCapacity module to react to a new load shape.
- A peak shape where optimization needs an energy shape.
- Reading a Power result as if slices add; they do not (use the energy result).
- Adding slices to an area that already has yearly shapes without saving the shape values first.
- Proposing many slices "for accuracy" without saying what it does to calculation time.
- Mixing up the Load Factor result (capacity use) with the load factor of the shape (mean height
  of the load curve); the help uses both words.

## Example (illustrative; not run against the sample area)

User: "Show me Freedonia's electricity load shape and tell me what a flatter curve would do to
new capacity."

1. `leap_status`, `get_area`. `api_get` `TimeSlices.Count` → 9; `TimeSlices(1).Name` → "Hours
   0000 to 1000" ... `TimeSlices(9).Name` → "Hours 8000 to 8760": a simple load duration curve,
   no seasons or day types (so SeasonalValue and the like do not apply). `api_get`
   `YearlyShapes.Count` → 1, `YearlyShapes(1).Name` → "SystemShape".
2. `find_branches` "Load Shape" → the fuels with shapes; `get_expression`
   `Load Shapes\Electricity`, System Load Shape, Current Accounts → expected `YearlyShape(SystemShape)`
   (unverified). `api_get` `YearlyShapes("SystemShape").Value("Hours 0000 to 1000")` and the other
   slices → the curve, highest first.
3. `get_branch` `Transformation\Electricity Generation` → Planning Reserve Margin, Peak Load Ratio;
   processes with Dispatch Rule MeritOrderDispatch (unverified). `get_values` Power Requirements
   at the module, scenario Baseline, year 2030, `filter` `Time Slice=Hours 0000 to 1000` and the
   last slice → peak and base load. `show_in_leap` Results, Electricity Generation, Power
   Requirements, `x_axis` `Time Slices`, `legend` Branches, `select` `Scenarios=Baseline`;
   `read_view`.
4. The change (with the user's agreement and "edit anything" access): `api_call`
   `YearlyShapes.Add("Flatter", 0)`, `api_set` each `YearlyShapes("Flatter").Value(slice)` to a
   less peaked set summing to 100; in a new scenario, `set_expression` System Load Shape
   `YearlyShape(Flatter)` (end-year shape, interpolated from SystemShape). `calculate`.
5. `get_values` Peak Power Requirements and Capacity at the module and `Capacity Added` at the
   candidate processes, and `Reserve Margin` at the module (no `unit`; answered in Percent), both
   scenarios, 2030 and 2040; report the lower peak and the capacity LEAP no longer adds, with
   units.
