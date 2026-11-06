---
name: leap-user-variables
description: User variables in a LEAP area through the LEAP MCP tools: what a user variable (custom variable) is, how to add a variable and define its unit, scale, defaults and notes, variable visibility (by branch type, by position in the tree, by tags, by scenario), variable categories and how to color code variables, how user variables extend LEAP's standard calculations, their limits, and how to read them in the Analysis and Results views. Use when the user asks to add a variable, define a custom variable, wonders where to put my data, asks "key assumption or user variable", cannot see a user variable at a branch, wants to group or color code variables, or asks how to read a user variable's values. For tags themselves, see leap-tags-indicators.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: leap_status, get_area, get_branch, get_branches, find_branches, get_expression, get_values, set_expression, set_expressions, api_get, api_set, api_call, api_describe, show_in_leap, read_view, search_help, read_help_topic
  tested-on: "property names checked and skill tested read-only on Freedonia 2026-11-06"
  status: draft for review
---

# User variables

## 1. What a user variable is

LEAP gives every branch a fixed set of variables for its kind (Activity Level, Final Energy
Intensity, Exogenous Capacity and so on). A **user variable** is one the user adds beside them.
It appears as an extra tab in the Analysis view at the branches its visibility settings allow,
and like any variable it holds one expression per scenario and per region, inherits from
Current Accounts and the parent scenario, and may be referenced from other expressions
(`Branch:MyVariable`). It is a data variable: LEAP never uses it in its own calculations
unless a standard variable's expression refers to it.

A **Key Assumption** is different: it is a *branch* under the top-level Key Assumptions
category, with one value, meant for drivers shared across the tree (population, GDP).
A user variable is a *column* that exists at many branches at once, one value per branch
(help: User Variables; Key Assumptions). Section 8 says which to choose.

Help topic: `read_help_topic` `Supporting_Screens/User_Variables.htm`. Related:
`Supporting_Screens/Variable_Categories.htm`, `Wizards_and_Properties/Macrovariable_Properties_Wizard.htm`.
Everything that defines, changes or deletes a user variable changes the area and needs
"add and edit anything" access (`leap_status` → `assistantAccess`); reading needs none. Nothing
is saved until `save_area`, and only when the user agrees.

## 2. Defining one

On screen: **Analysis: User Variables** (or right-click a user variable tab in the Analysis
view: Add, Delete, Edit, Duplicate). The properties are:

| Group | Property | Notes |
|---|---|---|
| Basic | Name | follows the rules for branch names; unique among user variables, case ignored; a name made only of digits cannot be found by name |
| | Scale, Units | the scale is a power of ten; the unit is **text, for information only** (section 3) |
| | Category | one of LEAP's variable categories, or the user's own (section 5) |
| | Notes | a longer description, shown in a panel while the variable is edited |
| | Time-Sliced Variable | a value per time slice instead of one a year |
| | Intermediate Variable | hidden when the user chooses "No Intermediate Variables" under User Variables to Show |
| Defaults | Default Expressions | one for Current Accounts, one for scenarios; used wherever nothing is entered; a blank scenario default means the Current Accounts default |
| | Read-Only | the data cannot be edited in the Analysis view (useful when the default expression always calculates it) |
| Visibility | Scenario Visibility, Tag Visibility, Branch Visibility, Available On & Below Branch | section 4 |
| Min/Max | Min, Max | LEAP tests the data against them later; blank means no limit. Through the API, `Min` and `Max` mean nothing unless `HasMin` and `HasMax` are true: read those first |

When the user says "don't create anything" and only wants to know what to fill in, answer with
the fields in the screen's order, with the API property beside each:

- Basic: Name (`Name`), Scale (`Scale`), Units (`UnitStr`), Notes (`Notes`)
- Defaults: Current Accounts (`DefaultExpressionCurrentAccounts`), Scenarios
  (`DefaultExpressionScenarios`), Read-Only (`ReadOnlyCurrentAccounts`, `ReadOnlyScenarios`)
