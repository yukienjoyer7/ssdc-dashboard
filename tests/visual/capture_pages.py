"""Capture every configured dashboard page at every configured viewport."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

import yaml
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tests/visual/pages.yaml"
OUTPUT = ROOT / "tests/visual/screenshots"


def load_manifest() -> dict:
    with MANIFEST.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def wait_for_render(page: Page) -> None:
    page.wait_for_load_state("domcontentloaded", timeout=30_000)
    page.locator("[data-testid='stAppViewContainer']").wait_for(state="visible", timeout=30_000)
    page.wait_for_timeout(2_000)
    page.locator("[data-testid='stStatusWidget']").wait_for(state="hidden", timeout=30_000)
    # Carbon components hydrate independently of Streamlit's status widget.
    # Wait for a rendered KPI tile so screenshots never capture plain fallback text.
    page.locator(".cds-kpi-card").first.wait_for(state="visible", timeout=30_000)
    # A page may have analytical marks or an explicit empty state when an
    # optional upstream artifact (such as semantic scores) is unavailable.
    page.locator(".js-plotly-plot, cds-inline-notification").first.wait_for(
        state="visible", timeout=30_000
    )
    page.wait_for_timeout(500)


def navigate(page: Page, base_url: str, configured_path: str, title: str) -> None:
    page.goto(base_url.rstrip("/") + configured_path, wait_until="domcontentloaded", timeout=30_000)
    try:
        wait_for_render(page)
    except PlaywrightTimeoutError:
        # Streamlit page routes can vary by version; use the app shell as a fallback.
        page.goto(base_url, wait_until="domcontentloaded", timeout=30_000)
        wait_for_render(page)
        shell_slug = configured_path.strip("/").replace("_", "-")
        page.locator(f"a[href='#{shell_slug}']").last.click(timeout=10_000, force=True)
        wait_for_render(page)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--base-url", default=None)
    args = parser.parse_args()
    manifest = load_manifest()
    base_url = args.base_url or manifest["base_url"]
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        for viewport in manifest["viewports"]:
            page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
            for dashboard_page in manifest["pages"]:
                filename = f"{dashboard_page['name']}__{viewport['name']}.png"
                try:
                    navigate(page, base_url, dashboard_page["path"], dashboard_page["title"])
                    page.screenshot(path=str(output / filename), full_page=True)
                    print(f"PASS screenshot {filename}")
                except Exception as exc:  # noqa: BLE001 - report every page failure and continue
                    failures.append(f"{dashboard_page['name']} @ {viewport['name']}: {exc}")
                    print(f"FAIL screenshot {filename}: {exc}", file=sys.stderr)
        browser.close()
    if failures:
        print("\nCapture failures:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
