from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

from rdflib import Graph

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY_PATH = PROJECT_ROOT / "ontology" / "cosmo.ttl"
DATA_DIR = PROJECT_ROOT / "data" / "ttl"
OUTPUT_PATH = DATA_DIR / "merged_graph.ttl"


def validate_paths(paths: Iterable[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required file(s): {', '.join(missing)}")


def build_graph(ontology_path: Path, data_paths: Iterable[Path]) -> Graph:
    graph = Graph()

    validate_paths([ontology_path, *data_paths])

    logger.info("Loading ontology: %s", ontology_path)
    graph.parse(ontology_path, format="turtle")

    for path in data_paths:
        logger.info("Loading data file: %s", path)
        graph.parse(path, format="turtle")

    return graph


def save_graph(graph: Graph, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=output_path, format="turtle")
    logger.info("Merged graph written to: %s", output_path)


def main() -> None:
    data_paths = sorted(DATA_DIR.glob("*.ttl"))
    data_paths = [p for p in data_paths if p.name != OUTPUT_PATH.name]

    if not data_paths:
        raise FileNotFoundError(f"No Turtle data files found in {DATA_DIR}")

    graph = build_graph(ONTOLOGY_PATH, data_paths)
    logger.info("Triples loaded: %d", len(graph))

    save_graph(graph, OUTPUT_PATH)


if __name__ == "__main__":
    main()