- Visibility: branch type (`BranchType`), top branch (`TopVisBranch`), on the branch
  (`OnBranch`), levels below (`VisibleLevelsBelow`), tags (no API member), scenarios
  (`VisibleCurrentAccounts`, `VisibleScenarios`)
- Min/Max: `HasMin`, `Min`, `HasMax`, `Max`

Through the API ("edit anything" access):

1. `api_call` `UserVariables.Add("Fleet Age", 0, "years")`: name, scale (0 none, -2 percent,
   3 thousand, 6 million, 9 billion, 12 trillion), unit text ("None" when empty). The new
   variable is visible **on every kind of branch at every level**, in Current Accounts and in
   the scenarios, default expressions 0, no minimum or maximum, its name as its notes, not
   time-sliced, not summable, not intermediate. LEAP switches to the Analysis view. The call
   fails when the name is empty, not legal or taken, the scale is not one of those numbers, or
   no more user variables can be added.
2. Narrow and describe it with `api_set` on `UserVariables("Fleet Age")`: `BranchType`,
   `TopVisBranch`, `OnBranch`, `VisibleLevelsBelow`, `VisibleCurrentAccounts`,
   `VisibleScenarios`, `DefaultExpressionCurrentAccounts`, `DefaultExpressionScenarios`,
   `ReadOnlyCurrentAccounts`, `ReadOnlyScenarios`, `TimeSliced`, `Intermediate`, `Summable`,
   `HasMin`, `Min`, `HasMax`, `Max`, `Notes`, `UnitStr`, `Scale`, `Name`. Every one is refused
   while LEAP is calculating or a supporting screen is open, and in an area whose changes
   cannot be saved. The two default expressions are not checked when set: read a value back.
3. Fill it at the branches: `set_expression` (or `set_expressions` for many branches) with the
   user variable's name as `variable`, in Current Accounts or a scenario, like any variable.
4. `api_get` `UserVariables("Fleet Age")` to confirm the definition; `api_describe` with
   `object` `UserVariable` or `UserVariables` lists every member with its help text.

Delete: `api_call` `UserVariables.Delete("Fleet Age")` removes the variable **and all its
data**, cannot be undone, and leaves expressions that refer to it unchanged (so broken). Only
when the user asks, and after naming what will be lost.

Not in the API: the variable's category and its Tag Visibility list (confirmed with
`api_describe`: no such members). Set those on the User Variables screen; say so.

## 3. Units and scales

- The unit is a **label**. The API help is explicit: "it is a label only: it is not a LEAPUnit
  and nothing is converted". The scale is only the power of ten LEAP shows with the data.
- Enter the data in one unit and scale everywhere the variable is used, and name them in the
  unit text and the notes ("Thousand TOE, from the national balance").
- A reference to a user variable (`Sector\Fuel:FuelUseHistorical`) gets the square brackets
  LEAP writes for any reference. Treat the value as being in the unit the data were entered
  in and convert in the expression yourself (`/ 1000`, `* 41.868`). Unverified: whether a unit
  text that happens to match a LEAP unit name (TOE, GJ) lets the brackets convert as they do
  for standard variables; do not rely on it.
- Percent data: scale -2 and shares written as 0 to 100, as LEAP's own share variables.

## 4. Visibility: where the variable appears

Four settings, all of which must allow a branch before the tab appears there:

