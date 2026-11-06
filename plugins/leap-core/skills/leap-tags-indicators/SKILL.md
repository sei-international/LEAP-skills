---
name: leap-tags-indicators
description: Custom groupings and custom reporting in a LEAP area through the LEAP MCP tools: tags on branches, tag groups, tag filters in expressions and results, indicator branches and user variables. Use when the user wants to tag or label branches, group technologies (clean, efficient, renewable, existing versus new), report a sector or a set of technologies that is spread across the tree, build an indicator (per capita, intensity indicator, share of renewables, an NDC or SDG target), or add a user variable (custom variable) to branches; or asks what a tag, a tag group, an indicator branch or a user variable is and how to read one.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: leap_status, get_area, get_branch, get_branches, find_branches, get_expression, get_values, set_expression, set_expressions, api_get, api_set, api_call, api_describe, show_in_leap, read_view, search_help, read_help_topic
  tested-on: "Freedonia, LEAP 2026.9.0.18, 2026-11-06 (read-only)"
  status: draft for review
---

# Tags, indicators and user variables

The tree organizes a model into folders: one place for each branch. Three tools let the user
group and report across that structure:

- **Tags** are labels on branches. A branch may carry several; tags may be sorted into **tag
  groups**. They filter references, results and the visibility of user variables.
- **Indicator branches** hold extra, user-defined results (ratios, per-capita values, shares),
  calculated after the main calculation under the top-level Indicators branch.
- **User variables** are extra data variables the user defines, shown as tabs beside the
  standard variables on the kinds of branches, or the tagged branches, the user chooses.

Everything that creates or changes one of these changes the area and needs the user's
"add and edit anything" access (`leap_status` → `assistantAccess`). Reading needs no access.
Where this skill says "unverified", the help and the API reference did not confirm the detail:
check it with `api_describe` or `read_help_topic` before relying on it.

## 1. Tags

### What they are

A tag is a name that follows the rules for branch names, with an optional description, a color
(None, Blue, Green, Orange, Purple) and at most one tag group. The help's own cases: power plants
in one long list tagged Thermal, Renewable or Nuclear, Existing or New, Specific or Generic;
cooking technologies tagged "clean". A branch may carry any number of tags, but for results
reporting **a branch must carry only one tag from any one tag group**.

In LEAP the user tags branches with the tag toolbar in the Analysis view (type names separated
by commas, Add, Delete, the Tag Painter), and organizes tags on the Manage Tags screen (Alt+T)
and the Tag Groups screen. Tag Settings decide whether a new tag is added to or replaces the
branch's tags, and whether it goes to the branch alone or to all branches below it.

### Reading tags through the API

- All tags in the area: `api_get` `Tags` (a collection; `Tags.Count`, `Tags("clean").Description`,
  `Tags("clean").TagGroup`, `Tags("clean").Color`, `Tags("clean").ID`).
