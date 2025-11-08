import json
import time
import os
import math
import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from pyproj import Geod

##############################################################################
# 1) CONFIG & GLOBALS (PRESERVES YOUR ORIGINAL LOGIC)
##############################################################################

# 193 UN members + Taiwan + Vatican City + Palestine (your 196 set)
VALID_COUNTRIES = {
    'afghanistan', 'albania', 'algeria', 'andorra', 'angola', 'antigua and barbuda', 'argentina',
    'armenia', 'australia', 'austria', 'azerbaijan', 'bahamas', 'bahrain', 'bangladesh',
    'barbados', 'belarus', 'belgium', 'belize', 'benin', 'bhutan', 'bolivia',
    'bosnia and herzegovina', 'botswana', 'brazil', 'brunei', 'bulgaria', 'burkina faso',
    'burundi', 'cambodia', 'cameroon', 'canada', 'cape verde', 'central african republic',
    'chad', 'chile', 'china', 'colombia', 'comoros', 'congo', 'costa rica', 'croatia',
    'cuba', 'cyprus', 'czech republic', 'democratic republic of the congo', 'denmark',
    'djibouti', 'dominica', 'dominican republic', 'ecuador', 'egypt', 'el salvador',
    'equatorial guinea', 'eritrea', 'estonia', 'eswatini', 'ethiopia', 'fiji', 'finland',
    'france', 'gabon', 'gambia', 'georgia', 'germany', 'ghana', 'greece', 'grenada',
    'guatemala', 'guinea', 'guinea-bissau', 'guyana', 'haiti', 'honduras', 'hungary',
    'iceland', 'india', 'indonesia', 'iran', 'iraq', 'ireland', 'israel', 'italy',
    'ivory coast', 'jamaica', 'japan', 'jordan', 'kazakhstan', 'kenya', 'kiribati',
    'kuwait', 'kyrgyzstan', 'laos', 'latvia', 'lebanon', 'lesotho', 'liberia', 'libya',
    'liechtenstein', 'lithuania', 'luxembourg', 'madagascar', 'malawi', 'malaysia',
    'maldives', 'mali', 'malta', 'marshall islands', 'mauritania', 'mauritius', 'mexico',
    'micronesia', 'moldova', 'monaco', 'mongolia', 'montenegro', 'morocco', 'mozambique',
    'myanmar', 'namibia', 'nauru', 'nepal', 'netherlands', 'new zealand', 'nicaragua',
    'niger', 'nigeria', 'north korea', 'north macedonia', 'norway', 'oman', 'pakistan',
    'palau', 'palestine', 'panama', 'papua new guinea', 'paraguay', 'peru', 'philippines',
    'poland', 'portugal', 'qatar', 'romania', 'russia', 'rwanda', 'saint kitts and nevis',
    'saint lucia', 'saint vincent and the grenadines', 'samoa', 'san marino',
    'sao tome and principe', 'saudi arabia', 'senegal', 'serbia', 'seychelles',
    'sierra leone', 'singapore', 'slovakia', 'slovenia', 'solomon islands', 'somalia',
    'south africa', 'south korea', 'south sudan', 'spain', 'sri lanka', 'sudan', 'suriname',
    'sweden', 'switzerland', 'syria', 'taiwan', 'tajikistan', 'tanzania', 'thailand',
    'timor-leste', 'togo', 'tonga', 'trinidad and tobago', 'tunisia', 'turkey',
    'turkmenistan', 'tuvalu', 'uganda', 'ukraine', 'united arab emirates',
    'united kingdom', 'united states', 'uruguay', 'uzbekistan', 'vanuatu',
    'vatican city', 'venezuela', 'vietnam', 'yemen', 'zambia', 'zimbabwe'
}

