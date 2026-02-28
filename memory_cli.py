"""memory_cli.py"""
import argparse
import json
from datetime import datetime, timedelta
from memory.pinecone_memory import PineconeMemory

memory = PineconeMemory()

def cmd_stats(_):
    stats = memory.memory_stats()
    print(json.dumps(stats, indent=2))

def cmd_recent(args):
    days = int(args.days)
    recent = memory.get_recent_articles(days=days)
    for a in recent:
        print(f"- [{a['published']}] {a['title']} ({a['source']})\n  {a['url']}")

def cmd_search(args):
    results = memory.semantic_search(query=args.query, top_k=5)
    for r in results:
        print(f"- {r['title']} (score: {r['score']:.2f})\n  {r['url']}")

def cmd_clear(args):
    ns = args.namespace
    confirm = input(f"Удалить все векторы из namespace '{ns}'? (y/N): ")
    if confirm.lower() == "y":
        memory.clear_namespace(ns)
        print(f"Namespace '{ns}' очищен.")
    else:
        print("Отмена.")

def main():
    parser = argparse.ArgumentParser(prog="memory_cli")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("stats")
    recent = sub.add_parser("recent")
    recent.add_argument("--days", default=7, help="За сколько дней назад")
    search = sub.add_parser("search")
    search.add_argument("query")
    clear = sub.add_parser("clear")
    clear.add_argument("namespace", choices=["articles", "lifehacks"])

    args = parser.parse_args()
    if args.command == "stats":
        cmd_stats(args)
    elif args.command == "recent":
        cmd_recent(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "clear":
        cmd_clear(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()