from pathlib import Path

import yaml
from sqlalchemy.dialects.postgresql import insert

from app.config import get_settings
from app.db import SessionLocal
from app.models import Company


def sync_companies() -> None:
    settings = get_settings()
    path = Path(settings.COMPANIES_FILE)
    if not path.is_absolute():
        path = (Path(__file__).resolve().parent.parent / path).resolve()

    if not path.exists():
        return

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or []

    with SessionLocal() as db:
        for item in data:
            stmt = (
                insert(Company)
                .values(
                    symbol=item["symbol"],
                    name=item["name"],
                    sector=item.get("sector"),
                    aliases=item.get("aliases", []),
                    is_active=True,
                )
                .on_conflict_do_update(
                    index_elements=["symbol"],
                    set_={
                        "name": item["name"],
                        "sector": item.get("sector"),
                        "aliases": item.get("aliases", []),
                        "is_active": True,
                    },
                )
            )
            db.execute(stmt)
        db.commit()