| Setting | Screen | API | Meaning |
|---|---|---|---|
| Branch Visibility | one kind of branch | `BranchType`: -2 all branches, 10 Key Assumptions, 1 all Demand, 101 demand categories, 104 demand technologies, 108 demand aggregate intensity branches, 2 all Transformation, 102 modules, 103 processes, 107 outputs, 15 Resources, 34 effect branches, 25 Stock Changes, 24 Statistical Differences, 38 Indicators, 27 Non Energy Sector Effects, 26 Non Energy Sector categories | the kind of branch that shows it |
| Available On & Below Branch | a top branch, On, Below, levels | `TopVisBranch` (a branch object), `OnBranch` (true: the top branch itself shows it), `VisibleLevelsBelow` (-1 none, 0 every branch below, 1 to 6 only the branches exactly that many levels down) | the part of the tree |
| Tag Visibility | a list of tags | not in the API (screen only) | only branches carrying one of the tags; blank means any branch |
| Scenario Visibility | Current Accounts, Scenarios | `VisibleCurrentAccounts`, `VisibleScenarios` | both unchecked hides the variable; its data are kept |

Levels below count from the top branch. Transformation processes sit two levels below their
module (module \ Processes \ process), so a variable meant for processes with a module as its
top branch needs `VisibleLevelsBelow` 0 (all levels) or 2, never 1.

Scenario Visibility: uncheck Scenarios for values that cannot differ by scenario (a source
year, a data grade, a register value); keep both for inputs that scenarios may change.

Tag Visibility is what lets one variable appear in just the branches that need it, wherever
they sit: tag the plants whose capacity has a stated source, make `CapacitySource` visible
at the tag, and no other process shows the tab (tags: skill leap-tags-indicators). Check that
the tag exists first: `api_get` `Tags` lists tags; `api_get` `Branches("full name").Tags`
lists a branch's tags. If it does not exist, the user creates it (Tags menu, Alt+T) and tags
the branches before the variable is useful.

Consequences for the tools:

- `get_branch` lists a user variable among the branch's data variables **only where it is
  visible**, and it lists the variables for the scenario named in the call (`variablesFor` in
  the answer; without `scenario`, the one selected in LEAP). A variable visible in Current
  Accounts only is found by `get_branch`, `get_expression` and `get_values` with scenario
  "Current Accounts", whatever LEAP's screen shows; asked for it in another scenario, the tool
  refuses and says where the variable exists. `api_get` `UserVariables("name")` gives the
  definition.
- `set_expression` at a branch where the variable is not visible is refused or writes nothing
  useful: check the four settings before writing, and before adding a second variable because
  the first "is missing".
- `api_set` `TopVisBranch` takes a branch object; whether `api_set` accepts a branch path
  such as `Branches("Demand\Transport")` is unverified. If it refuses, say so and ask the user
  to set the top branch on the screen.
- Changing `BranchType`, `TopVisBranch`, `VisibleLevelsBelow`, `OnBranch`, `Scale`, the
  defaults, the limits or time slicing marks results out of date.

## 5. Variable categories and colors

Screen: **Analysis: Variables: Variable Categories** (also a toolbar button on the User
Variables screen). The list can be viewed, edited and reordered, and each category has a
color; **the tabs of every variable in the category are drawn in that color** in the Analysis
view, so a user's own variables stand out from LEAP's. LEAP's built-in variables are
pre-assigned to default categories with gray tabs, which cannot be changed or recolored. In
the Analysis view the variable menu button can show only one category of variables (all cost
variables, all dispatch variables, one user category), so a category is also a filter.

The category of a user variable is set in the Category box on the User Variables screen. It is
not reachable through the API (no member on `UserVariable`, none found on the LEAP object):
describe what to do, do not try `api_set`. The colors offered are a small fixed palette (none,
blue, green, orange, red and a few more; unverified beyond those named).

## 6. What user variables are for

