---
name: leap-data-from-spreadsheet
description: Bring data from a spreadsheet, statistics table or energy balance into a LEAP area through the LEAP MCP tools, mainly into Current Accounts. Use when the user has a file or table of numbers (households, vehicle stocks, generation by plant, an energy balance, prices) and wants it entered, updated or checked in LEAP. Covers mapping rows to branches and variables, units and scale conversion, choosing between typed values, time-series functions and Excel links, bulk entry with set_expressions, and calibration against the Energy Balance view.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: leap_status, get_area, get_branches, find_branches, get_branch, get_expression, get_notes, list_fuels, set_expressions, get_values, calculate, show_in_leap, read_view, set_notes, api_get, api_call, api_describe, search_help
  tested-on: Freedonia (sample area)
  status: draft for review
---

# Entering data from a spreadsheet

Most of the work is matching: each row of the user's table must land in one branch, one variable,
one scenario (usually Current Accounts), one region, in the unit and scale that cell uses. The
entering itself is one `set_expressions` call. Get the matching right and write it down.

## Step 1: Understand the table

Read the file (or the pasted table). For each column or row, note: what quantity, which unit,
which years, which scenario it belongs to (historical data → Current Accounts; projections → a
scenario), and which region.

Ask the user when the table does not say: the unit, the year, whether numbers are shares of a
total or absolute values, whether a blank means zero or unknown.

## Step 2: Map rows to cells

1. `get_branches` under the relevant sector, `depth` 0, to list every branch once; `find_branches`
   for names in the table.
2. `get_branch` for the target branches with scenario "Current Accounts": the variables, their
   units and scales, and the existing expressions. The technology's fuel is not in the answer:
   read it from the intensity unit and the branch name, or `api_get` on `Branches("full name")`,
   before matching a survey fuel to a branch. Note the unit above the technologies: survey
   percentages of households equal technology shares only when the category above is a 100%
   saturation.
3. Build a mapping table (keep it in the conversation; the user must be able to check it). When
   the user wants a check rather than an entry, the same table with the last three columns is the
   deliverable, and nothing is entered:

   | Table row | Branch | Variable | Table unit | LEAP unit and scale | Factor | LEAP now | Difference | Proposed |
   |---|---|---|---|---|---|---|---|---|

4. Rows that match no branch: list them, with a proposed branch and a starting intensity taken
   from a sibling elsewhere in the tree (a rural stove of the same fuel) and marked as such. Do not
   create branches silently. Creating many branches from a table is what LEAP's own Tree: Create
   Branches from Excel does well; suggest it to the user for that part. Single branches can be
   added through `api_call` AddBranch with "edit anything" access after asking; `api_describe`
   with object `LEAPApplication` and filter `AddBranch` gives the argument list (parent, name,
   branch type, and a property list that can name the fuel and the intensity unit).
5. Branches that get no row: list them too. The user decides whether each stays, goes to 0, or is
   deleted; a `Remainder(100)` neighbor goes to 0 by itself when the others sum to 100.

## Step 3: Units and scales

- The LEAP cell's unit and scale win. Convert the table's values to them, or enter the value in
  the table's unit with `ConvUnits`: `1250 * ConvUnits(ktoe, GJ)` keeps the source visible.
- A value of 51,200,000 people in a cell scaled "Million People" is entered as `51.2`.
- Shares: if the table gives absolute numbers for neighbors that LEAP holds as shares, compute the
  shares and let one neighbor be `Remainder(100)`; put the absolute total in the parent's activity.
- Energy balances mix units (ktoe, TJ, GWh, tonnes); convert each row explicitly and show the
  factor in the mapping table.

## Step 4: Choose the expression form

- One year: a number.
- Several historical years in Current Accounts: `Data(2015, 100, 2016, 104, 2019, 118)` when the
  years are exact observations, `Interp(...)` when values between should be filled. The base year
  value is what LEAP uses for Current Accounts in a one-year setup; later years matter when the
  area has several Current Accounts years.
- Projections into a scenario: `Interp(2030, x, 2050, y)`.
- The user wants LEAP to follow the spreadsheet as it changes: `Excel(file, range)` or
  `Interp(file, range)`. This needs the workbook saved on the user's computer at a path LEAP can
  open; the link breaks if the file moves. Say this trade-off; typed values are more transparent.

## Step 5: Enter in bulk

- Group the changes: one `set_expressions` call per sector or per table, `scenario` set once.
  Every change is checked first; one bad row stops the whole call with the reason per row, so the
  area is never half updated.
- At most 500 changes per call; split larger tables.
- Read back a sample with `get_values` (three branches, two years) and compare with the table.
- Record the source: `set_notes` on the sector branch with the file name, the date, the sheet, the
  unit conversions used. Ask before replacing notes that already exist.

## Step 6: Calibrate

After entering Current Accounts data, the base year should reproduce the statistics:

0. Before and after, `get_values` `Final Energy Demand` on the sector branch you changed, base
   year of the baseline scenario, to see the effect of the change on its own.
1. `calculate` (tell the user), wait on `leap_status`.
2. `show_in_leap` view `Energy Balance`, scenario the baseline (Current Accounts stores no
   results, so the baseline's base year stands in for it), `year` the base year, `unit` that of the
   source balance; `read_view`.
3. Compare row by row with the source: total final consumption by sector and fuel, transformation
   inputs and outputs, imports and production. Differences come from missing branches, a wrong
   share, a wrong unit, or an unmodeled flow (statistical differences, stock changes, non-energy
   use).
4. Report the comparison as a table of source versus LEAP versus difference, and name the cells to
   fix. Fix only with the user's agreement.

## Rules

- Current Accounts is the shared base of every scenario: entering here changes everything. Say so
  and get agreement before the first `set_expressions`. After changing a Current Accounts share,
  `get_expression` for the same cell in each scenario: a scenario that sets the share itself keeps
  its own value, and the set may no longer be consistent.
- When `search_help` returns a link that is a file path rather than a web address, give the user
  the topic's title instead.
- Never overwrite an expression that is a formula or a reference with a number without telling the
  user what it was; `set_expressions` returns the old value, keep it in your report.
- Keep the mapping table in the conversation. It is the audit trail.
- Nothing is saved until the user saves; offer `save_version` with a comment before a large import
  if the user wants a fallback.

## Common mistakes

- Entering absolute numbers into share variables.
- Forgetting the scale (thousands versus units) or the energy unit (ktoe versus TJ).
- Writing projections into Current Accounts, or history into a scenario.
- Matching branches by a similar name without checking the type and fuel.
- Replacing `Remainder(100)` with a number, so the set no longer sums to 100.
- Linking to a spreadsheet on the assistant's side rather than the user's; LEAP opens files on the
  user's computer only.

## Example

User: "Here are 2019 household counts by province and urban/rural. Put them in."

1. Table: 9 provinces × urban/rural, thousands of households. Area: multi-region, one region per
   province; `Demand\Household` with Activity Level in "Thousand Household"; Urban and Rural below
   with Activity Level in percent share, Rural = `Remainder(100)`.
2. Mapping table: per province, total → Household Activity Level in that region (value in
   thousands as given); urban share = urban ÷ total × 100 → Urban Activity Level; Rural unchanged.
3. `set_expressions` with 18 changes, scenario "Current Accounts", each naming its `region`.
4. `get_values` for two provinces, 2019, confirm; `set_notes` on `Demand\Household` with the
   source and date.
5. Report: 18 cells changed in Current Accounts, old values listed, nothing saved.
