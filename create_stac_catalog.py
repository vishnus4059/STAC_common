
import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import rasterio
import geopandas as gpd
import matplotlib.pyplot as plt
import pystac
from shapely.geometry import mapping

# === Paths
data_dir = "/home/vishnu/corestack_STAC/data"
root_dir = os.path.join(data_dir, "gobindpur")
raster_dir = os.path.join(root_dir, "raster")
vector_dir = os.path.join(root_dir, "vector")
os.makedirs(raster_dir, exist_ok=True)
os.makedirs(vector_dir, exist_ok=True)

# === Input Files
raster_path = os.path.join(data_dir, "saraikela-kharsawan_gobindpur_2023-07-01_2024-06-30_LULCmap_10m.tif")
raster_thumb = os.path.join(data_dir, "thumbnail_gobindpur.png")
raster_style_file = os.path.join(data_dir, "style_file.qml")

vector_path = os.path.join(data_dir, "swb2_saraikela-kharsawan_gobindpur.geojson")
vector_thumb = os.path.join(data_dir, "thumbnail.png")
vector_style_file = os.path.join(data_dir, "swb_style.qml")

# === Function to parse QML style and extract symbology
def parse_qml_classes(qml_path):
    tree = ET.parse(qml_path)
    root = tree.getroot()
    classes = []
    for entry in root.findall(".//paletteEntry"):
        value = int(entry.attrib.get("value", -1))
        label = entry.attrib.get("label", f"Class {value}")
        color = entry.attrib.get("color", "#000000")
        classes.append({
            "value": value,
            "label": label,
            "color": color
        })
    return classes

# === Raster Thumbnail Generation
def generate_raster_thumbnail(tif_path, out_path):
    with rasterio.open(tif_path) as src:
        arr = src.read(1)
    plt.figure(figsize=(3, 3))
    plt.imshow(arr, cmap="tab20")
    plt.axis('off')
    plt.savefig(out_path, bbox_inches='tight', pad_inches=0)
    plt.close()

# === Vector Thumbnail Generation
def generate_vector_thumbnail(vector_path, out_path):
    gdf = gpd.read_file(vector_path)
    fig, ax = plt.subplots(figsize=(3, 3))
    gdf.plot(ax=ax, edgecolor="black", facecolor="lightblue")
    ax.axis('off')
    plt.savefig(out_path, bbox_inches='tight', pad_inches=0)
    plt.close()

# === Create Raster Item
def create_raster_item():
    with rasterio.open(raster_path) as src:
        bounds = src.bounds
        geom = mapping(src.bounds)
        bbox = [bounds.left, bounds.bottom, bounds.right, bounds.top]

    raster_item = pystac.Item(
        id="gobindpur_lulc_raster",
        geometry=geom,
        bbox=bbox,
        datetime=datetime(2024, 6, 30),
        properties={
            "proj:epsg": 4326,
            "title": "LULC Raster - Gobindpur",
            "description": "Land Use Land Cover raster map of Gobindpur",
            "legend": parse_qml_classes(raster_style_file)
        }
    )

    raster_item.add_asset("data", pystac.Asset(
        href=raster_path,
        media_type=pystac.MediaType.COG,
        roles=["data"],
        title="LULC COG"
    ))

    raster_item.add_asset("thumbnail", pystac.Asset(
        href=raster_thumb,
        media_type=pystac.MediaType.PNG,
        roles=["thumbnail"],
        title="Raster Thumbnail"
    ))

    item_path = os.path.join(raster_dir, "item.json")
    raster_item.set_self_href(item_path)
    raster_item.save_object()
    return raster_item

# === Create Vector Item
def create_vector_item():
    gdf = gpd.read_file(vector_path)
    geom = mapping(gdf.unary_union)
    bounds = gdf.total_bounds
    bbox = [float(b) for b in bounds]

    vector_item = pystac.Item(
        id="gobindpur_swb_vector",
        geometry=geom,
        bbox=bbox,
        datetime=datetime(2024, 6, 30),
        properties={
            "proj:epsg": 4326,
            "title": "SWB Vector - Gobindpur",
            "description": "Micro watershed (SWB) vector layer for Gobindpur",
            "style": parse_qml_classes(vector_style_file)
        }
    )

    vector_item.add_asset("data", pystac.Asset(
        href=vector_path,
        media_type=pystac.MediaType.GEOJSON,
        roles=["data"],
        title="SWB GeoJSON"
    ))

    vector_item.add_asset("thumbnail", pystac.Asset(
        href=vector_thumb,
        media_type=pystac.MediaType.PNG,
        roles=["thumbnail"],
        title="Vector Thumbnail"
    ))

    item_path = os.path.join(vector_dir, "item.json")
    vector_item.set_self_href(item_path)
    vector_item.save_object()
    return vector_item

# === Generate thumbnails if not already present
if not os.path.exists(raster_thumb):
    generate_raster_thumbnail(raster_path, raster_thumb)

if not os.path.exists(vector_thumb):
    generate_vector_thumbnail(vector_path, vector_thumb)

# === Create Catalog
catalog = pystac.Catalog(
    id="gobindpur",
    title="Gobindpur STAC Catalog",
    description="Gobindpur catalog with LULC raster and SWB vector layers"
)

raster_item = create_raster_item()
vector_item = create_vector_item()

catalog.add_item(raster_item)
catalog.add_item(vector_item)

# === Save Catalog
catalog_path = os.path.join(root_dir, "catalog.json")
catalog.set_self_href(catalog_path)
catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)

print(f"✅ STAC Catalog created at: {catalog_path}")