| Use | Pattern |
|---|---|
| Historical energy-balance series per fuel | `FuelUseHistorical` at demand technologies, Current Accounts only, `Interp(2010, 120, ..., 2022, 150)`; see skill leap-demand-structures section 3 |
| Sums for the parent | `HistTotalEnergy` at categories: `TotalChildren(FuelUseHistorical)` |
| Calibration factors and indices | `CalibFactor` default 1, used as `... * CalibFactor` in the standard variable; `Index2020` = value / `BaseYearValue` |
| An input to a standard variable | `Final Energy Intensity` written as `HistTotalEnergy / Total Activity`, or `Fuel Share` as `100 * FuelUseHistorical / Parent:HistTotalEnergy` |
| A per-scenario switch | `PolicyOn` default 0, set to 1 in the policy scenario; standard variable `If(PolicyOn = 1, a, b)` |
| A branch parameter LEAP lacks | fleet age, plant commissioning year, a data-quality grade, a stated capacity source |
| Comparing with a standard variable | a read-only, Intermediate helper such as `CapacityGap` with default expression `Exogenous Capacity - RegisterCapacity` and the same visibility as the input |
| Helpers inside Indicator branches | the help: normalizing and weighting variables compared across regions or scenarios |
| Documentation | the variable's Notes name the source; the branch's `set_notes` names the edition and unit |

A user variable changes a result only through such a reference. If the user expects demand or
supply to move after filling one in, find the standard variable that should refer to it.

## 7. Limits

- **400 user variables per area** (help: "up to 400"; source: `NumUserVarIDs = 400` in
  LEAP2000.INC; the source also disables the Add button at that count, not checked at run
  time). `UserVariables.Add` fails
  with "no more user variables can be added".
- Not used by LEAP's calculations unless referenced (section 6).
- One value a year unless Time-Sliced Variable is checked (`TimeSliced`); then a value per
  time slice (help and API agree).
- Renaming: the name may be changed on the screen or with `api_set` `Name` (spaces at the
  ends removed; a change of capitals only counts). References in expressions are stored
  internally by variable ID, so they follow the new name when shown (from the source;
  unverified in a live test; check one referring expression with `get_expression` after a
  rename). Deleting leaves references broken (API help).
- Default expressions are not checked when set; a wrong default shows up only as an error at
  the branch or in a calculation.
- Summable (`Summable`) decides whether values may be summed across branches so that charts
  stack them; a new variable from `UserVariables.Add` is not summable.
- Category and Tag Visibility: screen only (sections 2 and 5).

## 8. Key Assumption or user variable?

| Choose a Key Assumption branch when | Choose a user variable when |
|---|---|
| the value is a driver shared across the tree (population, GDP, prices, a carbon price) | the value belongs to one branch and differs branch by branch (each fuel's historical use, each plant's stated capacity source, each technology's fleet age) |
| the scenario storyline is told through it ("GDP grows 4%") | it is a helper calculation that sits beside the branch's own variables |
| the user wants the data visible in one place, under one category, with a tree of their own | its visibility should follow branch type, part of the tree or tags |
| many branches reference it | only the branch's own variables (or a parent's sum) reference it |
| the user wants it under Key Assumptions in the Results view's Data variables list | a per-scenario switch or calibration factor |

Both are the user's own variables; neither drives anything until referenced. When in doubt,
ask "one value, or one per branch?": one value is a Key Assumption.

## 9. Reading them

- **Analysis view**: a tab beside the standard variables, in the category's color. `get_branch`
  (with `scenario`) lists it among the data variables with its unit and expression;
  `get_expression` gives the expression and where it is inherited from; `get_values` gives
  the numbers by year. Section 4 says where it is visible and which scenario to name.
- **Results view**: the help topic says user variables "cannot currently be reported in the
  Result Views". The program is further on: the Results view's variable menu has a **Data
  variables** entry listing the data variables of the selected branch and of the branches
  below it, user variables under their own names, Key Assumptions and Indicators under the
  branch name; a user variable charted there stacks across branches only if it is Summable
  (from the source, 2026-10; not tested live, and `show_in_leap` may not take a data variable
  as `result_variable`: try, read the answer, and fall back to `get_values`). Say to the user
  that the help lags the program here.
