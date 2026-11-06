---
name: leap-uncertainty
description: Run and read an uncertainty analysis in a LEAP area through the LEAP MCP tools, using LEAP's stochastic (Monte Carlo) calculation mode. Use when the user asks about "uncertainty", "Monte Carlo", "stochastic", a "probability distribution" for an input, a "confidence range" or "confidence interval", "sensitivity" of a result to its inputs, "percentiles", "how sure can we be", "best and worst case", or asks to vary an input randomly. Covers choosing which inputs to make uncertain, writing Vary expressions, switching on stochastic mode and the number of runs, calculating, reading the statistics (mean, median, percentiles) through api_set ResultsStatistic and get_values, and presenting a range honestly.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: leap_status, get_area, get_branch, find_branches, get_expression, set_expression, set_expressions, add_scenario, api_describe, api_get, api_set, calculate, cancel_calculation, get_values, show_in_leap, read_view, view_image, read_help_topic, save_area
  tested-on: "Freedonia, LEAP 2026.9.0.18, 2026-11-06 (read-only planning; no stochastic run)"
  status: draft for review
---

# Uncertainty analysis (stochastic mode)

A standard LEAP calculation is deterministic: one value per input, one value per result. In
stochastic mode you say which inputs are uncertain and how (a probability distribution), LEAP
calculates each scenario many times with a different random sample of those inputs in each run, and
every result becomes a distribution: a mean, a spread, and percentiles. LEAP's help calls this
Stochastic Modeling; users call it Monte Carlo analysis.

This skill assumes you know the area (leap-orientation), expressions (leap-expressions) and how to
read results (leap-results). Say "sample" for a value taken from a distribution, never "draw".

## When it is worth it

- Use scenarios for choices people make (a policy, a target, a technology path). Use stochastic
  mode for things nobody chooses and nobody knows exactly: growth rates, prices, costs,
  efficiencies, capacity factors, how fast a technology spreads.