- The branches that carry a tag: `api_get` `Tags("clean").Branches` (a branch collection; each
  item's `FullName`).
- The tags at one branch: `api_get` `Branches("Demand\Household\Urban\Electrified\Cooking\LPG").Tags`.
  `get_branch` does not report tags, so this is the way to see them.
- Tag groups: `api_get` `TagGroups`, `TagGroups("Cooking").Tags`, `TagGroups("Cooking").UseInResults`
  (whether the group is a dimension in the Results view).
- `api_describe` on `Tags`, `Tag`, `TagGroups`, `TagGroup` and `Branches` lists every member.

### Setting tags through the API ("edit anything" access)

- A new tag that belongs to no branch yet: `api_call` `Tags.Add("clean")`. It fails if the name is
  blank, not a legal name or already in use; check `Tags.Exists("clean")` first.
- Tag a branch: `api_call` `Branches("...\Cooking\LPG").Tags.Add("clean")`. A name LEAP does not
  know is created in the area as well; a tag already at the branch is left alone. A second
  argument `true` also tags every branch below (`Tags.Add("clean", true)`).
- Remove a tag from one branch: `api_call` `Branches("...").Tags.Delete("clean")` (with `true` as a
  second argument, from the branches below too). The tag stays in the area.
- Delete a tag everywhere: `api_call` `Tags.Delete("clean")` removes it from every branch and from
  every user variable's visibility list. Ask before doing this.
- A group: `api_call` `TagGroups.Add("Cooking")` (new groups are used in the Results view), then
  set `Tags("clean").TagGroup`. `api_describe` confirms it is writable, takes a LEAPTagGroup
  object, and nil clears it (unverified: whether `api_set`'s text form accepts an object path
  such as `TagGroups("Cooking")`). `api_set` also takes `Tags("clean").Description` and
  `Tags("clean").Color`.
- `Branch.AddTag` and `Branch.RemoveTag` are older members, hidden from the Script Editor; use
  `Branch.Tags.Add` and `Branch.Tags.Delete`.

All of these are refused while LEAP is calculating, while a supporting screen is open, and in an
area whose changes cannot be saved. Tags are saved with the area (`save_area` when the user agrees).

## 2. Tag filters in references and results

Three places take a tag filter, with different rules:

| Where | Syntax | Operators |
|---|---|---|
| Reference to a **data** variable in an expression | `Demand\Household:Total Activity[Household, Tag=clean]` | `Tag=` only. `Tag<>` is not supported. No other filter dimension. |
| Reference to a **result** variable in an expression | `Freedonia:One_Hundred Year GWP Direct At Point of Emissions[Tonne, Fuel=Gasoline]`; up to two filters among fuel, cost, time slice, effect, balance category, module cost category or tag | `=` and `<>` |
| `get_values` `filter` on a result variable | `Tag=clean`, up to three parts joined by `\|` | written "as in a result reference" (the help allows `=` and `<>`; `Tag<>` here is unverified) |

The data-variable filter limits the branches summed: a reference to a higher-level branch adds
the variable over all branches below it, and `Tag=clean` keeps only the tagged ones. That is how
the help counts households using clean cooking fuels. A tag filter on a lower branch counts only
below it, so the same count can be split by sub-tree:
`Demand\Household\Urban:Total Activity[Thousand Household, Tag=clean]` and the same for `Rural`
("Thousand Household" is a rescale of the variable's own unit, Household). Result references in an
ordinary data variable must be lagged (`PrevYearValue(...)`); an indicator branch may use the
present year (section 4).

The GWP result's name is read from `get_branch` on the area root (its full name is the area's
name), for example `One_Hundred Year GWP Direct At Point of Emissions`. There are 20, 100 and 500
year horizons and "Allocated to Demands" variants, so say which one was used.

In the Results view each tag group whose Use For Results box is checked is a dimension named
after the group. With `show_in_leap`, `view` Results: put the group's name on `x_axis` or
`legend`, or use it in `select` (`Cooking=clean`); the tool's answer lists the dimensions it
accepts, so read it rather than guess (unverified: whether a tag group is accepted on `select`).
A branch with no tag from the group, or with two, is not reported correctly in that dimension.
`select` `Branches=Road, Rail*` is a **name** filter on branches, not a tag filter; it helps when
the grouping the user wants matches branch names rather than tags. The help topic "Using Tags in
Results View" is still marked under development.

## 3. Tag functions in expressions

For an expression that behaves differently at tagged branches (a user variable with one default
expression used at many branches, an efficiency bonus only at efficient technologies):

| Function | Returns |
|---|---|
| `HasTag(clean)` | 1 if the current branch carries the tag, else 0 |
| `HasTag(Branch:Variable, clean)` | the same for another branch. The help's syntax line and its example disagree on the argument order (the example writes the tag first: `HasTag(Thermal, Transformation\Electricity Generation\Coal:Exogenous Capacity)`); the order is unverified, so test it on one branch before relying on it |
| `AnyBranchTags(Thermal, CombinedCycle)` | 1 if the branch carries any of the tags |
| `AllBranchTags(Thermal, CombinedCycle)` | 1 if it carries all of them |
| `NumBranchTags` | the number of tags at the current branch |
| `TagID(My Tag)` | the tag's ID, for passing to a script or DLL |

Typical form: `If(HasTag(efficient), BaselineValue * 0.9, BaselineValue)`. Tag names go in
without quotation marks. Read each topic with `read_help_topic` before use (section Expressions:
HasTag, AnyBranchTags, AllBranchTags, NumBranchTags, TagID). The topics behind this skill:
`Indicators/Indicators.htm`, `Expressions/Results_Filters.htm` and
`Expressions/Referencing_Other_Data_Variables_in_Expressions.htm`.

## 4. Indicator branches

### What they are for

Indicators live under the top-level **Indicators** branch, the last major category of the tree.
Like Key Assumptions they are the user's own variables and are not used in LEAP's calculations;
unlike every other variable they are calculated **after** the main calculation, so they may refer
to the **present-year value of result variables** without `PrevYearValue`. That makes them the
place for energy per capita, emissions per unit of GDP, the share of renewables in generation,
the number of households on clean fuels, a distance from an NDC target. Two consequences:

- A regular data variable may not reference an indicator (indicators come last). Only other
  indicators may.
- Changing an indicator expression does not make the scenario's results out of date; LEAP
  updates the indicators themselves.

The Indicators branch is hidden by default: General: Settings, Scope tab, Indicators check box;
through the API `api_get`/`api_set` `AreaSetting("ShowIndicators")`. While that setting is false
the Indicators branch is invisible to `get_branches` and `find_branches`, but `api_get`
`Branches("IND")` still reads it. When shown, Indicators, Non Energy and the other top-level
branches with negative IDs are read like any branch: `get_branch` by ID or full name,
`get_branches` with one of them as `parent`. Below it the user adds **Indicator Category** branches (folders) and
**Indicator** branches, each with a unit entered as text and a scale. An Indicator branch can only
sit under an Indicator Category (`api_get` `BranchTypes("Indicator")` gives ParentTypes =
"Indicator Category"), so the category is required. The Indicator Functions (`RegionIndicator(Branch:Variable, fRankHigh)`,
`ScenarioIndicator(Branch:Variable, fRatioToMean)` and the rest; topic "Indicator Functions")
compare a value across regions or scenarios: rank, score, z-score, ratio to mean, index to base
year and others.

### Adding and writing one ("edit anything" access)

1. `api_call` `AddBranch("Indicators", "Per Capita", "Indicator Category")`. The category is
   required: an Indicator branch cannot sit directly under Indicators (the shorter name `IND`
   stands for the Indicators branch in branch paths).
2. `api_call` `AddBranch("Indicators\Per Capita", "Energy per Person", "Indicator", "Unit=GJ per person; IndicatorScaleID=0")`.
   `Unit` is free text, as on the screen; the scale property is `IndicatorScaleID`, not
   `IndicatorScale` (unverified: its accepted values). `api_get` `BranchTypes("Indicator")` lists
   the creation property names AddBranch takes.
3. `get_branch` on the new branch to see its data variable's name (unverified; read it, do not
   assume "Indicator"), then `set_expression` in Current Accounts or in the scenarios like any
   other cell. The expression may mix data and results:
   `Demand:Final Energy Demand[Gigajoule] / Key\Population[Person]`,
   `Freedonia:One_Hundred Year GWP Direct At Point of Emissions[Tonne] / Key\Population[Person]` or
   `Transformation\Electricity Generation:Outputs[GWh, Tag=renewable] / Transformation\Electricity Generation:Outputs[GWh] * 100`.
   Result variable names come from `get_branch` on the referenced branch, never from memory.
