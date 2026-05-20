from argparse import ArgumentParser

from research_system.pipelines.research_pipeline import run_research_pipeline
from research_system.utils.logger import get_logger

if __name__ == "__main__":
    parser = ArgumentParser(description="Run the research pipeline.")
    parser.add_argument(
        "topic",
        nargs="?",
        default="What are recent developments in agentic AI systems?",
        help="Research topic to investigate.",
    )
    args = parser.parse_args()

    logger = get_logger()
    logger.info("Starting research pipeline for topic: %s", args.topic)
    result = run_research_pipeline(args.topic)
    print(result["report"])
