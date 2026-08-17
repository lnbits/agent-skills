#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def model_schema(model: type[Any]) -> dict[str, Any]:
    modern = getattr(model, "model_json_schema", None)
    if callable(modern):
        return modern()
    legacy = getattr(model, "schema", None)
    if callable(legacy):
        return legacy()
    raise TypeError(f"{model.__name__} does not expose a JSON schema method")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print the authoritative LNbits WASM runtime contract as JSON."
    )
    parser.add_argument("--lnbits-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.lnbits_root.resolve()

    required = root / "lnbits/core/wasm_ext/wasm/config.py"
    if not required.is_file():
        parser.error(f"{root} does not contain lnbits/core/wasm_ext")

    sys.path.insert(0, str(root))
    from lnbits.core.wasm_ext.api.registry import (  # noqa: PLC0415
        extension_api_contract,
        extension_api_permission_ids,
    )
    from lnbits.core.wasm_ext.routes.assets import (  # noqa: PLC0415
        WASM_EXTENSION_CORE_STATIC_ASSETS,
        WASM_EXTENSION_GENERATED_CORE_ASSETS,
    )
    from lnbits.core.wasm_ext.wasm.config import (  # noqa: PLC0415
        WasmExtensionConfig,
    )

    assets: dict[str, Any] = {
        name: {"source": value[0], "content_type": value[1]}
        for name, value in WASM_EXTENSION_CORE_STATIC_ASSETS.items()
    }
    assets.update(
        {
            name: {"generated": True, "content_type": value[1]}
            for name, value in WASM_EXTENSION_GENERATED_CORE_ASSETS.items()
        }
    )
    output = {
        "root": str(root),
        "commit": git(root, "rev-parse", "HEAD"),
        "describe": git(root, "describe", "--tags", "--always", "--dirty"),
        "config_schema": model_schema(WasmExtensionConfig),
        "host_api": extension_api_contract(),
        "permission_ids": sorted(extension_api_permission_ids()),
        "iframe_core_assets": dict(sorted(assets.items())),
    }
    json.dump(output, sys.stdout, indent=2, sort_keys=True, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
