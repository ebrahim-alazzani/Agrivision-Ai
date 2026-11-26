"""Fail-closed replacement for the historical synthetic training scaffold.

Use the reviewed Colab pipeline only after a real dataset audit. This CLI no
longer emits fabricated metrics or saves randomly initialized checkpoints.
"""
import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="AgriVision training entry point (disabled scaffold)")
    parser.add_argument("--config", type=Path, default=Path("research/configs/baseline_config.yaml"))
    parser.add_argument("--output-dir", type=Path, default=Path("ai/weights"))
    parser.parse_args()
    parser.error(
        "This command is a scaffold and does not implement dataset loading or a real training loop. "
        "It intentionally refuses to train or create checkpoints. Audit and validate a real dataset "
        "first, then use a reviewed training pipeline."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
