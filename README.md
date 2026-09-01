# Mopeka Quality Filter for Home Assistant

A HACS-installable custom integration based on Home Assistant's built-in **Mopeka** Bluetooth integration, with a configurable minimum reading-quality threshold.

This integration uses its own `mopeka_quality` domain, so it can coexist with Home Assistant Core's built-in `mopeka` integration instead of overriding it.

## Features

- Based on the current Home Assistant Core Mopeka integration.
- Separate `mopeka_quality` domain.
- Passive Bluetooth discovery and UI configuration.
- Configurable tank medium type.
- Configurable **Required quality %** (0–100, default **100%**).
- Sensor readings below the configured quality threshold become `unknown`.
- The `reading_quality` diagnostic sensor remains available so rejected readings can be diagnosed.
- HACS-compatible repository layout and validation workflow.
- Automated semantic patch releases with `manifest.json` kept in sync with the GitHub release version.
- Tests for configuration, filtering, migration, domain identity, and release version handling.

## Reading quality behavior

Mopeka reports reading quality as 0%, 33%, 67%, or 100%. A measurement is accepted when its `reading_quality` is **at least** the configured Required quality %. The default of 100% therefore accepts only 100%-quality measurements.

The `reading_quality` sensor itself is never filtered. All other values from the same advertisement are set to `unknown` when the quality is below the threshold.

## Installation with HACS

1. Open HACS.
2. Add `https://github.com/danfulton72/mopeka_custom_component` as a **Custom repository** of type **Integration**.
3. Install **Mopeka Quality Filter**.
4. Restart Home Assistant.
5. Go to **Settings → Devices & services** and configure/discover your Mopeka sensor under **Mopeka Quality Filter**.
6. Use the integration's **Configure** action to change the medium or Required quality %.

## Manual installation

Copy `custom_components/mopeka_quality` into your Home Assistant configuration directory as:

```text
/config/custom_components/mopeka_quality
```

Restart Home Assistant.

## Domain migration note

Home Assistant config entries are bound to their integration domain. Entries created by an earlier build that used the `mopeka` domain are not automatically reassigned to `mopeka_quality`; remove/re-add that custom integration entry after upgrading to this domain-renamed release.

## Development

Create a virtual environment and install the test dependencies:

```bash
python -m pip install -r requirements_test.txt
pytest
```

The CI workflow also runs Hassfest and the HACS validation action.

## Releases

Every merged pull request to `main` runs the release workflow. The workflow:

1. Reads the latest GitHub release tag (the source of truth).
2. Increments the patch component (`x.y.z` → `x.y.(z+1)`).
3. Writes that exact version to `custom_components/mopeka_quality/manifest.json`.
4. Commits the manifest update.
5. Tags the release commit and creates the matching GitHub release with generated notes.

If no GitHub release exists yet, the baseline is `0.0.0`, so the first merged pull request creates `0.0.1`.

## Upstream

Integration code is adapted from the Apache-2.0 licensed Home Assistant Core Mopeka integration: `homeassistant/components/mopeka`.

The Bluetooth parser dependency is `mopeka-iot-ble`.

## License

Apache License 2.0. See [LICENSE](LICENSE).
