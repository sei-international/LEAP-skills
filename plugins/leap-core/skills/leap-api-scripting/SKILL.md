---
name: leap-api-scripting
description: Help a LEAP user automate LEAP with its programming interface (API): write or fix a VBScript or Python script for LEAP's Script Editor or for running outside LEAP, reach parts of the area the MCP tools do not cover through api_describe, api_get, api_set and api_call, or explain an API member. Use when the user mentions scripts, VBScript, Python, the Script Editor, COM, automation, batch runs, or asks for something no other tool does (time slices, tags, units, effects, user variables, settings, versions, bulk structural changes).
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: api_describe, api_get, api_set, api_call, search_help, read_help_topic, help_contents
  tested-on: Freedonia (sample area)
  status: draft for review
---

# LEAP's API and scripts

LEAP is a COM automation server. The same objects, properties and methods are available from
VBScript and Python inside LEAP's Script Editor, from a script or program outside LEAP, and, read
or written one at a time, through the `api_*` MCP tools. The help section "Automation Using the
API and AI Assistants" has one topic per class and member, with examples in both languages; the
sample scripts APIFullTest.vbs and APIFullTest.py in the common scripts folder exercise most of it.

## Two different jobs

1. **Reach something the other tools do not cover, now.** Use `api_describe` to find the member,
   then `api_get` (read), `api_set` (one property) or `api_call` (one method). You can do this
   yourself, within the user's access level.
2. **Write a script the user will run.** Use `api_describe` and the help as the reference, and give
   the user a complete script. The MCP tools cannot run scripts; the user runs it in the Script
   Editor (Advanced: Edit Scripts) or from their own Python or Windows Script Host.

## Finding members

- `api_describe` with no object lists the object types; with `object` (for example `Branch`,
  `Variable`, `Scenario`, `Fuels`, `TimeSlices`) lists its properties and methods, with
  `writableWithApiSet` and `callableWithApiCall` flags; `filter` narrows by name or text (a
  `filter` without `object` only returns the object list again, with a note).
- `api_get` path syntax: steps separated by dots, text arguments in double quotes:
  `Branches("Demand\Household").Variables("Activity Level").Expression`,
  `Fuels("Electricity").Density`, `AreaSetting("DiscountRate")`, `TimeSlices(3)`. An empty path
  describes the LEAP object. Ending at an object returns its simple properties and the names of the
  ones that lead on.
- Read the help topic of a member before relying on it: `search_help` with the member's name.
- **Reading many items.** `api_get` on a collection (`TimeSlices`, `Fuels`, `Scenarios`) lists
  index, ID and name only. Per-item properties need one call each: `TimeSlices(3)` for the whole
  object, or `Fuels("Wood").EnergyContent` for one property. The last time slice's
  `CumulativeHours` is the total hours. `list_fuels` gives the fuels a branch uses; `Fuels` holds
  every fuel in the area. Some properties come back as text (EnergyContent with its unit);
  settings such as `AreaSetting("DiscountRate")` come back as a bare number, with the unit in the
  help's Area Settings table.
- `Milestones` (the milestones drawn on Results charts: `Add`, `Delete`, `Item`, `Exists`,
  `Count`; each with Name, Year, Scenario, Region, Branch, Position, Hidden, Groups, Notes) is a
  collection like the others; the get_milestones, set_milestone and delete_milestone tools cover
  the usual cases.
- A branch's variable can be reached as `Branches("path").Variables("name")`,
  `Branch("path").Variable("name")` or `BranchVariable("path:name")`; its `Expression` follows
  the scenario selected in LEAP (a script sets `ActiveScenario` first; for a named scenario the
  `get_expression` tool, or `ExpressionRS`). Result variable names come
  from `get_branch` (`Final Energy Demand`, not older names in the help); a result's unit is in
  `DefaultResultUnit`.

## Using api_set and api_call

- `api_set` writes display properties at every access level (ActiveView, ActiveScenario,
  ActiveYear, ChartOption("name") ...) and area data (names, fuel properties, settings, years)
  only with "edit anything" access. `show_in_leap` covers the common display cases in one call.
- `api_call` runs display methods and question methods at every level (`Favorites("x").Activate()`,
  `ChartOptionNames("json")`, `CheckLegalName("...")`, `Fuels.Exists("Coal")`), and, with "edit
  anything", methods that change the area (`Fuels.Add(...)`, `AddBranch(...)`,
  `Branches("...").Delete()`, `MoveUp()`).
