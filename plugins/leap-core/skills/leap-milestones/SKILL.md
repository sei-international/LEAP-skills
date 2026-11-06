---
name: leap-milestones
description: Milestones on LEAP Results charts through the LEAP MCP tools. Use when the user mentions a milestone, a target year, marking a year on the chart, an NDC target, a policy start year, a historical event, a vertical line on the chart, a label or note on a chart at a year, or asks why a chart shows (or does not show) such marks. Covers what a milestone is, listing, adding, changing and deleting milestones with get_milestones, set_milestone and delete_milestone, the LEAP.Milestones API, the chart options that make them visible, and how to pair a milestone with a scenario result on a chart.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: leap_status, get_area, get_branch, get_values, get_milestones, set_milestone, delete_milestone, get_changes, show_in_leap, read_view, view_image, export_view, save_favorite, api_describe, api_get, api_set, api_call, search_help, read_help_topic
  tested-on: "Freedonia, LEAP 2026.9.0.19, 2026-11-06 (get_milestones, set_milestone, delete_milestone, api_get Milestones)"
  status: draft for review
---

# Milestones on LEAP charts

A milestone is a short note tied to a year, such as "NDC target" at 2030 or "Carbon tax starts"
at 2025, that LEAP draws on Results charts whose X axis is years. It can also be tied to a
scenario, a region and a branch, belong to groups, carry notes, and show live results in its text.
Milestones belong to the area (the model), but whether a chart shows them, and how they look,
belongs to each chart and is saved with a favorite.

A milestone is a labeled year, not a value. It does not draw a horizontal line at a target level
or a point on a series. To plot a target level as a line, add a Key Assumption (or Indicator)
branch holding the target path and put it on the chart as a series.

## What an assistant can do (read this first)

Three MCP tools work on the milestones themselves (LEAP 2026.9.0.19 or later):

- **`get_milestones`** lists them, with an optional `scenario` filter (that scenario's milestones
  plus the ones for all scenarios). Works at read-only access.
- **`set_milestone`** adds one (omit `id`) or changes one (give `id`). Needs "add and edit
  anything" access.
- **`delete_milestone`** removes one by `id` or by exact `name`; a name that matches more than
  one milestone is refused, so use the id. Needs the same access.

Both writers log to `get_changes`, and nothing is saved until the user saves the area.

Around them, the chart tools do the rest: **showing** milestones on the chart on screen with
`show_in_leap` and `chart_options`, or `api_set` of `ChartOption("ShowMilestones")` (chart
options, not milestone data); **keeping that look** with `save_favorite` (needs "edit anything"
access); **reading the number** for a milestone's text with `get_values`; **exporting** a chart
with its milestones with `export_view`.

## The three milestone tools

`get_milestones` answers `milestones[]`, each with `id`, `name`, `year`, `scenario` and
`scenarioId`, `region` and `regionId`, `branch` and `branchId`, `position` ("above" or "below"),
`hidden`, `groups`, `hasNotes` and `canShow` (whether LEAP would draw it at all: not hidden, year
inside the area's years, results for that year); plus `count`, `groups[]` (the area's milestone
groups) and a `note`.

`set_milestone` takes:

| Parameter | Takes |
|---|---|
| `id` | the id to change; omit to add |
| `name` | the text drawn in the box |
| `year` | 1900 to 2200 |
| `scenario` | `all`, or a scenario name |
| `region` | a region name (multi-region areas) |
| `branch` | a full branch name; the area's name for the whole area; `none` for no branch |
| `position` | `above` or `below` |
| `groups` | group names, comma separated |
| `hidden` | true or false |

Two year rules LEAP applies: a year before the first scenario year goes to Current Accounts
whatever scenario you name, and shows with every scenario; Current Accounts cannot be given a
year at or after the first scenario year.

The same objects are in the API: `LEAP.Milestones` (Count, Item by index, by `"ID:n"` or by
name, Exists, Add(Name, Year, [Scenario], [Region]), Delete, MaxID) and each `LEAPMilestone`
(ID, Name, Year, Scenario and ScenarioID (-1 = all), Region and RegionID, Branch and BranchID
(-88 = none, -1 = the area), Position 0 above / 1 below, ColorIndex (-1 = automatic), Hidden,
Groups as comma-separated names, Notes). `api_get Milestones` and `api_get Milestones(1)` are
verified. Scripts use them; in a conversation prefer the three tools.

## Where the user sees milestones

- Results view, Chart tab (and the chart half of Split), when the X axis is Years and the chart's
  Milestones: Show is on. They are off on every chart until turned on.
- Exports of such a chart (picture, PowerPoint) include them (help: Chart Options).
- Overview charts and the full-screen chart also draw them (from the source, not the help: unverified).
- Each milestone is a box with its text, joined to the chart by a line, above the plot or below the
  X axis. Double-clicking one opens the Milestones screen.
- A milestone at a year shows only if that year is a result year. In an area with custom result
  years, a milestone at a year LEAP does not store is not drawn.

## Does the area have milestones?

