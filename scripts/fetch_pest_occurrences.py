"""
Fetch real pest/disease occurrence records from GBIF for Nigeria.

- Uses GBIF speciesKey resolution (authoritative)
- Restricts records to Nigeria (country=NG)
- Uses state centroid + bbox buffer for spatial approximation
- Filters to real observation records only
"""

import argparse
import csv
import time
import requests
from pathlib import Path
from typing import List, Dict

GBIF_OCCURRENCE_API = "https://api.gbif.org/v1/occurrence/search"
GBIF_SPECIES_API = "https://api.gbif.org/v1/species/match"

DEFAULT_SPECIES = [
    "Spodoptera frugiperda",
    "Locusta migratoria",
    "Schistocerca gregaria"
]

# ---------------------------------------------------------------------------
# Load zones from climate script (NO FAKE FALLBACK)
# ---------------------------------------------------------------------------

def load_zones():
    from scripts.download_climate_data import Config
    return Config.ZONES


# ---------------------------------------------------------------------------
# Resolve GBIF speciesKey (CRITICAL FOR REAL DATA)
# ---------------------------------------------------------------------------

def resolve_species_key(species_name: str) -> int:
    r = requests.get(
        GBIF_SPECIES_API,
        params={"name": species_name},
        timeout=30
    )
    r.raise_for_status()
    data = r.json()

    if "usageKey" not in data:
        raise RuntimeError(f"Could not resolve GBIF speciesKey for {species_name}")

    return data["usageKey"]


# ---------------------------------------------------------------------------
# GBIF occurrence query
# ---------------------------------------------------------------------------

def gbif_search_species_bbox(
    species_key: int,
    minlat: float,
    maxlat: float,
    minlon: float,
    maxlon: float,
    start_year: int,
    end_year: int
) -> List[Dict]:

    results = []
    limit = 300
    offset = 0

    while True:
        params = {
            "speciesKey": species_key,
            "country": "NG",
            "hasCoordinate": "true",
            "basisOfRecord": "HUMAN_OBSERVATION",
            "minLatitude": minlat,
            "maxLatitude": maxlat,
            "minLongitude": minlon,
            "maxLongitude": maxlon,
            "year": f"{start_year},{end_year}",
            "limit": limit,
            "offset": offset
        }

        r = requests.get(GBIF_OCCURRENCE_API, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()

        records = data.get("results", [])
        if not records:
            break

        for occ in records:
            results.append({
                "gbifID": occ.get("key"),
                "species": occ.get("species"),
                "eventDate": occ.get("eventDate"),
                "year": occ.get("year"),
                "decimalLatitude": occ.get("decimalLatitude"),
                "decimalLongitude": occ.get("decimalLongitude"),
                "stateProvince": occ.get("stateProvince"),
                "locality": occ.get("locality")
            })

        offset += limit
        if offset >= data.get("count", 0):
            break

        time.sleep(1)

    return results


# ---------------------------------------------------------------------------
# CSV writer
# ---------------------------------------------------------------------------

def save_csv(path: Path, rows: List[Dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--species", type=str, default=",".join(DEFAULT_SPECIES))
    parser.add_argument("--start-year", type=int, default=1990)
    parser.add_argument("--end-year", type=int, default=2023)
    parser.add_argument("--buffer-deg", type=float, default=0.5)
    parser.add_argument("--output-dir", type=str, default="project_data/raw_data/pests")
    args = parser.parse_args()

    zones = load_zones()
    out_dir = Path(args.output_dir)
    summary = []

    species_list = [s.strip() for s in args.species.split(",") if s.strip()]

    for sp in species_list:
        print(f"\nResolving GBIF speciesKey for {sp}...")
        species_key = resolve_species_key(sp)
        print(f"  speciesKey = {species_key}")

        all_records = []

        for zone, states in zones.items():
            for state, coord in states.items():
                lat, lon = coord["lat"], coord["lon"]

                minlat, maxlat = lat - args.buffer_deg, lat + args.buffer_deg
                minlon, maxlon = lon - args.buffer_deg, lon + args.buffer_deg

                print(f"Querying {sp} in {state} ({zone})...")
                recs = gbif_search_species_bbox(
                    species_key,
                    minlat, maxlat,
                    minlon, maxlon,
                    args.start_year, args.end_year
                )

                for r in recs:
                    r["Geopolitical_Zone"] = zone
                    r["State"] = state

                summary.append({
                    "species": sp,
                    "zone": zone,
                    "state": state,
                    "count": len(recs)
                })

                all_records.extend(recs)
                time.sleep(1)

        save_csv(out_dir / f"occurrences_{sp.replace(' ', '_')}.csv", all_records)
        print(f"Saved {len(all_records)} real records for {sp}")

    save_csv(out_dir / "occurrence_summary_by_state.csv", summary)
    print("\nDONE: Real GBIF data collected successfully.")


if __name__ == "__main__":
    main()