# Synonyms / alternate names (preserved)
SYNONYM_MAP = {
    'republic of korea': 'south korea',
    'korea, republic of': 'south korea',
    'korea (rep.)': 'south korea',
    'korea (south)': 'south korea',
    'korea, dem. people’s rep. (north korea)': 'north korea',
    'democratic people\'s republic of korea': 'north korea',
    'korea, dem. rep. of': 'north korea',
    'ivory coast': 'ivory coast',
    'côte d’ivoire': 'ivory coast',
    'cote d’ivoire': 'ivory coast',
    'bolivia (plurinational state of)': 'bolivia',
    'lao people’s democratic republic': 'laos',
    'lao pdr': 'laos',
    'brunei darussalam': 'brunei',
    'union of the comoros': 'comoros',
    'tibet': 'china',
    'hong kong': 'china',
    'syrian arab republic': 'syria',
    'russian federation': 'russia',
    'viet nam': 'vietnam',
    'timor leste': 'timor-leste',
    'swaziland': 'eswatini',
    'bosnia & herzegovina': 'bosnia and herzegovina',
    'bosnia-herzegovina': 'bosnia and herzegovina',
    'united states of america': 'united states',
    'u.s.a.': 'united states',
    'united states (usa)': 'united states',
    'republic of the congo': 'congo',
    'congo, rep. of the': 'congo',
    'republic of congo': 'congo',
    'democratic republic of congo': 'democratic republic of the congo',
    'congo, the democratic republic of': 'democratic republic of the congo',
    'drc': 'democratic republic of the congo',
    'iran (islamic republic of)': 'iran',
    'iran, islamic republic of': 'iran',
    'gambia, the': 'gambia',
    'the gambia': 'gambia',
    'moldova (republic of)': 'moldova',
    'republic of moldova': 'moldova',
    'tanzania, united republic of': 'tanzania',
    'united republic of tanzania': 'tanzania',
    'venezuela (bolivarian republic of)': 'venezuela',
    'venezuela, bolivarian republic of': 'venezuela',
    'south sudan (republic of)': 'south sudan',
}

# Sample sizes (preserved)
SAMPLE_SIZE_MAP = {
    'canada': 2000, 'russia': 1500, 'china': 1000, 'united states': 1000,
    'indonesia': 1000, 'philippines': 1000, 'norway': 800, 'brazil': 800,
    'australia': 800, 'india': 800, 'japan': 800, 'argentina': 800, 'mexico': 800,
    'kazakhstan': 800, 'united kingdom': 800,
}
DEFAULT_SAMPLE_SIZE = 700

def get_sample_size(country: str) -> int:
    return SAMPLE_SIZE_MAP.get(country, DEFAULT_SAMPLE_SIZE)

# Polygon-selection rules (preserved, including the original "equador" key)
POLYGON_SELECTION_RULES = {
    'angola':            {'count': 2},
    'australia':         {'count': 5},
    'azerbaijan':        {'count': 2},
    'bahamas':           {'count': 3},
    'canada':            {'all': True},
    'chile':             {'distance_threshold': 500},
    'china':             {'count': 2},
    'cuba':              {'count': 2},
    'denmark':           {'custom_denmark': True},
    'equatorial guinea': {'count': 2},
    'equador':           {'count': 2},  # (typo preserved)
    'estonia':           {'count': 2},
    'finland':           {'count': 2},
    'france':            {'count': 1},
    'greece':            {'count': 3},
    'indonesia':         {'all': True},
    'italy':             {'count': 3},
    'japan':             {'custom_japan': True},
    'malaysia':          {'count': 2},
    'morocco':           {'count': 1},
    'netherlands':       {'count': 2},
    'new zealand':       {'count': 3},
    'norway':            {'count': 2},
    'oman':              {'count': 2},
    'papua new guinea':  {'count': 5},
    'philippines':       {'all': True},
    'portugal':          {'count': 1},
    'russia':            {'all': True},
    'south korea':       {'count': 2},
    'spain':             {'count': 2},
    'sweden':            {'count': 2},
    'solomon islands':   {'count': 4},
    'timor-leste':       {'count': 2},
    'turkey':            {'count': 2},
    'united states':     {'all': True},
    'venezuela':         {'count': 1},
    'vanuatu':           {'count': 2},
    'yemen':             {'count': 2},
    'ukraine':           {'custom_ukraine': True},
    'croatia':           {'custom_croatia': True},
}