`get_milestones`: `count` and the list, including hidden ones and ones tied to scenarios,
regions or branches not on the current chart. `canShow` false with `hidden` true, or a year
outside the area's years, explains a milestone the user cannot find on any chart. The user sees
the same list in LEAP under Milestones: Edit (right-click the chart).

## How the user creates and edits them in LEAP

The user has the same powers in LEAP itself, and some the tools lack (color, notes, %1
parameters). From the help topic "Milestones" (Menu Option: Chart: Milestones, on the Chart
toolbar of the Results view, or right-click a chart). The Milestones menu has:

- **Show**: show or hide the milestones on this chart.
- **Add...**: add a milestone. From a right-click on the chart, it starts at the year clicked.
- **Delete** and **Hide**: for the milestone right-clicked. A hidden one is kept but drawn on no chart.
- **Show All Hidden**: show every hidden milestone again.
- **Edit...**: opens the Milestones screen. Editing a milestone never makes the area need a new calculation.
- **Groups**: when the area has milestone groups, each group plus (No Group), so a chart can show chosen groups only.
- **Options**: Show Lines and Line Width; Text Size (-5 to +5 points); Follow Values; Shift
  Milestones to Straighten Lines; Pin Legend to Top of Chart; Borders and Border Color.

The **Milestones screen** is a table, one row per milestone: Scenario and Region ("(Any
scenario)" and "(Any region)" show it everywhere; a milestone for a year before the first scenario
year belongs to Current Accounts and shows with every scenario that inherits those years), Year
and Milestone (the text; a scenario and year can have several), Groups, Branch (optional; on a
chart whose legend shows that branch the box takes the series' color and its line goes to that
series), Color (Automatic or fixed), Position (above the chart or below the X axis), Hidden. Each
milestone can also have notes, which are not drawn. A line under the table says when the selected
milestone will not be shown and why (hidden, year outside the area's years, no results for that year).

**Live results in the text**: the text may hold %1 to %9; the Parameters button says what each
shows (branch, variable, scale, unit, filters; year, scenario and region default to the milestone's
own; an Excel-style number format). "Abated %1 million tonnes by 2050" stays up to date as the
model changes. The user writes the unit into the text. n/a means results are not available; a
question mark means the branch no longer exists; %% is a literal percent sign.

When the user asks for a milestone, add it with `set_milestone`, then put a chart on screen with
`ShowMilestones=true` so they see it. A fixed color, notes or a %1 parameter in the text are set
in the Milestones screen (`set_milestone` does not take them): say so, with the steps in LEAP's
words.

## Chart options an assistant can read and set

`LEAP.ChartOption(Name)` (ridl: ILEAPApplication.ChartOption, get and set; `ChartOptionNames(Format)`
lists them; `IsChartOption(Name, Description)` checks one). The milestone options, from LEAP's
option table:

| Option | Takes | Meaning |
|---|---|---|
| `ShowMilestones` | true/false | Shows the area's milestones on a chart whose X axis is years |
| `MilestoneLines` | true/false | Joins each milestone to the chart with a line |
| `MilestoneLineWidth` | 1 to 6 | Width of those lines |
| `MilestoneTextSize` | -5 to 5 | Text size relative to the chart's text; 0 the same |
| `MilestonesFollowValues` | true/false | Each milestone just above the values of its year, not in a row along the top |
| `MilestonesStraighten` | true/false | Slides milestones sideways so lines run straight |
| `MilestonesPinLegend` | true/false | Keeps a side legend at the top when milestones add room above the plot |
| `MilestoneBorders` | BoxesAndLines, BoxesOnly, None | Which parts get a thin border |
| `MilestoneBorderColor` | Gray, Tinted | Border color |
| `MilestoneGroups` | comma list of group IDs; 0 = no group; empty = all | Which groups the chart shows |

Three ways to use them:

1. `show_in_leap` with `view` Results and `chart_options` `"ChartType=Line; ShowMilestones=true"`.
   Options are applied last, in the order given; a name or value LEAP does not have is refused
   with the list of what it takes. Works at read-only access: it changes only what is on screen.
2. `api_get` path `ChartOption("ShowMilestones")` to read; `api_set` the same path to `true`
   to write (needs edit access). Verified on LEAP 2026.9.0.18.
3. `api_call` `ChartOptionNames("JSON")` to list every option with its current value, or
   `api_call` `IsChartOption("ShowMilestones")` to check the name. Both verified. Note that
   `ChartOptionNames` is a method: `api_get` refuses it, even though `show_in_leap`'s own tool
   text says `api_get`. Use `api_call`.

A chart option set through `api_set` stays with the chart on screen and is not undone by the next
`show_in_leap` unless given again. If you set one only to test it, set it back.

`MilestoneGroups` takes group IDs, which the user cannot see on screen; `get_milestones`'s
`groups[]` lists the area's groups by name only. Leave `MilestoneGroups` alone and use the
Groups menu in LEAP instead; to show one group's milestones alone, hide the others with
`set_milestone` `hidden` only if the user agrees.

## Typical uses, and pairing a milestone with a result

- **NDC or net-zero target year**: "NDC target: 70% of Baseline by 2030", tied to the Mitigation
  scenario, branch the area root or Demand, Automatic color, so the box takes that scenario's line
  color when Scenarios is on the legend. The target figure goes into the name: read the Baseline
  value with `get_values` and compute 70% of it. A %1 parameter (set by the user in LEAP) shows
  the modeled value, not the target, since parameters take a reference, year, scenario, region
  and number format but do no arithmetic. So "Target 12.3 Mt, modeled %1 Mt" puts both in one box.
- **Policy start year**: "Efficiency standard starts", tied to the scenario that has the measure,
  so it appears only when that scenario is on the chart.
- **Historical event**: "Drought" or "Fuel price shock" at a year before the first scenario year;
  it belongs to Current Accounts and shows with every scenario.
- **Plant or project**: tied to the Transformation process branch, so on a chart with Branches on
  the legend the line goes to that plant's series.

To put a chart on screen that pairs the milestone with the scenario result it is about:

1. `leap_status` → results up to date (milestones for years with no results are not shown).
2. `get_branch` on the branch to confirm the result variable name (never guess it);
   `get_milestones` to see what the area already has, so you do not add a duplicate.
3. `show_in_leap` `view` Results, `branch`, `variable`, `x_axis` Years, `legend` Scenarios,
   `select` `Scenarios=Baseline, Mitigation`, `unit`, `chart_options`
   `"ChartType=Line; ShowMilestones=true"`. The `unit` here takes no scale word ("Metric Tonne";
   LEAP picks Million), while `get_values` takes the scale ("Million Metric Tonnes").
4. `read_view` to confirm the numbers; `view_image` to see whether the milestone boxes are there
   (for you only; the user sees the chart in LEAP). If none show, the usual causes are below.
5. Offer `save_favorite` so the chart keeps milestones on, and `export_view` (png, svg) for a file.

## Rules

- Add, change and delete only what the user asked for, and only at "add and edit anything"
  access; at lower access, hand the user the steps in LEAP's words.
- Ask before deleting; prefer `set_milestone` with `hidden` true, which keeps the milestone.
  `delete_milestone` by `id`, not by name, when names repeat.
- Nothing is saved until the user saves the area; say so after adding or changing milestones.
- Use the area's own scenario, region and branch names (`get_area`, `find_branches`); `branch`
  in `set_milestone` is the full name.
- After adding one, `get_milestones` to confirm the year and scenario LEAP recorded (a year
  before the first scenario year lands in Current Accounts), and show it on a chart.
- Turning milestones on changes what the user is looking at; say what you put on screen.
- A milestone's number should match what LEAP calculates: read it with `get_values` for the same
  branch, variable, scenario, year and unit, or suggest the %1 form so LEAP keeps it current.

## Common mistakes

- Adding a milestone and not turning `ShowMilestones` on: the user sees nothing.
- Giving Current Accounts as the scenario for a year at or after the first scenario year: refused.
- Expecting milestones on a chart with Scenarios or Fuels on the X axis: years only.
- Forgetting `ShowMilestones=true`: they are off on every new chart.
- Giving `chart_options` without `view` Results: refused.
- Telling the user a milestone needs a recalculation: it never does.
- Looking for a Current Accounts milestone only in Current Accounts: it shows with every
  scenario that inherits that year.
- Saying the user can see a `view_image` picture in the conversation.
- Using `api_get` for `ChartOptionNames`: it is a method, use `api_call`.
- Deleting by a name the area uses twice: refused; use the `id` from `get_milestones`.

## Example (Freedonia: base year 2020, first scenario year 2021, end year 2050; Baseline, Mitigation)

User: "Mark the 2030 NDC target on the emissions chart and show me Baseline against Mitigation."

1. `leap_status` → results up to date; access "add and edit anything".
2. `get_branch` "Freedonia" (the root) → id -1 and type "Unknown Branch Type", which is normal
   for the root; it lists the result variables, among them
   `One_Hundred Year GWP Direct At Point of Emissions`. `get_values` it for Baseline, 2030,
   `unit` `Million Metric Tonnes`, and compute the target from it (70% of Baseline, say).
3. `get_milestones` → `count` 0 (or the list; add nothing that is already there).
4. `set_milestone` `name` "NDC target: 12.3 Mt CO2e" (the computed figure), `year` 2030,
   `scenario` Mitigation, `branch` Freedonia, `position` above. The answer gives the new id.
5. `show_in_leap` `view` Results, `branch` Freedonia, `variable` as above, `x_axis` Years,
   `legend` Scenarios, `select` `Scenarios=Baseline, Mitigation`, `unit` `Metric Tonne`,
   `chart_options` `"ChartType=Line; ShowMilestones=true"`.
6. `get_milestones` `scenario` Mitigation → the milestone with `year` 2030, `scenario`
   Mitigation, `canShow` true. `view_image` to check the box sits at 2030 on the Mitigation
   line; `read_view` for the table. Offer `save_favorite` ("edit anything") and `export_view` png.
7. Tell the user what was added and shown, that a live modeled figure ("%1 Mt CO2e") can be set
   in the Milestones screen with the Parameters button, and that the milestone is in the area
   only once they save it.
