# Home Assistant Dashboards & Integrations

A small collection of Home Assistant Lovelace dashboards (shared as plain
YAML you can paste directly into the dashboard editor) and a custom
integration for the [Tandoor](https://github.com/TandoorRecipes/recipes)
recipe manager.

## Dashboards

### Usage

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
- [browser_mod](https://github.com/thomasloven/hass-browser_mod) — used for
  the camera feed popup and for showing recipe details as an in-app popup
  (`window.browser_mod.showPopup(...)`, not a Lovelace `tap_action`, so it's
  a hard requirement rather than optional here)

Entity IDs in these dashboards (calendars, lights, cameras, sensors) are
placeholders — swap them for your own before use. `sensor.tandoor_meal_plan`
and `todo.tandoor_shopping_list` match the entity IDs the
`tandoor_meal_plan` integration below creates by default.

### `dashboards/family_calendar.yaml`
<img width="1546" height="868" alt="image" src="https://github.com/user-attachments/assets/fb40037c-2d29-4646-9324-834060c39323" />

Wall-mounted kiosk dashboard: weather header, a meal-plan strip pulling from
a Tandoor instance, a multi-calendar week view, and a small button bar
(camera feed popup + a light toggle) pinned to the bottom-left corner via
`position: fixed` on each button, independent of page scroll.

Clicking a meal opens its recipe (image, servings/time, ingredients, steps)
as a native in-app popup built from data already on the `meals` attribute —
no iframe, so it isn't affected by the recipe site's own `X-Frame-Options`
header, and no external site ever gets embedded.

## Integrations

### `integrations/tandoor_meal_plan/`

A Home Assistant integration for Tandoor, configured entirely through the
UI (**Settings > Devices & Services > Add Integration > Tandoor Meal
Plan**, then enter your Tandoor URL and an API token) — no YAML, and the
token is stored in HA's encrypted config-entry storage rather than a
plaintext script.

Provides:

- `sensor.tandoor_meal_plan` — count of meals in the next 7 days, with a
  `meals` attribute (each entry's `recipe` includes image, servings,
  working/waiting time, and full steps/ingredients) for building a
  meal-plan display like the one in `family_calendar.yaml`.
- `sensor.tandoor_recipes` — total recipe count, with a `recipes` attribute
  listing name/rating/last-cooked for the first page of results.
- `todo.tandoor_shopping_list` — Tandoor's shopping list as a native HA
  to-do list: add, check off, or delete items from HA, a dashboard, or a
  voice assistant, synced back to Tandoor.
- `tandoor_meal_plan.search_recipes` service — fuzzy-search recipes by
  name; returns matches for use in scripts/automations.

Install by copying `integrations/tandoor_meal_plan/` into your HA config's
`custom_components/` directory (that exact name is required — Home
Assistant's component loader looks for it specifically), restart HA, then
add the integration via the UI as above.