- Wrap many changes in `BeginBulkUpdate()` ... `EndBulkUpdate()` so LEAP refreshes once.
- Refused: saving, opening or deleting areas, versions, printing, exporting, anything that names or
  runs a script, deprecated members. Say so rather than hunting for a way round.
- Every change is logged (`get_changes`) and is not saved until the user saves.

## Writing a script for the user

Settle what the user has not already said: inside LEAP or outside; VBScript or Python; which
area; what it must produce (a file, a printout, changed data). Then:

- **Inside the Script Editor**: an object named `LEAP` already exists; `LEAP.Print` (VBScript) or
  `print` (Python) writes to the output pane; API constants such as `acSilent` are available by
  name. Python files use the extension `.pys` (or choose Python as the language); LEAP ships its own
  Python.
- **Outside LEAP**: create the object and wait for it to start:

  ```vbscript
  Set LEAP = CreateObject("LEAP.LEAPApplication")
  Do Until LEAP.ProgramStarted : WScript.Sleep 500 : Loop
  LEAP.Verbose = 1            ' errors shown, questions and messages not
  LEAP.Visible = True
  LEAP.ActiveArea = "Freedonia"
  ```

  ```python
  import comtypes.client, time
  LEAP = comtypes.client.CreateObject("LEAP.LEAPApplication")
  while not LEAP.ProgramStarted:
      time.sleep(0.5)
  LEAP.Verbose = 1
  LEAP.Visible = True
  LEAP.ActiveArea = "Freedonia"
  ```

  If LEAP is already running, CreateObject joins it. Finish by leaving LEAP open or calling
  `LEAP.Quit` after checking `LEAP.CanQuit`. NEMO optimization is not available in a LEAP started
  by a script.
- **VBScript habits**: `Set` for objects, none for values; `Dim` is optional; `&` joins text;
  errors stop the script unless `On Error Resume Next`, and `LEAP.Verbose` decides whether LEAP
  shows them.
- **Python habits**: raw strings for branch paths (`r"Demand\Household"`); properties that take
  arguments are read with a call (`B.Parent()`) and assigned with square brackets
  (`V.ExpressionRS[1, "Baseline"] = "Growth(3%)"`).
- **Typical read loop**: `for S in LEAP.Scenarios:` works in the Script Editor's Python (and
  `For Each S In LEAP.Scenarios` in VBScript); an index loop from 1 to `Count` works everywhere.
  `Scenarios` includes Current Accounts (`S.IsCurrentAccounts`); `S.ResultsShown` is "marked for
  calculation" (`includedInResults` in `get_area`). Read with `V.ValueRS(region, scenario, year)`,
  which names the scenario and leaves the user's view alone; setting `LEAP.ActiveScenario`
  redraws the Results view and is for edits, not reads.
- **Typical edit loop**: set `LEAP.ActiveScenario`, change expressions through
  `LEAP.Branch(path).Variable(name).Expression` (or `ExpressionRS` for a region and scenario),
  `LEAP.Calculate()`, then read `ValueRS`, and write to a file or Excel.
- Always include: a comment at the top saying what the script does and which area it expects;
  a check that the right area is open; `BeginBulkUpdate`/`EndBulkUpdate` around many edits; no
  saving unless the user asked, and then `LEAP.SaveArea` once at the end.
- Tell the user the script has not been run by you, what it will change, and to run it on a copy
  of the area first (the sample scripts add and delete branches as they go).

## Explaining a member

Give the signature, what it returns, when it may be used (Current Accounts or scenarios, access
level), one example in the language the user uses, and the help link.

## Common mistakes

- Paths without double quotes around text, or with forward slashes.
- Assuming a member exists because it does in another version; `api_describe` is the truth for
  this LEAP.
- Writing to a property that is read-only (the flags in `api_describe` say).
- Mixing `Value` (active scenario and region), `ValueR` and `ValueRS`.
- Forgetting that `Expression` set through the API is checked like any expression and refused when
  invalid, with the reason in the error.
- A script that saves the area without the user asking.

## Example

User: "List every time slice with its hours, and tell me if they sum to 8760."

1. `api_describe` object `TimeSlice` → properties Name, Hours, CumulativeHours (and others).
2. `api_get` `TimeSlices` → names and IDs only; then `api_get` `TimeSlices(1)` ... `TimeSlices(9)`
   for Hours (the last slice's CumulativeHours gives the total).
3. Sum and report; if the user wants it as a script, give the Python loop
   `for TS in LEAP.TimeSlices: print(TS.Name, TS.Hours)` with a running total.
