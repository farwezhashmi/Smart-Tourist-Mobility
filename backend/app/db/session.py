from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


settings = get_settings()
engine_options = {"pool_pre_ping": True}
if settings.database_url.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
else:
    engine_options["connect_args"] = {"connect_timeout": 5}

engine = create_engine(settings.database_url, **engine_options)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def initialize_local_database() -> None:
    if not settings.database_url.startswith("sqlite"):
        return

    from app.db.models import Base, Location, Route, TransportMode

    Base.metadata.create_all(bind=engine)
    with SessionLocal.begin() as db:
        locations = [
            ("Secunderabad Railway Station", "transport_hub", "Secunderabad", 78.5011, 17.4399, "Railway concourse and road-level pickup access"),
            ("Charminar", "attraction", "Old City", 78.4747, 17.3616, "Pedestrian approaches can be crowded"),
            ("Hussain Sagar Lake", "attraction", "Tank Bund", 78.4734, 17.4239, "Accessible promenade sections vary"),
            ("Golconda Fort", "attraction", "Golconda", 78.4011, 17.3833, "Historic site with uneven surfaces"),
            ("Rajiv Gandhi International Airport", "transport_hub", "Shamshabad", 78.4294, 17.2403, "Terminal drop-off and accessible facilities"),
            ("Nampally", "transport_hub", "Nampally", 78.4677, 17.3936, "Rail and road interchange with busy approaches"),
        ]
        for name, location_type, zone, longitude, latitude, notes in locations:
            if db.query(Location).filter_by(name=name).first() is None:
                db.add(Location(name=name, location_type=location_type, zone=zone, point=f"POINT({longitude} {latitude})", accessibility_notes=notes))

        modes = [
            ("auto", "Auto-rickshaw", False, False, 115.0),
            ("cab", "Cab", False, True, 140.0),
            ("bus", "City bus", True, True, 80.0),
            ("metro", "Metro", True, True, 35.0),
            ("walking", "Walking", True, True, 0.0),
        ]
        for code, name, is_public, accessible, emissions in modes:
            if db.query(TransportMode).filter_by(code=code).first() is None:
                db.add(TransportMode(code=code, name=name, is_public=is_public, supports_accessibility=accessible, emission_factor_g_per_km=emissions))
        db.flush()

        route_specs = {
            ("Secunderabad Railway Station", "Charminar"): [("auto", 7.4, 28, 250, 0, False), ("cab", 7.8, 25, 180, 0, True), ("bus", 8.2, 42, 450, 1, True), ("metro", 9.0, 38, 350, 1, True)],
            ("Secunderabad Railway Station", "Hussain Sagar Lake"): [("auto", 4.5, 18, 180, 0, False), ("cab", 4.8, 16, 120, 0, True), ("bus", 5.2, 28, 300, 1, True), ("metro", 5.8, 25, 250, 1, True)],
            ("Secunderabad Railway Station", "Golconda Fort"): [("auto", 12.5, 42, 300, 0, False), ("cab", 13.0, 38, 220, 0, True), ("bus", 14.0, 70, 650, 2, True), ("metro", 15.0, 62, 500, 2, True)],
            ("Rajiv Gandhi International Airport", "Charminar"): [("auto", 19.5, 58, 350, 0, False), ("cab", 20.0, 48, 250, 0, True), ("bus", 22.0, 95, 900, 2, True), ("metro", 23.0, 82, 700, 2, True)],
            ("Nampally", "Charminar"): [("auto", 3.8, 18, 180, 0, False), ("cab", 4.0, 15, 120, 0, True), ("bus", 4.5, 25, 300, 1, True), ("metro", 5.0, 23, 250, 1, True)],
            ("Nampally", "Golconda Fort"): [("auto", 8.5, 32, 250, 0, False), ("cab", 9.0, 28, 180, 0, True), ("bus", 9.8, 52, 500, 1, True), ("metro", 10.5, 47, 450, 1, True)],
        }
        locations_by_name = {location.name: location for location in db.query(Location).all()}
        modes_by_code = {mode.code: mode for mode in db.query(TransportMode).all()}
        for (origin_name, destination_name), alternatives in route_specs.items():
            origin = locations_by_name[origin_name]
            destination = locations_by_name[destination_name]
            for mode_code, distance, duration, walking, transfers, accessible in alternatives:
                mode = modes_by_code[mode_code]
                exists = db.query(Route).filter_by(origin_location_id=origin.id, destination_location_id=destination.id, mode_id=mode.id).first()
                if exists is None:
                    db.add(Route(origin_location_id=origin.id, destination_location_id=destination.id, mode_id=mode.id, provider="hyderabad_demo", provider_route_id=f"{mode_code}-{origin_name}-{destination_name}", distance_km=distance, duration_min=duration, walking_distance_m=walking, transfer_count=transfers, is_accessible=accessible, source_type="synthetic_demo", source_reference="phase-2-demo-seed"))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
