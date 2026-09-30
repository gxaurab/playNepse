import argparse

from app.services.market import backfill_prices, fetch_floorsheet


def main() -> None:
    parser = argparse.ArgumentParser(description="playNepse CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    backfill_parser = subparsers.add_parser("backfill", help="Backfill historical prices")
    backfill_parser.add_argument("--days", type=int, default=45, help="Number of days to backfill")

    subparsers.add_parser("floorsheet", help="Fetch latest floorsheet")

    args = parser.parse_args()

    if args.command == "backfill":
        rows = backfill_prices(days=args.days, trigger="manual")
        print(f"Backfill completed: {rows} price rows upserted.")
    elif args.command == "floorsheet":
        rows = fetch_floorsheet(trigger="manual")
        print(f"Floorsheet fetch completed: {rows} rows inserted.")


if __name__ == "__main__":
    main()