- Two or three alternative scenarios ("low growth", "high growth") are often enough for a sensitivity
  question. Stochastic mode earns its cost when the user wants a probability ("how likely is it that
  emissions stay below X?"), a range with percentiles, or a ranking of which inputs matter most
  (the Uncertainty Report in LEAP).
- The cost is calculation time: every run is an ordinary calculation of every scenario marked for
  results. A hundred runs is roughly a hundred calculations, shared among the parallel workers when
  parallel calculation is on. Say this before you start.

## Step 1: Agree what is uncertain

Restate it in LEAP's terms and confirm with the user:

- **Which inputs**, named as branch and variable. Put uncertainty where it really is: a growth rate,
  a cost, an efficiency, a share, a capacity factor. Not a result calculated from them.
- **Which distribution and how wide.** If the user gives a direction but no numbers ("growth is
  uncertain"), propose a distribution and its parameters and say they are your assumption. Common
  choices: Normal for a symmetric error around a central estimate (a growth rate, an efficiency);
  Lognormal for something skewed and never below zero (costs, prices, demand levels); Triangular or
  BetaPERT for an expert's minimum, likeliest and maximum; Uniform when only a range is known;
  Discrete for a few named cases with weights.
- **Steady or year to year.** By default a Vary takes one sample per run and uses it in every year
  (a cost, an efficiency, a long-run growth rate). The "Annual" option takes a new sample every year
  (weather, hydro inflows, fuel prices); year-to-year swings partly cancel, so totals spread less.
- **Which scenario.** Vary functions can go in Current Accounts (then the historical data are
  uncertain too and the spread starts in the base year) or in a scenario. Prefer a scenario unless
  the user wants base-year uncertainty. Prefer a new scenario based on the one the user names, so
  the original stays deterministic: `add_scenario`, as in leap-build-scenario.

Then `leap_status`: `assistantAccess` must allow editing expressions. Switching the calculation mode
and the run settings is an area setting, which needs the user to let AI assistants add and edit
anything; otherwise ask the user to set it on the Calculation Mode screen.

## Step 2: Write the uncertain inputs

The function is `Vary`. Syntax, from the help topic Vary:

```
Vary(Distribution, DeterministicValue, Parameter1, Parameter2, ...)
Vary(Distribution, DeterministicValue, Parameter1, ..., "Min", Lowest, "Max", Highest, "Annual")
```

`DeterministicValue` is what a deterministic calculation uses; it may be any expression. The
parameters are numbers in the variable's units (a percent growth rate takes `3%`). The distribution
name may be quoted or not. Distributions and parameters:

| Distribution | Parameters |
|---|---|
| Normal | mean, standard deviation |
| Lognormal | mean, standard deviation (of the quantity itself) |
| Uniform | minimum, maximum |
| Triangular, BetaPERT | minimum, likeliest, maximum |
| Beta | alpha, beta |
| Exponential | mean |
| Gamma | shape, scale |
| Logistic | mean, scale |
| MaxExtreme, MinExtreme | likeliest, scale |
| Pareto | location, shape |
| StudentT | midpoint, scale, degrees of freedom |
| Weibull | shape, scale |
| Bernoulli | probability of 1 |
| Poisson | mean |
| Binomial | trials, probability |
| Discrete | value, probability, value, probability, ... (weights are scaled to add up to 1) |

Options follow the parameters as quoted words: `"Min", value` and `"Max", value` cut the
distribution off (samples come from the part that remains); `"Annual"` takes a new sample every year.

**Wrapping an existing expression.** Read it first with `get_expression`. Wrap only the number that
is uncertain, so the rest of the expression keeps its shape:

- `Growth(3%)` becomes `Growth(Vary(Normal, 3%, 3%, 0.5%))`
- `Interp(2050, 45)` becomes `Interp(2050, Vary(Triangular, 45, 40, 45, 55))`
- A cost of `1200` becomes `Vary(Lognormal, 1200, 1200, 300, "Min", 800, "Annual")`
- `Vary(Discrete, 3%, 2%, 25, 3%, 50, 4%, 25)` gives 2%, 3% or 4% with weights a quarter, a half, a quarter.
- A scenario expression that scales the baseline: `BaselineValue * Vary(Normal, 1, 1, 0.1)`.

In a deterministic calculation a Vary gives its deterministic value, so results do not change until
stochastic mode is on. That is also the check after entry: `get_values` in the scenario should give
the numbers it gave before the edit.

**Inputs that move together.** Wrap each one in `VaryGroup("GroupName", Expression)`, exactly as
the help gives it. The Vary functions inside the expression are tied to the group: every Vary in
the area under the same group name takes the same percentile in a run, so related fuel prices or
the costs of similar technologies rise and fall together. The help's example: `VaryGroup("Fuel
prices", Vary(Lognormal, 80, 80, 20))` on one branch and `VaryGroup("Fuel prices", Vary(Lognormal,
12, 12, 4))` on another move together. `VaryGroup("GroupName", -1, Expression)` makes the input
move the other way: high when the others are low.

A worked case: the user says an industrial sector's intensities "could be 1% a year better or
worse", and the scenario inherits them flat from Current Accounts. Write
`Growth(VaryGroup("Industry intensity", Vary(Uniform, 0%, -1%, 1%)))` on each intensity, so one
sample moves the whole sector; or put the rate on one Key Assumption and refer to it from each
intensity. An input used in many places needs no group: put it on a Key Assumption branch and
refer to it, and one sample reaches every place.

When the user says "anywhere between", Uniform is the literal reading: every value in the range is
equally likely. Say so, and offer Triangular if the middle value is likelier.

Enter the expressions with `set_expressions` in one call, scenario set to the scenario agreed. In
LEAP itself the user can do the same with the Uncertainty Wizard (Ctrl+Alt+U on an expression),
which draws the distribution; mention it when the user is at the keyboard.

### What to vary and what not to

- **Shares that must sum to 100:** vary at most one or two and leave `Remainder(100)` on another, so
  the set still sums to 100 in every run. Never put a Vary on every share. Cut the distribution off
  with `"Min", 0` and `"Max", 100` so a sample cannot push a share out of range; a run in which a
  share goes below 0 fails and is left out of the statistics.
- **Current Accounts:** leave it deterministic unless the user asks for uncertain historical data.
- **A result or an intermediate:** no; its spread follows from the inputs.
- **One input that drives many things:** vary the Key Assumption the expressions refer to (check with
  `get_expression` that they do), not each place it is used.
- The older `Random`, `RandomLowerUpper`, `TrueRandom` and `RandomInteger` functions are not
  uncertainty analysis: they give one random value per cell with no statistics behind it. Use Vary.

## Step 3: Switch on stochastic mode

In LEAP: General menu, Calculation Mode (also a button on the main toolbar and a pane of the status
bar). Type of Calculation: Stochastic. Runs: Maximum runs per scenario (default 100); Keep results
of every run (on by default; needed for histograms, cumulative charts and the Uncertainty Report).
Sampling: Monte Carlo or Latin Hypercube (fewer runs for the same precision, with a set number of
runs only). Stop Calculations: after the maximum runs, or when every forecast has converged (the
mean of each listed result known to a precision, default 2%, at 90, 95 or 99% confidence, between a
minimum and the maximum runs). These settings are saved with the area, and changing them marks
results out of date.

Through the tools the same settings are area settings. Read the current ones first with `api_get`:
`AreaSetting("StochasticMode")`, `AreaSetting("StochasticRuns")`, `AreaSetting("StochasticKeepRuns")`,
`AreaSetting("StochasticSampling")` (0 Monte Carlo, 1 Latin Hypercube),
`AreaSetting("StochasticStopRule")`, and `api_get` `ResultsStatistic`. The full list of setting
names is in the help topic API/API_AreaSettings.htm (`read_help_topic`), not in `api_describe`.
Changing them needs `api_set`, "edit anything" access and the user's agreement:

- `api_set` `AreaSetting("StochasticMode")` = true
- `AreaSetting("StochasticRuns")` = the maximum runs (default 100)
- `AreaSetting("StochasticKeepRuns")`, `AreaSetting("StochasticSampling")` (0 Monte Carlo, 1 Latin
  Hypercube), `AreaSetting("StochasticStopRule")` (0 fixed runs, 1 until converged),
  `AreaSetting("StochasticPrecision")`, `AreaSetting("StochasticConfidence")`,
  `AreaSetting("StochasticMinRuns")`. The forecasts for the converge rule
  (`StochasticForecasts`) are stored as IDs: ask the user to choose them on the screen.

How many runs: a few hundred are usually enough for means and the middle percentiles; the 5th and
95th percentiles need more. Start with the default 100 to check that everything works, then raise it.
Latin Hypercube settles with fewer runs.

Each scenario has a Random Seed, a variable on the area (top) branch set per scenario. The same
seed gives the same samples again, so a calculation repeats exactly; change it to see a different
set of runs. (Unverified: whether `set_expression` can reach the Random Seed through the tools;
the user can change it in the Analysis view.)

## Step 4: Calculate

Tell the user how long to expect. A run of N samples costs N + 1 calculations (the deterministic
pass plus N samples) of every scenario marked for results. The tools do not report how long one
calculation takes (`leap_status` gives only when the area was last calculated): ask the user, or
time one deterministic calculation first. Check `api_get` `AreaSetting("ParallelEnabled")`: when it
is false the speed-up from parallel calculation does not apply (when it is on, one run is one part
per scenario and region, shared among the workers). `calculate`, then
`leap_status` every few seconds. `calculation` reports `percentDone`, `mode` (parallel, with
`partsDone` of `partsTotal`, or serial), and `secondsSoFar`. Between batches of runs LEAP may
report serial for a moment; that is bookkeeping, not a recalculation. LEAP's own progress window
shows "Runs completed: N of up to M". If LEAP shows a message, the user has to answer it. If the
user needs LEAP back, `cancel_calculation`.

`get_area` does not list the runs: they are temporary scenarios LEAP makes and removes itself. The
scenarios you see are the ones that have statistics.

## Step 5: Read the results

After a stochastic calculation every result exists at these statistics: Deterministic (the
ordinary result), Mean, Median, Standard Deviation, Minimum, Maximum, and the 5th, 10th, 25th,
75th, 90th and 95th percentiles. A base year is the same in every run and shows its deterministic
value whatever statistic is chosen.

**Numbers in the conversation.** `get_values` reads a result in a scenario with runs at the
statistic in `LEAP.ResultsStatistic` (Deterministic by default; a scenario without runs gives its
ordinary result; the `filter` cannot choose a statistic). So:

1. `api_set` path `ResultsStatistic`, value one of: Deterministic, Mean, Standard Deviation,
   Minimum, Maximum, 5th Percentile, 10th Percentile, 25th Percentile, Median, 75th Percentile,
   90th Percentile, 95th Percentile. It is refused while LEAP is calculating or a supporting
   screen is open. It also changes what the Energy Balance, Sankey and Summaries show.
2. `get_values` for the result, scenarios and years you need.
3. Repeat for each statistic you report (at least Median or Mean, 5th and 95th Percentile).
4. Set `ResultsStatistic` back to Deterministic when done. Say so to the user.

Results of a single run are not exposed through the tools (unverified: no tool or API member reads
one run was found). LEAP's Uncertainty Report and histogram read the kept runs.

**On screen in LEAP.** `show_in_leap` with `view` Results, the result variable, `x_axis` Years,
`legend` Statistic (unverified name for the legend; the help says Statistic is a dimension that can
go on the X axis or the legend). Then `api_set` `ChartOption("ChartType")` = Fan (bands between the
5th and 95th and the 25th and 75th percentiles around the median), BoxPlot, Histogram or Cumulative
(the last two need the kept runs and show one result's spread over the runs in the last year
shown). `ChartOption("Statistic")` chooses one statistic for an ordinary chart (Deterministic, Mean,
StdDev, Min, Max, P5, P10, P25, Median, P75, P90, P95); it can only be set while the Results view is
showing. Check with `read_view` or `view_image`. A statistic of a total is the sum of its parts'
statistics, exact for the mean and approximate for the others; the chart's Advanced menu, Spread
Statistics, can read every kept run instead (slower).

**Which inputs matter.** The Uncertainty Report (Advanced menu in the Results View) ranks every
Vary by its rank correlation with a result and gives each input's share of variance, with a scatter
page. It is not reachable through the tools; tell the user where it is and what to look at.

## Step 6: Present a distribution honestly

- Give a range, not a number: "In 2050 Baseline emissions are 10.2 Mt CO2e (median), with a 90%
  range of 8.9 to 11.8 Mt (5th to 95th percentile), against 10.1 Mt deterministic." Name the
  statistic every time; never let a mean stand in for "the result".
- Say how many runs, which inputs were varied, with which distributions, and which numbers were the
  user's and which were your assumptions. The range is only as good as those assumptions.
- For a comparison of scenarios, compare the same statistic in both, and say that a scenario
  inherits its parent's samples unless its seed differs, so the difference between them is steadier
  than either level.
- A percentile of a difference or of a total is not the difference or sum of percentiles; say
  "about" unless the exact-spread option was used.
- The mean can differ from the deterministic value with skewed distributions (Lognormal); that is
  expected, not an error.
- Do not call it a sensitivity analysis of the whole model: only the inputs with a Vary vary.

## Common mistakes

- Running stochastic mode with no Vary anywhere: every run is identical and every statistic equals
  the deterministic value. Check with `get_expression` that at least one Vary is in a calculated scenario.
- Forgetting to set `ResultsStatistic` back: later deterministic readings come out as means.
- Reading results while stale: `leap_status` must say results are up to date. Changing any
  calculation-mode setting makes them out of date.
- A standard deviation in the wrong unit (0.5 instead of 0.5% on a growth rate).
- Varying a share without a `Remainder(100)` partner or without cut-offs.
- Putting a Vary on a cell that already refers to another varied cell (a natural gas intensity
  written as 90% of the coal one), so the input is varied twice.
- Too few runs for tail percentiles: 100 runs give a rough 5th and 95th percentile.

## Example (Freedonia)

Freedonia: base year 2020, first scenario year 2021, end year 2050, scenarios Baseline and
Mitigation. User: "How uncertain are Baseline emissions in 2050 if household growth and the oil
price are uncertain?" (The household cell and the result below were checked against the sample
area; confirm the oil price branch with `find_branches` and `get_branch`.)

1. `leap_status`: access allows editing; `get_area`: Baseline is the first scenario.
2. `add_scenario` "Baseline Uncertain", based_on Baseline, abbreviation "BASU".
3. `find_branches` "Household": the cell is `Demand\Household`, Activity Level, where
   `get_expression` gives `Growth(3%)` entered in Baseline (Key\Households is not referenced
   there). `find_branches` the crude oil or oil product resource whose cost or price variable the
   user means; `get_expression` gives, say, `80`.
4. `set_expressions` in "Baseline Uncertain": the household Activity Level `Growth(Vary(Normal, 3%,
   3%, 0.5%))`; the price `Vary(Lognormal, 80, 80, 20, "Annual")`. Read back 2030 and 2050 with
   `get_values`: unchanged from Baseline (deterministic values). If the user also wants industrial
   intensities uncertain: Freedonia's industrial intensities are flat Current Accounts values in
   Baseline, so a `Growth(VaryGroup(...))` as in Step 2 is the form; and Iron and Steel's Natural
   Gas intensity is written as 90% of its Coal neighbor, so a Vary belongs on Coal only.
5. Calculation Mode: Stochastic, 200 runs, Latin Hypercube, keep runs. Through `api_set`
   `AreaSetting("StochasticMode")` = true, `AreaSetting("StochasticRuns")` = 200,
   `AreaSetting("StochasticSampling")` = 1 if access allows; otherwise the user sets them.
6. Tell the user: 201 Freedonia calculations (one deterministic plus 200 samples) of each scenario
   marked for results; ask how long one takes, or time one first. `calculate`; `leap_status` until
   done.
7. `api_set` `ResultsStatistic` = Median; `get_values` the result One_Hundred Year GWP Direct At
   Point of Emissions at the root branch "Freedonia", unit Million Metric Tonnes (99.5 in 2050 in the
   deterministic Baseline), scenario "Baseline Uncertain", 2030 and 2050. Repeat for 5th Percentile,
   95th Percentile and Mean; then set Deterministic and read it once more.
8. Report: "2050 Baseline emissions: median A Mt CO2e, 90% range B to C, deterministic D, from 200
   runs with household growth Normal(3%, 0.5%) and oil price Lognormal(80, 20) sampled yearly;
   the distributions are my assumptions." Then `show_in_leap` the fan chart and
   `read_view` to confirm. Point the user to the Uncertainty Report for which input mattered more.
9. Set `ResultsStatistic` back to Deterministic. Nothing is saved; ask before `save_area`.