# Micronations / small states coords (preserved, including Maldives extra point)
MICRONATION_COORDS = {
    "andorra": [(1.6016, 42.5424)],
    "antigua and barbuda": [(-61.8456, 17.0747)],
    "bahrain": [(50.5577, 26.0667)],
    "barbados": [(-59.5432, 13.1939)],
    "cape verde": [(-23.5087, 14.9300)],
    "comoros": [(43.3333, -11.6455)],
    "dominica": [(-61.3710, 15.4239)],
    "grenada": [(-61.6792, 12.1165)],
    "kiribati": [(173.0314, 1.3382)],
    "liechtenstein": [(9.5537, 47.1660)],
    "maldives": [(73.5093, 4.1755), (73.5, 3.2)],
    "malta": [(14.3754, 35.9375)],
    "marshall islands": [(171.1854, 7.1315)],
    "mauritius": [(57.5522, -20.3484)],
    "micronesia": [(158.2239, 6.9248)],
    "monaco": [(7.4128, 43.7306)],
    "nauru": [(166.9315, -0.5338)],
    "palau": [(134.4795, 7.3419)],
    "saint kitts and nevis": [(-62.7830, 17.3578)],
    "saint lucia": [(-60.9789, 13.9094)],
    "saint vincent and the grenadines": [(-61.2872, 13.2528)],
    "samoa": [(-172.1046, -13.7590)],
    "san marino": [(12.4578, 43.9424)],
    "sao tome and principe": [(6.7273, 0.3302)],
    "seychelles": [(55.4915, -4.6796)],
    "singapore": [(103.8198, 1.3521)],
    "tonga": [(-175.1982, -21.1789)],
    "tuvalu": [(179.2168, -8.5199)],
    "vatican city": [(12.4534, 41.9029)]
}

# Geodesic model (WGS84)
geod = Geod(ellps='WGS84')

##############################################################################
# 2) GEODESIC / DIRECTION HELPERS (SAME SAMPLING/SELECTION AS DISTANCE)
##############################################################################

def geodesic_distance(lon1, lat1, lon2, lat2):
    _, _, dist_m = geod.inv(lon1, lat1, lon2, lat2)
    return dist_m / 1000.0

def geodesic_forward_azimuth(lon1, lat1, lon2, lat2):
    fwd_az, _, _ = geod.inv(lon1, lat1, lon2, lat2)
    return (fwd_az + 360.0) % 360.0

def azimuth_to_8dir(a):
    a = (a + 360.0) % 360.0
    if (a >= 337.5) or (a < 22.5):  return "N"
    if 22.5 <= a < 67.5:            return "NE"
    if 67.5 <= a < 112.5:           return "E"
    if 112.5 <= a < 157.5:          return "SE"
    if 157.5 <= a < 202.5:          return "S"
    if 202.5 <= a < 247.5:          return "SW"
    if 247.5 <= a < 292.5:          return "W"
    return "NW"

def direction_point_to_point(lon1, lat1, lon2, lat2):
    return azimuth_to_8dir(geodesic_forward_azimuth(lon1, lat1, lon2, lat2))

def _minpair_polygon_to_polygon(polyA, polyB, samplesA, samplesB):
    if not polyA or polyA.is_empty or not polyB or polyB.is_empty:
        return None
    bA, bB = polyA.boundary, polyB.boundary
    stepA, stepB = bA.length / samplesA, bB.length / samplesB
    ptsA = [(bA.interpolate(i*stepA).x, bA.interpolate(i*stepA).y) for i in range(samplesA+1)]
    ptsB = [(bB.interpolate(j*stepB).x, bB.interpolate(j*stepB).y) for j in range(samplesB+1)]
    best, min_d = None, float('inf')
    for xA, yA in ptsA:
        for xB, yB in ptsB:
            d = geodesic_distance(xA, yA, xB, yB)
            if d < min_d:
                min_d = d
                best = (xA, yA, xB, yB)
    return best

def direction_polygon_to_polygon(polyA, polyB, samplesA, samplesB):
    best = _minpair_polygon_to_polygon(polyA, polyB, samplesA, samplesB)
    if not best: return None
    xA, yA, xB, yB = best
    return direction_point_to_point(xA, yA, xB, yB)

def _minpair_point_to_polygon(lon, lat, poly, samples):
    if not poly or poly.is_empty: return None
    b = poly.boundary
    step = b.length / samples
    best, min_d = None, float('inf')
    for i in range(samples+1):
        pt = b.interpolate(i*step)
        d = geodesic_distance(pt.x, pt.y, lon, lat)
        if d < min_d:
            min_d = d
            best = (pt.x, pt.y)
    return best

