---
name: leap-reporting
description: Turn a calculated LEAP model into a report, policy brief or presentation through the LEAP MCP tools. Use when the user asks to "write up the results", wants a report, a policy brief, a summary of scenarios, charts for a report or a presentation, an export to Excel, favorites or an overview of the key charts. Covers planning the tables and charts from the question, building each chart in LEAP, saving favorites and collecting them in an Overview, exporting files, keeping units, scales, years and rounding consistent, and writing the text with its caveats.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: leap_status, get_area, get_notes, get_values, get_expression, get_milestones, set_milestone, show_in_leap, read_view, view_image, export_view, save_favorite, api_get, api_call, search_help, read_help_topic
  tested-on: LEAP 2026.9.0.19, Freedonia
  status: draft for review
---

# Reporting LEAP results

A report turns a calculated model into an answer a reader can act on: a few charts and tables
that all use the same scenarios, years and units, and text that says what they show and how
far to trust it. This skill builds on leap-results (which tool reads which result, result
variable names, filters, units) and on step 7 of leap-build-scenario (comparing a scenario with
its baseline). It does not repeat them.

## Step 1: Plan the report from the question

Before any chart, settle three things with the user and write them down:

- **Scenarios**: the baseline and the scenarios to set against it, named as the user names
  them. `get_area` gives the scenario tree and `hasResults`; only calculated scenarios can be
  reported. Scenarios whose socioeconomic assumptions differ are not a policy comparison
  (help, Concepts: Scenarios); say so if the user wants one.
- **Years**: the base year, two or three report years (for example 2030, 2040, the end year)
  and the comparison years. Years before the first scenario year are the same in every
  scenario, so comparisons start at the first scenario year.
- **Indicators**: the result variables that answer the question. Name them with
  `get_branch` or `search_help`, never from memory.

The standard set for an energy and emissions study, each one chart or table:

| Topic | Result variable and branch | Dimensions |
|---|---|---|
| Final energy demand by sector | `Final Energy Demand` at Demand, legend Branches (one level) | Years × Branches |
| Final energy demand by fuel | same, legend Fuels | Years × Fuels |
| Electricity generation by source | `Outputs by Output Fuel` at `Transformation\<module>\Processes`, legend Branches, so the processes are the series (`Energy Generation` is time-sliced: it needs Time Slices or `Years & Time Slices` on the X axis, and `show_in_leap` refuses it with Years alone) | Years × Branches |
| Generating capacity | `Capacity` at the same module | Years × Branches |
| Primary supply | `Primary Requirements` at Resources, legend Fuels | Years × Fuels |
| Emissions by sector | the 100-year GWP result at the root, legend Branches | Years × Branches |
| Emissions by gas | `Pollutant Loadings` or the GWP result at the root, legend Effects | Years × Effects |
| Costs, if the area has them | the Cost-Benefit view, or social cost results at the root | table |
| Headline comparison | the totals above, scenarios side by side in two or three years | table |

Drop what the question does not need; add what it does (a sector table, a fuel, a region). A
brief needs fewer charts than a report: usually the headline table and two or three charts.

