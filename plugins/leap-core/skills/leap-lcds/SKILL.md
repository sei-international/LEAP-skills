---
name: leap-lcds
description: Find and use data from the LEAP Cloud Data Server (LCDS), SEI's online store of open national statistics for energy and emissions modeling. Use when the user wants population, GDP, urbanization, energy balance statistics, emissions, degree days or development indicators for a country brought into a LEAP area, asks what data the LCDS holds, or wants to query the LCDS directly. Covers the data sets, how to list them and their series and dimensions through the LCDS web service, how to retrieve a series as JSON, and how to write the matching LEAP expression.
metadata:
  author: Stockholm Environment Institute
  leap-version: "2026.9 or later"
  mcp-tools: set_expression, get_values, get_notes, get_branch, api_get, search_help
  tested-on: Freedonia (sample area); live server checked 2026-11-06
  status: draft for review
---

# The LEAP Cloud Data Server

The LCDS is a web service at `https://leap.sei.org/dataserver/dataserver.dll` that answers plain
web requests with JSON. LEAP's Time-Series Wizard uses it, and a LEAP expression can refer to it
directly, so a model stays linked to the source. Anyone can query it; no key is needed. It is read
only. Its own help page is the server address with nothing after it.

Data come back in the data set's own unit and scale, by country, as yearly values. Everything is
national: one three-letter ISO code per request.

## The data sets (as the server listed them on 2026-11-06)

| Set | What it holds | Years | Series | Extra dimensions | Unit |
|---|---|---|---|---|---|
| `UNPopulation` | U.N. World Population Prospects 2019 | 1950–2100 | none | Dim1 Variant: Low, Medium, High | Thousand Person |
| `UNUrbanization` | U.N. World Urbanization Prospects 2018: urban share | 1950–2063 | none | none | Share (%) |
| `GDP` | GDP PPP, constant 2017 international $, history plus SSP projections (World Bank, IMF, OECD, SEI) | 1990–2100 | none | Dim1 Scenario: SSP1 … SSP5 | Billion U.S. Dollar |
| `WDI` | World Bank World Development Indicators | 1960–2023 | indicator code, e.g. `EN.CO2.TRAN.ZS` | none | varies by series |
| `UNEnergy` | U.N. Energy Statistics Database 2019 | 1970–2020 | `Energy` (TJ), `Physical`, `Share` | Dim1 FlowCode (e.g. `01` Production, `015EE` main-activity electricity plants); Dim2 ProductCode (fuel) | by series |
| `EDGAR` | JRC/PBL emissions database | 1970–2019 | IPCC sector code, e.g. `1A3b` Road transportation | Dim1 Compound (gas) | Thousand Metric Tonne |
| `IDEES` | JRC-IDEES 2021, EU member states, disaggregated energy, activity and emissions | 2000–2021 | series name, e.g. `Activity.Mpkm.Tr.Road.Passenger.Car` | none | by series |
| `GDL` | Global Data Lab Area Database 4.0 | 1992–2020 | indicator | Dim1 Region (subnational) | varies |
| `Cooling` | Cooling degree days vs 18.3 °C with change to 2050 (KAPSARC, World Bank) | 2015–2050 | none | none | degree days |
| `Heating` | Heating degree days vs 18.3 °C (KAPSARC, World Bank) | 1995–2015 | none | none | degree days |

The list can change. Always ask the server (`/DataSets`) before telling the user what exists, and
ask `/Info` for the series and dimension codes of a set rather than guessing them.

## The web service

All requests are GET; parameter names are not case sensitive. Add `&Pretty` for a readable HTML
page instead of JSON. LEAP adds a `UID` parameter identifying the user; a request without it works.

| Request | Parameters | Returns |
|---|---|---|
| `/DataSets` | none | `{"DataSets":[{Set, Title, Publisher, PubYear, URL, YearsCovered, FirstYear, LastYear, Series, "1st Extra Dimension", "2nd Extra Dimension", Units, LastUpdate}, ...]}` |
| `/List` | none | `{"DataSets":[{"Set":"..."}, ...]}`: names only |
| `/Info` | `SET` | the set's description plus `Series` (list of `{Name, Description}`) where the set has series, and `Dim1s` / `Dim2s` (lists of `{Name, Description}`) where it has extra dimensions |
| `/Countries` | none | `{"Countries":[{ISO3, ShortName, LongName}, ...]}` |
| `/Data` | `SET`, `ISO3`, and `SERIES`, `DIM1`, `DIM2` as the set requires | the set's description, `Units`, `ISO3`, the codes used, `QueryID`, and `Data`: a list of `{Year, Value}` |

Examples:

```
https://leap.sei.org/dataserver/dataserver.dll/DataSets?Pretty
https://leap.sei.org/dataserver/dataserver.dll/Info?SET=UNEnergy
https://leap.sei.org/dataserver/dataserver.dll/Data?SET=UNPopulation&ISO3=GHA&DIM1=Medium
https://leap.sei.org/dataserver/dataserver.dll/Data?SET=WDI&ISO3=USA&SERIES=EN.CO2.TRAN.ZS
https://leap.sei.org/dataserver/dataserver.dll/Data?SET=UNEnergy&ISO3=KEN&SERIES=Energy&DIM1=015EE&DIM2=EL
https://leap.sei.org/dataserver/dataserver.dll/Data?SET=GDP&ISO3=CHN&DIM1=SSP2
```