def direction_point_to_polygon(lon, lat, poly, samples):
    tgt = _minpair_point_to_polygon(lon, lat, poly, samples)
    if not tgt: return None
    xB, yB = tgt
    return direction_point_to_point(lon, lat, xB, yB)

def direction_multiple_points_to_multiple_points(points1, points2):
    best, min_d = None, float('inf')
    for x1, y1 in points1:
        for x2, y2 in points2:
            d = geodesic_distance(x1, y1, x2, y2)
            if d < min_d:
                min_d = d
                best = (x1, y1, x2, y2)
    if not best: return None
    x1, y1, x2, y2 = best
    return direction_point_to_point(x1, y1, x2, y2)

def direction_multiple_points_to_polygon(points, poly, samples):
    best, min_d = None, float('inf')
    b = poly.boundary
    step = b.length / samples
    bpts = [(b.interpolate(i*step).x, b.interpolate(i*step).y) for i in range(samples+1)]
    for x1, y1 in points:
        for x2, y2 in bpts:
            d = geodesic_distance(x1, y1, x2, y2)
            if d < min_d:
                min_d = d
                best = (x1, y1, x2, y2)
    if not best: return None
    x1, y1, x2, y2 = best
    return direction_point_to_point(x1, y1, x2, y2)

def create_geodesic_buffer(lon, lat, radius_km, num_points=360):
    angles = list(range(0, 360, max(1, int(360/num_points))))
    pts = []
    for az in angles:
        x, y, _ = geod.fwd(lon, lat, az, radius_km*1000)
        pts.append((x, y))
    return Polygon(pts)

##############################################################################
# 3) MAINLAND FILTERING (RULES & SPECIAL CASES PRESERVED)
##############################################################################

def filter_polygons(multi_or_poly, country_name):
    if isinstance(multi_or_poly, Polygon):
        polygons = [multi_or_poly]
    elif isinstance(multi_or_poly, MultiPolygon):
        polygons = list(multi_or_poly.geoms)
    else:
        return None
    polygons = [p for p in polygons if p and not p.is_empty]

    # Russia: exclude Kaliningrad & Crimea
    if country_name == 'russia':
        kal_lon = (19.0, 23.0); kal_lat = (54.0, 55.5)
        cri_lon = (32.0, 36.5); cri_lat = (44.0, 46.5)
        def in_box(p, x_rng, y_rng):
            c = p.centroid; return (x_rng[0] <= c.x <= x_rng[1]) and (y_rng[0] <= c.y <= y_rng[1])
        polygons = [p for p in polygons if not in_box(p, kal_lon, kal_lat) and not in_box(p, cri_lon, cri_lat)]

    # United States: keep 50 states only
    if country_name == 'united states':
        def in_50(p):
            c = p.centroid; lat, lon = c.y, c.x
            mainland = (-125.0 <= lon <= -66.0) and (24.4 <= lat <= 49.5)
            alaska   = (-172.0 <= lon <= -130.0) and (51.2 <= lat <= 72.0)
            hawaii   = (-161.0 <= lon <= -154.0) and (18.5 <= lat <= 23.0)
            return mainland or alaska or hawaii
        polygons = [p for p in polygons if in_50(p)]

    # Japan: 4 main islands + Tsushima buffer, exclude < 30N
    if country_name == 'japan':
        polygons = [p for p in polygons if p.centroid.y >= 30.0]
        polys_sorted = sorted(polygons, key=lambda p: p.area, reverse=True)
        main4 = polys_sorted[:4]
        tsushima = Point(129.3, 34.4).buffer(0.05)
        out_polys = main4 + [tsushima]
        return MultiPolygon(out_polys) if out_polys else None

    # Norway: add small buffer at (16.0E, 68.5N)
    if country_name == 'norway':
        polys_sorted = sorted(polygons, key=lambda p: p.area, reverse=True)
        main = polys_sorted[0] if polys_sorted else None
        extra = Point(16.0, 68.5).buffer(0.05)
        return unary_union([main, extra]) if main else extra

    # United Kingdom: within 620 km of Manchester
    if country_name == 'united kingdom':
        buf = create_geodesic_buffer(-2.25, 53.48, 620)
        filtered = [p.intersection(buf) for p in polygons]
        filtered = [p for p in filtered if p and not p.is_empty]
        return unary_union(filtered) if filtered else None

    # Croatia: add three coastal buffers
    if country_name == 'croatia':
        polys_sorted = sorted(polygons, key=lambda p: p.area, reverse=True)
        main = polys_sorted[0] if polys_sorted else None
        pts = [Point(18.5, 42.4), Point(18.1, 42.6), Point(17.8, 42.9)]
        bufs = [pt.buffer(0.05) for pt in pts]
        return unary_union([main] + bufs) if main else MultiPolygon(bufs)

    # Ukraine: add Crimea bbox
    if country_name == 'ukraine':
        crimea = Polygon([(32.0, 44.0),(36.5, 44.0),(36.5, 46.5),(32.0, 46.5),(32.0, 44.0)])
        polygons.append(crimea)

    # Denmark: within 320 km of Copenhagen
    if country_name == 'denmark':
        buf = create_geodesic_buffer(12.56, 55.68, 320)
        filtered = [p.intersection(buf) for p in polygons]
        filtered = [p for p in filtered if p and not p.is_empty]
        return unary_union(filtered) if filtered else None

    # Standard table rules
    polys_sorted = sorted(polygons, key=lambda p: p.area, reverse=True)
    if not polys_sorted:
        return None
    rule = POLYGON_SELECTION_RULES.get(country_name, {'count': 1})
    if rule.get('all', False):
        return MultiPolygon(polys_sorted)
    if 'count' in rule:
        return MultiPolygon(polys_sorted[:rule['count']])
    if 'distance_threshold' in rule:
        main = polys_sorted[0]; keep = [main]
        def centroid_distance(a, b):
            ca, cb = a.centroid, b.centroid
            return geodesic_distance(ca.x, ca.y, cb.x, cb.y)
        for p in polys_sorted[1:]:
            if centroid_distance(main, p) <= rule['distance_threshold']:
                keep.append(p)
        return MultiPolygon(keep)
    return polys_sorted[0]

