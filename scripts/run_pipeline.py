import argparse
import asyncio

from agentic_code_testing.orchestrator.agent import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run user_story -> planner -> codetest_writer over A2A.")
    parser.add_argument(
        "file_path", nargs="?", default="user_inputs/user_stories/05_leaderboard_no_format.md",
        help="User story file to run through the pipeline.",
    )
    parser.add_argument("story_id", nargs="?", type=int, default=1)
    parser.add_argument("--output-dir", default="./out")
    parser.add_argument(
        "--root-dir", default="./path/to/your/codebase",
        help="Codebase the story is about -- what code_reader_agent answers questions against.",
    )
    args = parser.parse_args()

    result = asyncio.run(run_pipeline(
        file_path=args.file_path,
        story_id=args.story_id,
        output_dir=args.output_dir,
        root_dir=args.root_dir,
    ))
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