- Through `api_get`: `UserVariables` (count and names with IDs), `UserVariables("name")` (every
  property; `TopVisBranch` is listed under `leadToObjects`, read it with
  `UserVariables("name").TopVisBranch` to get the branch's `FullName`),
  `Branches("...").Variables("name").Expression` (the expression for the scenario selected on
  LEAP's screen; for a named scenario use `get_expression` with its `scenario` argument).

## Common mistakes

- Reporting a user variable "missing" without checking `BranchType`, `TopVisBranch`,
  `OnBranch`, `VisibleLevelsBelow`, Tag Visibility and the scenario visibility, and without
  naming the scenario it is visible in.
- Treating the unit as converted: it is a label. Doing the arithmetic in two units.
- Adding with `UserVariables.Add` and leaving it visible everywhere: a tab of noise at every
  branch; narrow it at once.
- A default expression of 0 where a factor of 1 is meant (calibration factors, switches).
- Expecting results to change after filling a user variable that nothing references.
- Deleting a user variable to "clean up" without listing the expressions that refer to it.
- Promising to set the category, the color or the Tag Visibility through the API.
- Two user variables for one quantity because the first was visible in Current Accounts only
  and `get_branch` was called with another scenario.

## Example on Freedonia (illustrative; the second part is not yet run)

Freedonia has one user variable, **Livestock** (checked 2026-11-06 with `api_get`):

- `api_get` `UserVariables` → Count 1, item id 1538 "Livestock".
- `api_get` `UserVariables("Livestock")` → Scale 0, UnitStr "head", BranchType 26 (Non
  Energy Sector categories), OnBranch true, VisibleLevelsBelow -1, VisibleCurrentAccounts and
  VisibleScenarios true, DefaultExpressionCurrentAccounts "0", Summable true, TimeSliced
  false, Notes "Number of livestock head, all animal types."
- `api_get` `UserVariables("Livestock").TopVisBranch` → `Non Energy\Agriculture and Other
  Land Use\Livestock`. So the tab shows at that one category branch and nowhere else.
- `get_branch` `Non Energy\Agriculture and Other Land Use\Livestock` with scenario Current
  Accounts → data variable "Livestock", unit head, expression `65 Million`, followed by the
  branch's result variables. Below it, the `Manure Management` branches can refer to it as
  `Non Energy\Agriculture and Other Land Use\Livestock:Livestock` so the herd is entered once.

Planned pattern, user asks: "I have the energy balance for 2015 to 2022 by fuel for Industry;
keep it in the model and calibrate the base year to it."

1. `leap_status` → access "add and edit anything"; otherwise explain the screen route.
2. `api_call` `UserVariables.Add("FuelUseHistorical", 3, "Thousand TOE")`. Then `api_set`
   `BranchType` 104 (demand technologies), `TopVisBranch` the Industry branch (path from
   `find_branches` "Industry"; if `api_set` refuses an object, ask the user to pick the top
   branch on the User Variables screen), `OnBranch` false, `VisibleLevelsBelow` 0,
   `VisibleScenarios` false, `Summable` true, `Notes` "National energy balance 2015-2022,
   thousand TOE".
3. `set_expressions` with scenario Current Accounts (the only scenario the variable is visible
   in) at each fuel technology under Industry: `Interp(2015, 120, 2016, 124, ..., 2022, 150)`.
4. `api_call` `UserVariables.Add("HistTotalEnergy", 3, "Thousand TOE")`, `BranchType` 101,
   same top branch, `OnBranch` true, `DefaultExpressionCurrentAccounts`
   `TotalChildren(FuelUseHistorical)`, `ReadOnlyCurrentAccounts` true, `Intermediate` true.
5. At the Industry category: `Final Energy Intensity` = `HistTotalEnergy / Total Activity`
   (units as `get_branch` shows them); at each technology `Fuel Share` =
   `100 * FuelUseHistorical / Parent:HistTotalEnergy`, one of them `Remainder(100)`.
6. `get_values` on `HistTotalEnergy` and on the branch's Final Energy Demand for the base
   year; they should match the balance. Report what was added (two user variables, visible
   under Industry only), that the area is not saved, and that the category and color can be
   set on the Variable Categories screen.