##############################################################################
# 4) NAME NORMALIZATION (PRESERVED)
##############################################################################

def normalize_name(raw):
    import re
    s = str(raw).lower().strip()
    if s in VALID_COUNTRIES: return s
    if s in SYNONYM_MAP and SYNONYM_MAP[s] in VALID_COUNTRIES:
        return SYNONYM_MAP[s]
    t = re.sub(r'[\(\),\'’\.]', '', s).replace("  ", " ").strip()
    if t in SYNONYM_MAP and SYNONYM_MAP[t] in VALID_COUNTRIES:
        return SYNONYM_MAP[t]
    if t in VALID_COUNTRIES: return t
    return ""

##############################################################################
# 5) MAIN: ALL-PAIRS 8-DIRECTION MATRIX (WITH PROGRESS)
##############################################################################

def main():
    shapefile_path = os.path.join(".", "data", "ne_110m_admin_0_countries.shp")
    output_file = os.path.join(".", "outputs", "country_directions.json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    print("==> Loading shapefile ...")
    gdf = gpd.read_file(shapefile_path)
    if gdf.crs and gdf.crs.to_string() != "EPSG:4326":
        print("==> Reprojecting to EPSG:4326 ...")
        gdf = gdf.to_crs(epsg=4326)

    possible_name_cols = [
        "ADMIN","NAME","NAME_LONG","SOVEREIGNT","BRK_NAME","FORMAL_EN","GEOUNIT","GU_A3","ISO_A3","ISO_A2"
    ]
    found_cols = [c for c in possible_name_cols if c in gdf.columns]
    if not found_cols:
        raise ValueError("No known name columns found in the shapefile.")

    def extract_country(row):
        for c in found_cols:
            nm = normalize_name(row[c])
            if nm in VALID_COUNTRIES:
                return nm
        return ""

    total = len(gdf)
    print(f"==> Found {total} rows. Extracting and filtering polygons ...")

    country_geoms = {}
    for idx, (_, row) in enumerate(gdf.iterrows(), start=1):
        if idx == 1 or idx % 20 == 0 or idx == total:
            print(f"   [geom {idx}/{total}] parsing ...")
        nm = extract_country(row)
        if not nm:
            continue
        filtered = filter_polygons(row.geometry, nm)
        if filtered and not filtered.is_empty:
            if nm not in country_geoms:
                country_geoms[nm] = filtered
            else:
                country_geoms[nm] = unary_union([country_geoms[nm], filtered])

    # Ensure we have entries for the full set (some None -> micronation fallback)
    final_polygons = {c: country_geoms.get(c, None) for c in VALID_COUNTRIES}

    # Prepare matrix
    all_countries_sorted = sorted(VALID_COUNTRIES)
    N = len(all_countries_sorted)
    direction_map = {c: {} for c in all_countries_sorted}

    print(f"\n==> Computing pairwise directions among {N} countries ...")
    t0 = time.time()

    for i, c1 in enumerate(all_countries_sorted, start=1):
        poly1 = final_polygons[c1]
        s1 = get_sample_size(c1)

        # progress banner per row
        print(f"[{i}/{N}] {c1} -> others ...", flush=True)

        for j, c2 in enumerate(all_countries_sorted, start=1):
            # Mirror if we already computed c2->c1
            if j < i:
                prev = direction_map[c2].get(c1, None)
                # Opposite sector for the reverse direction (if known)
                if   prev == "N":  direction_map[c1][c2] = "S"
                elif prev == "NE": direction_map[c1][c2] = "SW"
                elif prev == "E":  direction_map[c1][c2] = "W"
                elif prev == "SE": direction_map[c1][c2] = "NW"
                elif prev == "S":  direction_map[c1][c2] = "N"
                elif prev == "SW": direction_map[c1][c2] = "NE"
                elif prev == "W":  direction_map[c1][c2] = "E"
                elif prev == "NW": direction_map[c1][c2] = "SE"
                else:               direction_map[c1][c2] = prev  # None/unknown
                continue

            if c1 == c2:
                direction_map[c1][c2] = None
                continue

            poly2 = final_polygons[c2]
            s2 = get_sample_size(c2)

            # A) Both polygons
            if poly1 is not None and poly2 is not None:
                d8 = direction_polygon_to_polygon(poly1, poly2, s1, s2)
                direction_map[c1][c2] = d8 if d8 is not None else "unknown"

            # B) Both micronations
            elif (c1 in MICRONATION_COORDS) and (c2 in MICRONATION_COORDS):
                d8 = direction_multiple_points_to_multiple_points(
                    MICRONATION_COORDS[c1], MICRONATION_COORDS[c2]
                )
                direction_map[c1][c2] = d8 if d8 is not None else "unknown"

            # C) c1 polygon, c2 micronation
            elif poly1 is not None and (c2 in MICRONATION_COORDS):
                b = poly1.boundary
                step = b.length / s1
                bpts = [(b.interpolate(k*step).x, b.interpolate(k*step).y) for k in range(s1+1)]
                best, min_d = None, float('inf')
                for x2, y2 in MICRONATION_COORDS[c2]:
                    for xA, yA in bpts:
                        d = geodesic_distance(xA, yA, x2, y2)
                        if d < min_d:
                            min_d = d
                            best = (xA, yA, x2, y2)
                if best:
                    xA, yA, xB, yB = best
                    direction_map[c1][c2] = direction_point_to_point(xA, yA, xB, yB)
                else:
                    direction_map[c1][c2] = "unknown"

            # D) c1 micronation, c2 polygon
            elif (c1 in MICRONATION_COORDS) and poly2 is not None:
                pts1 = MICRONATION_COORDS[c1]
                d8 = direction_multiple_points_to_polygon(pts1, poly2, s2)
                direction_map[c1][c2] = d8 if d8 is not None else "unknown"

            else:
                direction_map[c1][c2] = "unknown"

        # small heartbeat every few rows
        if i % 10 == 0 or i == N:
            elapsed = time.time() - t0
            print(f"   ...completed {i}/{N} rows in ~{elapsed:.1f}s", flush=True)

    elapsed_total = time.time() - t0
    print(f"\n==> All directions computed in ~{elapsed_total/60:.1f} minutes.")

    # Save single JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(direction_map, f, indent=2)

    print(f"==> Saved matrix to '{output_file}'")

if __name__ == "__main__":
    main()
