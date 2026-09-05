# Home Assistant Dashboards

A small collection of Home Assistant Lovelace dashboards, shared as plain
YAML you can paste directly into the dashboard editor.

## Usage

1. In Home Assistant, go to **Settings > Dashboards > + Add Dashboard >
   New dashboard from scratch**, give it a name, and open it.
2. Click the three-dot menu (top right) > **Edit Dashboard**, then the
   three-dot menu again > **Raw configuration editor**.
3. Delete the placeholder content and paste in the full contents of the
   `.yaml` file you want.
4. Save.

Each dashboard relies on a few [HACS](https://hacs.xyz/) frontend cards.
Install these via HACS before pasting the config, or the corresponding
cards will show as "custom element doesn't exist":

- [card-mod](https://github.com/thomasloven/lovelace-card-mod)
- [bootstrap-grid-card](https://github.com/luca77-fs/bootstrap-grid-card)
- [clock-weather-card](https://github.com/pkissling/clock-weather-card)
- [weather-chart-card](https://github.com/mlamberts78/weather-chart-card)
- [week-planner-card](https://github.com/rejuvenate/lovelace-week-planner-card)
- [button-card](https://github.com/custom-cards/button-card)
- [html-template-card](https://github.com/PiotrMachowski/Home-Assistant-Lovelace-HTML-Jinja2-Template-card)
- [browser_mod](https://github.com/thomasloven/hass-browser_mod) (used for
  the camera popup; the button still works without it if you strip the
  `tap_action`)

Entity IDs in these dashboards (calendars, lights, cameras, sensors) are
placeholders — swap them for your own before use.

## Dashboards

- [`dashboards/family_calendar.yaml`](dashboards/family_calendar.yaml) —
  wall-mounted kiosk dashboard: weather header, a meal-plan strip pulling
  from a [Tandoor](https://github.com/TandoorRecipes/recipes) instance, a
  multi-calendar week view, and a small pinned button bar (camera feed
  popup + a light toggle) that stays fixed to the bottom-left corner while
  the rest of the page scrolls.
