import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Union, get_args, get_origin

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def build_dynamic_query(
    search_obj: BaseModel,
    model_cls,
    db: Session,
    limit: Optional[int] = None,  # default limit for pagination
    offset: Optional[int] = None,  # default offset for pagination
):
    try:
        return _build_dynamic_query(
            search_obj=search_obj,
            model_cls=model_cls,
            db=db,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        logger.error(f"Error in node search: {e}")
        return {"error": str(e)}


def _build_dynamic_query(
    search_obj: BaseModel,
    model_cls,
    db: Session,
    limit: Optional[int] = None,  # default limit for pagination
    offset: Optional[int] = None,  # default offset for pagination
):
    """
    Build and execute a SQLAlchemy 2.0-style SELECT based on the non-None
    attributes of a Pydantic model instance.  The operator is inferred from
    each field's *declared* type, not the runtime value.

    Handles both direct model fields and relationship fields (e.g., family, genus, taxon_rank).
    """
    from biokb_wcvp.db import models

    filters = []
    joins = []  # Track which tables we need to join

    # Only the attributes the client actually supplied (`exclude_none`)
    payload = search_obj.model_dump(exclude_none=True)

    # Map search field names to (relationship_model, relationship_attr, target_column)
    # For fields that are in related tables
    relationship_fields = {}

    if model_cls == models.Plant:
        relationship_fields = {
            "family": (models.Family, "family", models.Family.name),
            "genus": (models.Genus, "genus", models.Genus.name),
            "taxon_rank": (models.TaxonRank, "taxon_rank", models.TaxonRank.name),
            "taxon_status": (
                models.TaxonStatus,
                "taxon_status",
                models.TaxonStatus.name,
            ),
            "infraspecific_rank": (
                models.InfraspecificRank,
                "infraspecific_rank",
                models.InfraspecificRank.name,
            ),
            "lifeform_description": (
                models.LifeformDescription,
                "lifeform_description",
                models.LifeformDescription.name,
            ),
            "climate_description": (
                models.ClimateDescription,
                "climate_description",
                models.ClimateDescription.name,
            ),
        }
    elif model_cls == models.Location:
        relationship_fields = {
            "continent": (models.Continent, "continent", models.Continent.name),
            "region": (models.Region, "region", models.Region.name),
            "area": (models.Area, "area", models.Area.name),
        }

    for field_name, value in payload.items():
        # Check if this is a relationship field
        if field_name in relationship_fields:
            rel_model, rel_attr, rel_column = relationship_fields[field_name]
            if rel_model not in joins:
                joins.append(rel_model)

            # Get the declared type for this field
            declared_type = search_obj.__pydantic_fields__[field_name].annotation
            if get_origin(declared_type) is Union:
                args = [arg for arg in get_args(declared_type) if arg is not type(None)]
                if args:
                    declared_type = args[0]
            origin = get_origin(declared_type) or declared_type

            # Apply filter on the related table's column
            if origin is str:
                filters.append(
                    rel_column.like(value) if ("%" in value) else rel_column == value
                )
            else:
                filters.append(rel_column == value)
            continue

        # Skip if the SQLAlchemy model has no matching column / hybrid attr
        if not hasattr(model_cls, field_name):
            continue
        column = getattr(model_cls, field_name)

        # ↓ The type you wrote in the Pydantic model definition
        declared_type = search_obj.__pydantic_fields__[field_name].annotation
        # Handle Optional types (e.g., Optional[str] or Union[str, None])
        if get_origin(declared_type) is Union:
            args = [arg for arg in get_args(declared_type) if arg is not type(None)]
            if args:
                declared_type = args[0]
        origin = get_origin(declared_type) or declared_type

        # STRING ......................................................................
        if origin is str:
            logger.info(f"Used string filter for {field_name}")
            filters.append(column.like(value) if ("%" in value) else column == value)

        # NUMBERS .....................................................................
        elif origin in (int, float, Decimal):
            filters.append(column == value)

        # BOOLEANS ....................................................................
        elif origin is bool:
            filters.append(column.is_(value))

        # DATE / DATETIME – supports equality or simple closed range ...................
        elif origin in (date, datetime):
            if isinstance(value, (list, tuple)) and len(value) == 2:
                filters.append(column.between(value[0], value[1]))
            else:
                filters.append(column == value)

        # FALLBACK .....................................................................
        else:
            logger.warning(
                f"Unsupported type for field '{field_name}': {declared_type}. "
                "Using equality operator as fallback."
            )
            filters.append(column == value)

    # Build the SELECT statement with joins if needed
    stmt = select(model_cls)
    for join_model in joins:
        stmt = stmt.outerjoin(join_model)
    stmt = stmt.where(*filters)

    # Build count statement with the same joins
    count_stmt = select(func.count()).select_from(model_cls)
    for join_model in joins:
        count_stmt = count_stmt.outerjoin(join_model)
    count_stmt = count_stmt.where(*filters)

    total_count = db.execute(count_stmt).scalar()

    if limit is not None:
        stmt = stmt.limit(limit)
    if offset is not None:
        stmt = stmt.offset(offset)

    logger.info(stmt.compile(compile_kwargs={"literal_binds": True}))

    return {
        "count": total_count,
        "limit": limit,
        "offset": offset,
        "results": db.execute(stmt).scalars().all(),
    }
