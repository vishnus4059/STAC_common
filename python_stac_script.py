import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import rasterio
import geopandas as gpd
import matplotlib.pyplot as plt
import pystac
from shapely.geometry import mapping, box

from constants import DEFAULT_START_DATE, DEFAULT_END_DATE

# === Local Paths
base_dir = "/home/vishnu/corestack_STAC/STAC_common/data"
corestack_dir = os.path.join(base_dir, "Corestack Catalogs")
gobindpur_dir = os.path.join(corestack_dir, "gobindpur")
raster_dir = os.path.join(gobindpur_dir, "raster")
vector_dir = os.path.join(gobindpur_dir, "vector")

os.makedirs(raster_dir, exist_ok=True)
os.makedirs(vector_dir, exist_ok=True)

# === GitHub Raw URL Base
http_base = "https://raw.githubusercontent.com/vishnus4059/STAC_common/main/data/Corestack%20Catalogs/gobindpur"

# === Input Files
raster_filename = "saraikela-kharsawan_gobindpur_2023-07-01_2024-06-30_LULCmap_10m.tif"
vector_filename = "swb2_saraikela-kharsawan_gobindpur.geojson"
raster_path = os.path.join(base_dir, raster_filename)
vector_path = os.path.join(base_dir, vector_filename)

raster_thumb = os.path.join(raster_dir, "thumbnail.png")
vector_thumb = os.path.join(vector_dir, "thumbnail.png")

raster_style_file = os.path.join(base_dir, "style_file.qml")
vector_style_file = os.path.join(base_dir, "swb_style.qml")

# === Extract Dates from Filename
def extract_dates_from_filename(filename):
    try:
        parts = filename.split('_')
        start_date = datetime.strptime(parts[2], "%Y-%m-%d")
        end_date = datetime.strptime(parts[3], "%Y-%m-%d")
    except Exception as e:
        print(f"⚠️ Failed to extract dates from filename '{filename}': {e}")
        start_date = DEFAULT_START_DATE
        end_date = DEFAULT_END_DATE
    return start_date, end_date

# === Parse QML Style
def parse_qml_classes(qml_path):
    tree = ET.parse(qml_path)
    root = tree.getroot()
    classes = []

    for entry in root.findall(".//paletteEntry"):
        class_info = {}
        for attr_key, attr_value in entry.attrib.items():
            if attr_key == "value":
                try:
                    class_info[attr_key] = int(attr_value)
                except ValueError:
                    class_info[attr_key] = attr_value
            else:
                class_info[attr_key] = attr_value
        classes.append(class_info)
    return classes

# === Thumbnail Generators
def generate_raster_thumbnail(tif_path, out_path):
    with rasterio.open(tif_path) as src:
        arr = src.read(1)
    plt.figure(figsize=(3, 3))
    plt.imshow(arr, cmap="tab20")
    plt.axis('off')
    plt.savefig(out_path, bbox_inches='tight', pad_inches=0)
    plt.close()

def generate_vector_thumbnail(vector_path, out_path):
    gdf = gpd.read_file(vector_path)
    fig, ax = plt.subplots(figsize=(3, 3))

    # Ensure white background
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Plot with visible styling
    gdf.plot(ax=ax, edgecolor="black", facecolor="lightblue", linewidth=0.5)

    ax.axis('off')
    plt.savefig(out_path, bbox_inches='tight', pad_inches=0, facecolor=fig.get_facecolor())
    plt.close()