Errors come back as HTTP 400 with the body `Bad Request` and nothing more, whatever the cause
(unknown set, missing or invalid ISO3, a series or dimension missing where the set needs one or
given where it does not, an unknown code). Check SET, ISO3 and each code against `/Info` yourself.
A valid request for which the country has no data returns 200 with an empty `Data` list, not an
error. Parameter names and values are both case-insensitive. `Info` for `WDI` and `UNEnergy` is
long (thousands of codes); search it for the user's words rather than showing it.

The `Fetched` and `LastUpdate` fields are dates as day numbers. `YearsCovered` is the data set's
range, not the series': read the first and last `Year` in `Data` (some WDI series stop years
earlier than the set; the Heating set prints its range backwards). Years with no value are simply
absent from `Data`.

Useful codes seen: `UNEnergy` final consumption is flow `12` (total), `1231` (households), with
product `EL` for total electricity; `WDI` `EG.USE.ELEC.KH.PC` is electricity use per person but is
sparse for many countries. Neither holds projections of energy use.

## Working through the steps

1. **Find the set and the codes.** `/DataSets` for the candidates; `/Info?SET=...` for the exact
   series and dimension codes; `/Countries` if the country code is uncertain. Match the user's
   words to a `Description`, and show them the code and description you chose.
2. **Look at the data first.** `/Data` with the full parameters. Check the years, the unit, gaps,
   and whether the numbers are plausible for the country. Tell the user the source line (Title,
   Publisher, PubYear, URL) the server gives.
3. **Match the LEAP variable.** `get_branch` with the scenario for the target variable's unit,
   scale and present expression, and look for variables computed from it: a formula such as
   Households × Household Size must be reworked (Households = Population ÷ Household Size), not
   overwritten. The LCDS value arrives in the set's unit (Thousand Person, Billion U.S. Dollar,
   TJ, ...). Either the variable uses the same unit and scale, or the expression converts
   (`/ 1000`, `ConvUnits`), with the reason in the notes. Say which you did.
4. **Write the expression** (leap-expressions, section 11):

   ```
   Interp(LCDS, DataSet [, Series] [, Dim1 [, Dim2]] [, ISO3] [, GrowthRate])
   ```

   Give the arguments the set needs, in the order series, Dim1, Dim2, as `/Info` lists them.
   Always give `ISO3` unless the user confirms that the area is national with a country set in
   Settings: Scope, or multi-national with regions mapped to countries (then the same expression
   works in every region); the tools do not report the area's scope. The trailing growth rate is
   accepted by LEAP's Time-Series Wizard although the Interp help topic does not list it for the
   LCDS form. `Step`, `Data`, `Smooth`
   and the forecast functions take the same arguments. Historical statistics go in Current
   Accounts (`Data` or `Interp`); projections such as `UNPopulation` or `GDP` suit a baseline
   scenario, with `InterpFSY` when Current Accounts holds several years.
5. **Enter and check.** `set_expression`; LEAP fetches and caches the series. `get_values` for
   three years and compare with the `/Data` answer. If the expression is refused, the reason
   usually names the code the server rejected; correct it from `/Info`.
6. **Document.** When the user links a series through LEAP's Time-Series Wizard, LEAP adds the
   server's source notes to the branch notes. Whether `set_expression` does the same is
   unverified: read `get_notes` afterwards and, if the source line is missing, add it with
   `set_notes` with the user's agreement.

## Rules

- Never invent a series or flow code; always read it from `/Info`.
- Say the unit and scale of what you bring in, and what the LEAP variable expects.
- Say that a linked expression depends on the LCDS being reachable the first time it is evaluated
  (afterwards it is cached) and that the data have a publication year; the user decides whether a
  live link or typed numbers suit them.
- The LCDS is SEI's service: if it does not answer, say so plainly and offer typed numbers from
  the `/Data` answer you already have, or from the user's own source.

## Example

User: "Use U.N. medium population for Kenya as the driver in Key Assumptions."

1. `/Info?SET=UNPopulation` → Dim1s Low, Medium, High; Units Thousand Person; years 1950–2100.
2. `/Data?SET=UNPopulation&ISO3=KEN&DIM1=Medium` → 2019 ≈ 52,574 (thousand), 2050 ≈ 91,575.
3. `get_branch` `Key Assumptions\Population` → Activity Level in Million People.
4. Current Accounts: `Interp(LCDS, UNPopulation, Medium, KEN) / 1000` (thousand → million), or
   change the variable's scale to Thousand with the user's agreement and drop the division.
   Baseline: inherits; or `InterpFSY(LCDS, UNPopulation, Medium, KEN) / 1000` if Current
   Accounts holds several years.
5. `get_values` 2019, 2030, 2050 → matches the server's numbers divided by 1000. `set_notes` with
   "U.N. World Population Prospects 2019, medium variant, via LCDS, retrieved 2026-11-06".
