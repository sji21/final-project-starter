import argparse
import json
from pathlib import Path

from app.dataset import export_train, inspect_records
from app.evaluation import evaluate


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_jsonl(path):
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main():
    parser = argparse.ArgumentParser(description="업무 팩 평가·학습 데이터 도구")
    sub = parser.add_subparsers(dest="command", required=True)
    evaluate_parser = sub.add_parser("evaluate")
    evaluate_parser.add_argument("--run", required=True)
    evaluate_parser.add_argument("--gold", required=True)
    evaluate_parser.add_argument("--out", required=True)
    dataset_parser = sub.add_parser("dataset-check")
    dataset_parser.add_argument("input")
    export_parser = sub.add_parser("dataset-export")
    export_parser.add_argument("input")
    export_parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if args.command == "evaluate":
        result = evaluate(read_json(args.run), read_json(args.gold))
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
    elif args.command == "dataset-check":
        _, result = inspect_records(read_jsonl(args.input))
    else:
        result = export_train(read_jsonl(args.input), Path(args.out))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("valid") is False:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