# === Raster Item
def create_raster_item():
    start_date, end_date = extract_dates_from_filename(raster_filename)
    with rasterio.open(raster_path) as src:
        bounds = src.bounds
        geom = mapping(box(*bounds))
        bbox = [bounds.left, bounds.bottom, bounds.right, bounds.top]

    generate_raster_thumbnail(raster_path, raster_thumb)
    style_info = parse_qml_classes(raster_style_file)
    style_json_path = os.path.join(raster_dir, "legend.json")
    with open(style_json_path, "w") as f:
        json.dump(style_info, f, indent=2)

    item = pystac.Item(
        id="gobindpur_lulc_raster",
        geometry=geom,
        bbox=bbox,
        datetime=end_date,
        properties={
            "proj:epsg": 4326,
            "title": "LULC Raster - Gobindpur",
            "description": "Land Use Land Cover raster map of Gobindpur",
            "lulc:classes": style_info,
            "start_datetime": start_date.isoformat(),
            "end_datetime": end_date.isoformat()
        }
    )
    item.add_asset("data", pystac.Asset(
        href=f"{http_base}/{raster_filename}",
        media_type=pystac.MediaType.GEOTIFF,
        roles=["data"],
        title="LULC Geotiff"
    ))
    item.add_asset("thumbnail", pystac.Asset(
        href=f"{http_base}/raster/thumbnail.png",
        media_type=pystac.MediaType.PNG,
        roles=["thumbnail"],
        title="Raster Thumbnail"
    ))
    item.add_asset("legend", pystac.Asset(
        href=f"{http_base}/raster/legend.json",
        media_type=pystac.MediaType.JSON,
        roles=["metadata"],
        title="Legend JSON"
    ))
    item.set_self_href(os.path.join(raster_dir, "item.json"))
    item.save_object()
    return item

# === Vector Item
def create_vector_item():
    start_date, end_date = extract_dates_from_filename(raster_filename)

    gdf = gpd.read_file(vector_path)
    geom = mapping(gdf.union_all())
    bounds = gdf.total_bounds
    bbox = [float(b) for b in bounds]

    generate_vector_thumbnail(vector_path, vector_thumb)
    style_info = parse_qml_classes(vector_style_file)
    style_json_path = os.path.join(vector_dir, "style.json")
    with open(style_json_path, "w") as f:
        json.dump(style_info, f, indent=2)

    item = pystac.Item(
        id="gobindpur_swb_vector",
        geometry=geom,
        bbox=bbox,
        datetime=end_date,
        properties={
            "proj:epsg": 4326,
            "title": "SWB Vector - Gobindpur",
            "description": "Micro watershed (SWB) vector layer for Gobindpur",
            "style": style_info,
            "start_datetime": start_date.isoformat(),
            "end_datetime": end_date.isoformat()
        }
    )
    item.add_asset("data", pystac.Asset(
        href=f"{http_base}/{vector_filename}",
        media_type=pystac.MediaType.GEOJSON,
        roles=["data"],
        title="SWB GeoJSON"
    ))
    item.add_asset("thumbnail", pystac.Asset(
        href=f"{http_base}/vector/thumbnail.png",
        media_type=pystac.MediaType.PNG,
        roles=["thumbnail"],
        title="Vector Thumbnail"
    ))
    item.add_asset("style", pystac.Asset(
        href=f"{http_base}/vector/style.json",
        media_type=pystac.MediaType.JSON,
        roles=["metadata"],
        title="Style JSON"
    ))
    item.set_self_href(os.path.join(vector_dir, "item.json"))
    item.save_object()
    return item

# === Gobindpur Subcatalog
gobindpur_catalog = pystac.Catalog(
    id="gobindpur",
    title="GobindpurCatalog",
    description="Gobindpur catalog with LULC raster and SWB vector layers"
)
gobindpur_catalog.add_item(create_raster_item())
gobindpur_catalog.add_item(create_vector_item())
gobindpur_catalog.set_self_href(os.path.join(gobindpur_dir, "catalog.json"))

# === Root Catalog: Corestack Catalogs
corestack_catalog = pystac.Catalog(
    id="corestack",
    title="CorestackCatalogs",
    description="Root catalog containing all subcatalogs like Gobindpur"
)
corestack_catalog.add_child(gobindpur_catalog)
corestack_catalog.set_self_href(os.path.join(corestack_dir, "catalog.json"))
corestack_catalog.normalize_and_save(corestack_dir, catalog_type=pystac.CatalogType.SELF_CONTAINED)

print(f"✅ Root STAC Catalog created at: {os.path.join(corestack_dir, 'catalog.json')}")
