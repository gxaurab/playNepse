import logging
import time
from datetime import UTC, date, datetime, timedelta
from datetime import time as dt_time
from typing import Any

import httpx
from nepse import Nepse
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.db import SessionLocal
from app.events import publish
from app.models import Company, Floorsheet, Price
from app.runs import track_run

logger = logging.getLogger(__name__)


def get_nepse_client() -> Nepse:
    client = Nepse()
    client.setTLSVerification(False)
    return client


def parse_date(val: Any) -> date | None:
    if not val:
        return None
    if isinstance(val, date):
        return val
    try:
        return date.fromisoformat(str(val).split("T")[0])
    except (ValueError, TypeError, IndexError):
        return None


def parse_time(val: Any) -> dt_time | None:
    if not val:
        return None
    if isinstance(val, dt_time):
        return val
    try:
        s = str(val).strip()
        if "T" in s:
            s = s.split("T")[1]
        return dt_time.fromisoformat(s)
    except (ValueError, TypeError, IndexError):
        return None


def backfill_prices(days: int = 45, trigger: str = "manual") -> int:
    client = get_nepse_client()
    today = datetime.now(UTC).date()
    # Filter Friday (4) and Saturday (5) since NEPSE trades Sun-Thu
    dates_to_check = [
        today - timedelta(days=i)
        for i in reversed(range(days + 1))
        if (today - timedelta(days=i)).weekday() not in (4, 5)
    ]

    total_upserted = 0
    fetched_dates = []
    skipped_dates = []

    with (
        SessionLocal() as db,
        track_run(db, job_type="prices", source="nepse", trigger=trigger) as run,
    ):
        companies = db.execute(select(Company).where(Company.is_active.is_(True))).scalars().all()
        symbol_to_id = {c.symbol: c.id for c in companies}

        for date_val in dates_to_check:
            date_str = date_val.strftime("%Y-%m-%d")
            try:
                res = client.getPriceVolumeHistory(date_str)
            except (httpx.HTTPError, ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
                logger.warning("Failed fetching prices for %s: %s", date_str, exc)
                skipped_dates.append(date_str)
                time.sleep(0.5)
                continue

            if not isinstance(res, dict) or not res.get("content"):
                logger.info("No price data for %s (holiday)", date_str)
                skipped_dates.append(date_str)
                time.sleep(0.5)
                continue

            content = list(res.get("content", []))
            total_pages = res.get("totalPages", 1)
            for page in range(1, total_pages):
                try:
                    page_url = (
                        f"{client.api_end_points['todays_price']}?&size=500"
                        f"&businessDate={date_str}&page={page}"
                    )
                    page_res = client.requestPOSTAPI(
                        url=page_url,
                        payload_generator=client.getPOSTPayloadIDForFloorSheet,
                    )
                    if isinstance(page_res, dict):
                        content.extend(page_res.get("content", []))
                except (httpx.HTTPError, ValueError, KeyError, TypeError, OSError, RuntimeError):
                    break

            date_upserted = 0
            for row in content:
                symbol = row.get("symbol")
                if symbol not in symbol_to_id:
                    continue

                company_id = symbol_to_id[symbol]
                stmt = (
                    insert(Price)
                    .values(
                        company_id=company_id,
                        date=date_val,
                        open=row.get("openPrice"),
                        high=row.get("highPrice"),
                        low=row.get("lowPrice"),
                        close=row.get("closePrice"),
                        volume=row.get("totalTradedQuantity"),
                        turnover=row.get("totalTradedValue"),
                        trades=row.get("totalTrades"),
                        vwap=row.get("averageTradedPrice"),
                    )
                    .on_conflict_do_update(
                        index_elements=["company_id", "date"],
                        set_={
                            "open": row.get("openPrice"),
                            "high": row.get("highPrice"),
                            "low": row.get("lowPrice"),
                            "close": row.get("closePrice"),
                            "volume": row.get("totalTradedQuantity"),
                            "turnover": row.get("totalTradedValue"),
                            "trades": row.get("totalTrades"),
                            "vwap": row.get("averageTradedPrice"),
                        },
                    )
                )
                db.execute(stmt)
                date_upserted += 1

            db.commit()
            fetched_dates.append(date_str)
            total_upserted += date_upserted
            time.sleep(0.5)

        run.items_new = total_upserted
        symbols = sorted(symbol_to_id.keys())

    publish("prices", {"symbols": symbols})
    print(f"Trading dates fetched ({len(fetched_dates)}): {fetched_dates}")
    print(f"Trading dates skipped ({len(skipped_dates)}): {skipped_dates}")
    return total_upserted


def fetch_floorsheet(trigger: str = "manual") -> int:
    client = get_nepse_client()
    with (
        SessionLocal() as db,
        track_run(db, job_type="floorsheet", source="nepse", trigger=trigger) as run,
    ):
        companies = db.execute(select(Company).where(Company.is_active.is_(True))).scalars().all()
        symbol_to_id = {c.symbol: c.id for c in companies}

        res = client.getFloorSheet()
        if isinstance(res, dict):
            rows = res.get("floorsheets", {}).get("content", [])
        elif isinstance(res, list):
            rows = res
        else:
            rows = []

        inserted_count = 0
        for row in rows:
            symbol = row.get("stockSymbol")
            if symbol not in symbol_to_id:
                continue

            company_id = symbol_to_id[symbol]
            contract_id = row.get("contractId")
            if not contract_id:
                continue

            business_date = parse_date(row.get("businessDate"))
            if not business_date:
                continue

            buyer_broker = str(row.get("buyerMemberId") or row.get("buyerBrokerName") or "") or None
            seller_broker = (
                str(row.get("sellerMemberId") or row.get("sellerBrokerName") or "") or None
            )

            stmt = (
                insert(Floorsheet)
                .values(
                    contract_id=contract_id,
                    company_id=company_id,
                    business_date=business_date,
                    buyer_broker=buyer_broker,
                    seller_broker=seller_broker,
                    quantity=row.get("contractQuantity"),
                    rate=row.get("contractRate"),
                    amount=row.get("contractAmount"),
                    trade_time=parse_time(row.get("tradeTime")),
                )
                .on_conflict_do_nothing(index_elements=["contract_id"])
            )
            db.execute(stmt)
            inserted_count += 1

        db.commit()
        run.items_new = inserted_count
        symbols = sorted(symbol_to_id.keys())

    publish("floorsheet", {"symbols": symbols, "items_new": inserted_count})
    return inserted_count