4. Before promising a comparison between scenarios, `get_expression` on a tagged technology in
   each scenario: when the shares are inherited, the indicator will be identical across
   scenarios, and the user should know.
5. Values appear after a calculation: `calculate` when the user wants them, then `get_values` at
   the indicator branch for the scenarios and years asked (which variable name `get_values`
   wants at an indicator branch is unverified; `get_branch` lists it). Current Accounts has no
   stored results, so read the base year of a real scenario.

## 5. User variables

### What they are

A user variable is an extra variable (up to 400 per area) that appears as a tab in the Analysis
view beside the standard ones. It has a name, a scale and a unit as text (a label only; nothing
is converted), a category, notes, default expressions for Current Accounts and for scenarios, an
optional minimum and maximum, and may be time-sliced, read-only, intermediate or summable. Its
cells take any LEAP expression and other expressions may refer to it like any variable. The help
says user variables cannot be reported in the Results view; they are for intermediate
calculations in the Analysis view and for feeding indicators.

**Where it appears** is a scope, set on the Analysis: User Variables screen:

- Branch Visibility: a kind of branch (all branches, Key Assumptions, demand categories, demand
  technologies, Transformation modules, processes, outputs, Resources, effect branches,
  Indicators and so on).
- Available On & Below Branch: a top branch, whether the top branch itself shows it, and how
  many levels below it do.