The root branch is named for the area (`get_area`'s name), for example `Freedonia`. There is
no result variable called `Outputs`: at a module branch, legend Branches gives only "Output
Fuels" and "Processes", so read generation at the module's `Processes` branch. Sector parts
need not add up to the root: Demand plus Transformation GWP is less than the area total
because of Non Energy. Read the root for totals and the parts for shares.

`get_notes` on the area and on the main branches gives the model's own description of itself,
its sources and its scenarios; quote it as the model's documentation, not as fact.

## Step 2: Build each chart in LEAP

`show_in_leap` with `view` Results puts one chart on screen. Choose the axes for the reader:

| To show | x_axis | legend | chart_options |
|---|---|---|---|
| A trajectory compared across scenarios | Years | Scenarios | `ChartType=Line` |
| Composition over time (fuels, sectors, sources) in one scenario | Years | Fuels or Branches | `ChartType=Bar; Stacked=Stacked` |
| Composition in each scenario, year by year | `Years & Scenarios` | Fuels or Branches | `ChartType=Bar; Stacked=Stacked` |
| A snapshot of one year across scenarios | Scenarios | Branches or Fuels | `ChartType=Bar; Stacked=Stacked`, plus `year` |
| Shares rather than amounts | as above | as above | `Stacked=PercentStacked` |

Rules that come from how LEAP works:

- `Stacked=...` is accepted only when `ChartType` is Bar or HorizontalBar; give the chart
  type first in the same `chart_options` string. Line charts compare; stacked bars compose.
- `unit` takes the unit name with no scale word (`Gigajoule`, `Metric Tonne`); LEAP picks the
  scale. Read the scale from `read_view`'s heading and keep it the same in the text.
- `select` names the scenarios and items: `Scenarios=Baseline, Mitigation; Fuels=All`.
  Scenario names in the legend are the user's names; the abbreviation appears where names
  are long.
- The Results view keeps the filters of whatever was shown before. So every `show_in_leap`
  for a chart must set `select` for every dimension that is not on an axis (`Fuels=All`;
  `Effects=All`; `Regions=All`, as the result has them) and, for bar charts over years, the
  years to show (`Years=2020, 2030, 2040, 2050`). Confirm "All Fuels" (or the filter you
  meant) in `read_view`'s heading before trusting the numbers: a leftover `Fuels=Electricity`
  filter once made a demand chart four times too small.
- Set `chart_options` `NumDecimals=2` (or 1 with large scales) before `read_view` or a csv
  export; LEAP's default rounding loses a significant figure. LEAP re-picks the scale
  (Thousand toe, Million toe) when the years change, so read the scale from the heading each
  time.
- `Years & Scenarios` bars with many years are unreadable (62 bars, labels printed over the
  title); restrict the years with `select`. With this layout LEAP prints only the first
  dimension's label under each group; say so when describing the picture.
- `read_view` tables with scenarios on an axis carry a Total row and a Total column that add
  the scenarios and the years; ignore them in a brief, or switch them off with
  `chart_options` `TableRowTotal=false; TableColumnTotal=false`.
- Branches on the legend are the children of the branch you named; the number of levels is
  a chart setting, not something you add up yourself.
- `api_call` with path `ChartOptionNames("json")` (it is a method, so `api_get` fails) lists
  every chart option (palette, grid lines, labels, decimals, table totals) with the values it
  takes; use it before guessing one.
- Milestones (a policy start, a target year) can be drawn on charts whose X axis is years;
  they are off until `chart_options` `ShowMilestones=true` is given for a chart, and the
  setting is kept with a favorite. `get_milestones` lists the area's milestones and
  `set_milestone` adds one (see leap-milestones).
- One process or demand technology can be shown alone when the result is not stacked (the
  answer's `branchShown` names it); for a stacked result put Branches on the legend or X axis
  and `select` `Branches=<name>`.

After each `show_in_leap`, `read_view` to confirm the variable, scenarios, years, unit and
scale in the heading, and that the numbers are the ones you will quote. `view_image` is for
your own check of how the chart reads (labels overlapping, a series hidden); the user does not
see it in the conversation, and it never goes into the report.

Tell the user what is on screen after each chart; they are looking at the same LEAP.

For headline numbers, `get_values` `filter` takes Fuel, Effect, Time Slice, Cost Category,
Module Cost Category, Capacity Type, Vintage, Output Type, Input Type, Import Category, Export
Category, Forex Category, Region and Scenario. `Branch=` and `Year=` are refused with advice:
name the branch and the years in their own parameters. An unknown item is refused with the
names LEAP has. Percent results such as `Reserve Margin` are read with no `unit` and come back
in `Percent`. `search_help`'s `link` is the web address to cite; `localFile` is for your reading.

## Step 3: Save favorites and collect an Overview (optional)

Skip this step when the user asked only for files or text. A favorite keeps every setting of
a chart or table (branch, result, axes, filters, unit, chart type, stacking, formatting) but
not its values, so it shows the latest results after any recalculation. That makes favorites
the right way to hand the user a chart set they can reopen and refresh.

- `save_favorite` with `name` and `folder` (needs "edit anything" access; LEAP must be in the
  Results view). Use one folder per report, named for it ("Policy brief 2026"), and names
  that say what the chart is ("Final demand by sector, Mitigation"). A favorite of the same
  name is replaced. Favorites are kept at once, whether or not the area is saved.
- `api_get` `Favorites` lists them; a favorite in a folder has the full name `Folder#Name`.
  `api_call` `Favorites("Folder#Name").Activate()` or `show_in_leap` with `favorite` puts one
  back on screen. Favorite names may not contain `/ \ | : < > * ? [ ] =` or a double quote.
- An Overview shows up to 16 favorites on one screen, with a Table tab whose contents
  `read_view` returns. There is no MCP tool that builds one: tell the user to open the
  Overviews view, Manage Overviews, add an overview and pick the folder's favorites. Once it
  exists, `show_in_leap` with `view` Overviews shows it (selecting one overview by name through
  `show_in_leap` is unverified). The Overview exports all its charts to PowerPoint from its
  toolbar, which the user does by hand.
- In Manage Favorites the user can add a title, subtitle and notes to each favorite; title and
  subtitle are used when charts are exported, and the notes can be drawn beside the chart.
  Offer the chart's caption text from step 6 for the notes. Setting them through the API is
  unverified; the ILEAPFavorite object exposes only Name, FolderName, FaveName, Index and
  Activate.

## Step 4: Export files

`export_view` writes what is on screen to a folder under the user's Documents (which may be
redirected, for example to Dropbox) and returns the full path; always give the user the
folder the answer names. `format` is one of:

| Format | What it writes | Use for |
|---|---|---|
| `csv` | the table of the view, as LEAP exports it | tables for the report, your own checking |
| `excel` | the same table in a workbook (needs Microsoft Excel on the computer) | tables the user will edit or chart |
| `png` | a picture of the Results chart, Sankey diagram or screen | charts for a document or slides |
| `svg` | the Sankey diagram as a drawing | a Sankey that must scale in print |

Give `name` so the files are recognizable ("Fig3 Emissions by sector Mitigation"); otherwise
LEAP makes a name from the view and the time. One chart, one export: switch the chart with
`show_in_leap`, confirm with `read_view`, then `export_view`.

- **Results tables**: `chart_options` `View=Table` before a `csv` or `excel` export when the
  table page should be in front (the table export itself is independent of the page shown:
  unverified). Table options such as `NumDecimals` and `TableColumnTotal` are chart options.
- **Energy Balance**: `show_in_leap` `view` Energy Balance, `scenario`, `year` the base year,
  `unit`; `read_view` gives the balance; `export_view` `csv` or `excel`. A base-year balance
  anchors the report in the calibrated year; a balance in the end year of each scenario shows
  where the system goes. LEAP's own Excel export can write one balance per year or region to
  separate sheets; whether `export_view` does the same is unverified, so export one at a time.
- **Sankey**: `show_in_leap` `view` Sankey, `scenario`, `year`; `export_view` `svg` (or
  `png`). The detail level (fuels only, sectors, subsectors) and fuel groups versus fuels are
  area settings the user sets on the Sankey toolbar; say which the picture shows.
- **Summary views**: the Cost-Benefit report (cumulative discounted costs and benefits of each
  scenario against a reference, with avoided GHG and cost per tonne) and the Decomposition
  report (a waterfall of population, affluence, intensity and carbon factors) are their own
  views: `show_in_leap` `view` `Cost-Benefit` or `Decomposition` (also `MACCs`,
  `Affordability`; there is no view called "Summaries"), then `read_view` and `export_view`.
  Costs appear only where unit costs were entered: a scenario can differ physically and show no
  cost difference.
- **Pictures**: `png` from `export_view` is the only chart picture that reaches the user.
  Where the report is written outside LEAP, a chart drawn from `read_view`'s numbers is often
  clearer and matches the text's units exactly.

## Step 5: Keep everything consistent

- **One energy unit** across every table and chart (the area's default, or the one the user
  asks for), **one emissions unit** (CO2 equivalent for GWP results, mass per gas for
  pollutant loadings), one currency and price year for costs.
- **One scale per quantity**, chosen so the headline numbers have one to three digits before
  the point (thousand tonnes of oil equivalent, million tonnes CO2e). LEAP picks a scale per
  chart; check each `read_view` heading and ask for the common unit again if a chart differs.
  Never mix scales within a table.
- **The same years** in every table: the base year, the report years, the end year.
- **Three significant figures** in the text and tables, fewer when the model's inputs are
  rougher. Percent changes to the nearest whole percent unless the difference is small.
- **Scenario names as the user uses them**, the same spelling in every caption. Give the
  LEAP name once in brackets if it differs.
- **Captions** that state variable, branch, scenarios, unit and scale, and the source
  ("LEAP, area Freedonia, calculated on <date>").

## Step 6: Write the text

Lead with the answer: the headline difference in the end year, in absolute terms and as a
percent of the baseline. Then:

1. **Setting**: the area, the base year and end year, the first scenario year, the baseline
   and what it assumes (from `get_notes` and `get_area`), the scenarios compared.
2. **Results**, one short section per indicator in the order of the headline table: the
   baseline level, the scenario level, the difference and percent in two or three years. A
   table beats a paragraph of numbers.
3. **Drivers in LEAP's terms**: which activity levels, intensities, shares, capacities or
   dispatch choices moved, as `get_expression` and the scenario's own notes show. A step in a
   single year is usually a measure starting; say so. A scenario can inherit from several
   additional scenarios (a package): `api_get` `Scenarios("Mitigation").AdditionalScenarios`
   lists them. `get_area` shows only the parent, and `get_expression` only says inherited
   true or false, so name the measures behind a package scenario from that list, and do not
   promise to trace a driver through `get_expression` alone.
4. **Model versus interpretation**, kept apart: "the model shows demand falling 12%" is the
   model; "this is achievable" or "this is the cheapest path" is your reading, and must be
   labeled as such.
5. **Caveats**, always present:
   - years after the base year are projections, not data, and no year is calibrated beyond
     Current Accounts;
   - what the model does not cover (sectors, fuels, gases, upstream emissions, costs not
     entered, regions outside the area);
   - the uncertainty of the main drivers (growth rates, prices, technology costs); report
     sensitivity scenarios where the area has them, and a stochastic spread only when the
     area was calculated that way;
   - where results depend on a setting (discount rate, GWP horizon, dispatch rule).
6. **What was done in LEAP**: which favorites and files were made and where, so the user can
   reproduce the charts.

## What not to do

- Put a `view_image` picture in the report or describe it as something the user saw. Use
  `export_view` for pictures or draw from the numbers.
- Quote a number without its unit, scale, scenario and year.
- Mix scales or units between charts, or between a chart and the text.
- Give more precision than three significant figures, or a percent to decimals.
- Compare scenarios in years before the first scenario year, or compare a scenario against a
  baseline with different population or GDP assumptions as if it were a policy effect.
- Add up branches, fuels or regions yourself when a parent branch, a filter or a view gives
  LEAP's total.
- Report a scenario that is not calculated, or results that are out of date
  (`leap_status` → `resultsUpToDate`).
- Present the model's documentation, or your interpretation, as what the model computed.

## Example

User: "Write a short policy brief comparing Mitigation with Baseline for Freedonia."

1. `leap_status` → ready, area Freedonia, results up to date, access: edit anything.
   `get_area` → base year 2020, first scenario year 2021, end year 2050; Baseline and
   Mitigation calculated. `get_notes` on the area → a training model of an imaginary country.
2. Plan agreed with the user: years 2020, 2030, 2040, 2050; indicators: final demand by
   sector and by fuel, electricity generation by source, primary requirements, GWP emissions
   by sector; costs only if the Cost-Benefit report has entries. Units: thousand tonnes of oil
   equivalent for energy, million tonnes CO2e for emissions.
3. Headline numbers with `get_values`: `Final Energy Demand` at Demand and
   `One_Hundred Year GWP Direct At Point of Emissions` at the root (branch `Freedonia`),
   scenarios "Baseline, Mitigation", 2021–2050, units as planned. Table:

   | Indicator | 2020 | Baseline 2050 | Mitigation 2050 | Difference | Percent |
   |---|---|---|---|---|---|
   | Final energy demand (thousand toe) | … | … | … | … | …% |
   | GHG emissions (million tonnes CO2e) | … | … | … | … | …% |

   (Values come from the live model; none are given here.)
4. Charts, each `show_in_leap` → `read_view` (check "All Fuels" and the scale in the
   heading) → `save_favorite` in folder "Policy brief" if the user wants favorites:
   - "Final demand by sector": Demand, Final Energy Demand, `x_axis` `Years & Scenarios`,
     `legend` Branches, `chart_options` `ChartType=Bar; Stacked=Stacked; NumDecimals=2`,
     `unit` Tonne of Oil Equivalent, `select` `Scenarios=Baseline, Mitigation; Fuels=All;
     Years=2020, 2030, 2040, 2050`.
   - "Final demand by fuel": same with `legend` Fuels and `select` `Scenarios=Baseline,
     Mitigation; Branches=All; Years=2020, 2030, 2040, 2050`.
   - "Electricity generation by source": `Transformation\Electricity Generation\Processes`,
     Outputs by Output Fuel, `x_axis` `Years & Scenarios`, `legend` Branches (the processes),
     stacked bars, `select` with `Fuels=All` and the four years.
   - "Primary requirements by fuel": Resources, Primary Requirements, `legend` Fuels,
     `select` with `Branches=All` and the four years.
   - "GHG emissions, scenarios": root branch `Freedonia`, the GWP result, `x_axis` Years,
     `legend` Scenarios, `ChartType=Line`, `select` `Effects=All; Branches=All`.
   - "GHG emissions by sector 2050": root branch `Freedonia`, `x_axis` Scenarios,
     `legend` Branches, `year` 2050, stacked bars, `select` `Effects=All`.
5. `export_view` `png` for each chart with a figure name; `csv` of the headline tables;
   Energy Balance 2020 Baseline as `excel`; Sankey 2050 for each scenario as `svg`. The paths
   each answer names go into the brief's annex.
6. If favorites were saved, ask the user to gather the "Policy brief" folder into an Overview
   in Manage Overviews so the set can be reopened after any recalculation.
7. Text: the answer first (emissions in 2050 lower by X million tonnes CO2e, Y% below
   Baseline), the setting, one paragraph per indicator with the drivers (the measures in
   Mitigation, named from its `AdditionalScenarios` list: efficient lighting and
   refrigerators, CNG buses, gas and renewables in generation, efficient industry, biogas),
   then caveats: a training model of an imaginary
   country, projections from a single base year, costs only where entered, no upstream or
   land-use emissions, growth rates as assumed in Baseline.

## Unverified in this draft

Checked against LEAP's help and the API definition: favorites keep settings not values,
folders and `Folder#Name`, `Activate`, the Favorites Manager title, subtitle and notes,
Overviews of up to 16 favorites with a Table tab, the export formats and folder, Sankey svg,
the Energy Balance and summary view contents, composite dimensions, stacking limits, the unit
rule. Not confirmed by running the tools:
choosing one overview by name in `show_in_leap`, whether the Results table export depends on
the page shown, whether `export_view` writes all balances at once, favorite notes drawn on
exported charts (built, not yet checked in the running program), and every number in the
example.