- Tag Visibility: a list of tags; the variable shows only at branches carrying one of them.
  Blank means every branch its other settings allow.
- Scenario Visibility: Current Accounts, scenarios, both or neither (hidden, data kept).

A user variable the user cannot see at a branch is usually outside one of these, not missing.

### Through the API

- List: `api_get` `UserVariables` (`UserVariables.Count`, `UserVariables("Fleet Age").UnitStr`,
  `.Scale`, `.BranchType`, `.TopVisBranch`, `.OnBranch`, `.VisibleLevelsBelow`,
  `.VisibleCurrentAccounts`, `.VisibleScenarios`, `.DefaultExpressionCurrentAccounts`,
  `.DefaultExpressionScenarios`, `.ReadOnlyCurrentAccounts`, `.ReadOnlyScenarios`, `.TimeSliced`,
  `.Intermediate`, `.Summable`, `.HasMin`, `.Min`, `.HasMax`, `.Max`, `.Notes`).
  `api_describe` on `UserVariable` gives the full list and the branch-type numbers.
- Define one ("edit anything"): `api_call` `UserVariables.Add("Fleet Age", 0, "years")`: name,
  scale as a power of ten (0, -2 percent, 3, 6, 9, 12), unit text. The new variable shows on
  every branch at every level, in Current Accounts and scenarios, default expressions 0. Then
  narrow it with `api_set`: `UserVariables("Fleet Age").BranchType` = 104 (demand technologies),
  `.TopVisBranch` = a branch (unverified whether `api_set` takes a branch path for an object
  property), `.VisibleLevelsBelow`, `.OnBranch`, `.DefaultExpressionScenarios`, `.Notes`.
  The API reference exposes no Tag Visibility member on a user variable; that list is set on the
  User Variables screen (unverified: it may exist under another name; `api_describe` tells).
- Fill it: at a branch where it is visible, `set_expression` with the user variable's name as
  `variable`, as for any variable; `set_expressions` for many branches. A default expression
  (`api_set` `DefaultExpressionCurrentAccounts`) covers every branch where nothing is entered and
  is not checked when set, so read a value back.
- Read it: `get_branch` with a scenario lists it among the branch's variables (name the scenario
  it is visible in: a variable visible in Current Accounts only is read with scenario "Current
  Accounts", whatever LEAP's screen shows); `get_expression` and `get_values` with the
  variable's name give the expression and the numbers.
- Delete: `api_call` `UserVariables.Delete("Fleet Age")` removes all its data and cannot be
  undone; expressions that refer to it are left broken. Only when the user asks.

## 6. Typical uses

| The user wants | Do |
|---|---|
| Group technologies as clean or efficient | tag them (`Branches("...").Tags.Add("clean")`); put the tags in one group with Use For Results |
| Report a sector scattered across the tree (all cooking, all cooling) | one tag group, one tag per branch; `show_in_leap` with the group as a dimension, or an indicator summing `...[Tag=...]` |
| Households on clean fuels | indicator: `Demand\Household:Total Activity[Household, Tag=clean]`; split by sub-tree with `Demand\Household\Urban:...` and `Demand\Household\Rural:...` |
| Energy or emissions per capita (NDC indicator) | indicator: result at the root or `Demand` divided by `Key\Population`, for example `Freedonia:One_Hundred Year GWP Direct At Point of Emissions[Tonne] / Key\Population[Person]`, unit text "GJ per person" or "t CO2e per person"; say which GWP horizon and variant was used |
| Share of renewables in generation | tag renewable processes; indicator: `Outputs[GWh, Tag=renewable]` over `Outputs[GWh]` at the module |
| Energy intensity of GDP | indicator: `Demand:Final Energy Demand[...] / Key\GDP[...]` |
| A branch-level parameter LEAP does not have (fleet age, a policy flag) | user variable scoped to the branch kind, filled with `set_expressions` |
| An efficiency bonus only at tagged branches | expression with `If(HasTag(efficient), ..., ...)` |

## Common mistakes

- `Tag<>x` on a data-variable reference: only `Tag=` is supported there. Use an indicator that
  subtracts the tagged part from the total, or a second tag.
- A filter other than Tag on a data variable (`Fuel=` works on results only).
- Making a regular data variable refer to an indicator: refused, indicators are calculated last.
- An indicator referring to itself or two indicators referring to each other: circular.
- Expecting results to go stale after changing an indicator expression: they do not; the
  indicator alone is recalculated. Expecting a user variable or indicator to change demand or
  supply: neither is used in LEAP's calculations unless a calculated variable refers to it.
- Two tags from the same tag group on one branch, or none: the branch shows wrongly in that
  results dimension.
- A user variable "missing" at a branch: check its BranchType, TopVisBranch, VisibleLevelsBelow,
  OnBranch, Tag Visibility and Scenario Visibility before adding a second one.
- Writing a user variable's unit as if LEAP converted it: it is a label.
- Deleting a tag from `Tags` (area-wide) when the user meant one branch.
- Guessing result variable names, tag names or a tag group's dimension name instead of reading
  them from `get_branch`, `api_get Tags` and the `show_in_leap` answer.

## Tidy-ups worth reporting

Mention these when `api_get` `Tags` and `TagGroups` show them, and offer to fix them:

- Duplicate tag names that differ only in punctuation or case (for example "Nuclear" and
  "Nuclear.").
- Tag groups without Use in Results, which never appear as a dimension in the Results view.
- Tags defined in the area but attached to no branch.

## Example (illustrative, not yet run)

Freedonia: base year 2020, scenarios Baseline and Mitigation. User: "Tag the clean cooking
technologies and give me an indicator of how many households cook with clean fuels in each
scenario."

1. `leap_status` → `assistantAccess` is "add and edit anything"; otherwise stop and say what is
   possible read-only. `get_area` → scenarios Baseline, Mitigation.
2. `find_branches` "cooking" → `Demand\Household\Urban\Electrified\Cooking` and the rural ones;
   `get_branch` on each lists the technology children (electricity, LPG, natural gas, kerosene,
   charcoal, wood, whichever the area has; take the names from the answer).
3. Agree with the user which count as clean (the help's example: electricity, natural gas, LPG).
   `api_call` `Branches("Demand\Household\Urban\Electrified\Cooking\LPG").Tags.Add("clean")` for
   each; `api_get` `Tags("clean").Branches` to confirm the list.
4. `api_get` `AreaSetting("ShowIndicators")`; if false, `api_set` it true so the user sees the
   branch (while it is false, `get_branches` and `find_branches` do not show it; `api_get`
   `Branches("IND")` still does). The category comes first, since an Indicator branch cannot sit
   directly under Indicators: `api_call` `AddBranch("Indicators", "Cooking", "Indicator Category")`,
   then `api_call` `AddBranch("Indicators\Cooking", "Clean Cooking Households", "Indicator", "Unit=Thousand Households")`.
5. `get_branch` on the new branch for its variable name; `set_expression` there, Current
   Accounts, `Demand\Household:Total Activity[Thousand Household, Tag=clean]` ("Thousand
   Household" is a rescale of the variable's own unit, Household, as `get_branch` on
   `Demand\Household` shows for Total Activity). Scenarios inherit it. For an urban and a rural
   count, two more indicators with `Demand\Household\Urban:...` and `Demand\Household\Rural:...`.
6. `get_expression` on one tagged technology (for example the LPG branch's share) in Baseline and
   in Mitigation. If Mitigation inherits the Baseline shares, say so now: the indicator will be
   the same in both scenarios until the shares differ.
7. `calculate` with the user's agreement; `get_values` at the indicator for Baseline and
   Mitigation, 2020, 2030, 2050. Report the numbers with the unit, and that any difference between
   scenarios comes from the cooking fuel shares in Mitigation.
8. Offer a share version (divide by `Demand\Household:Total Activity[Thousand Household]` times
   100, unit "%"). Say what was added (one tag on N branches, one indicator category, one or three
   indicator branches), that it is not saved until `save_area`, and that the tags also appear in
   the Results view once put in a tag group with Use For Results.
