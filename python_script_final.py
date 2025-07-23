#!/usr/bin/env python
# Multi-block STAC Catalog Generator

import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime

import rasterio
import geopandas as gpd
import matplotlib.pyplot as plt
import pystac
import constants
from shapely.geometry import mapping, box
from pystac.extensions.table import TableExtension
from pystac.extensions.classification import ClassificationExtension
from pystac import Asset, MediaType

def extract_raster_dates_from_filename(filename):
    try:
        print(filename)
        parts = filename.split('_')
        start_date = datetime.strptime(parts[2], "%Y-%m-%d")
        end_date = datetime.strptime(parts[3], "%Y-%m-%d")
    except Exception as e:
        raise ValueError(f"Failed to extract raster dates from filename '{filename}': {e}")
    return start_date, end_date    

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
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    fig, ax = plt.subplots(figsize=(3, 3))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    gdf.plot(ax=ax, color="lightblue", edgecolor="blue", linewidth=0.5)
    ax.axis('off')
    plt.savefig(out_path, dpi=150, bbox_inches='tight', pad_inches=0, facecolor=fig.get_facecolor())
    plt.close()

def create_raster_item(filename, raster_path, raster_dir, raster_thumbnail, raster_style_file):
    start_date, end_date = extract_raster_dates_from_filename(filename)
    with rasterio.open(raster_path) as src:
        bounds = src.bounds
        geom = mapping(box(*bounds))
        bbox = [bounds.left, bounds.bottom, bounds.right, bounds.top]

    generate_raster_thumbnail(raster_path, raster_thumbnail)
    style_info = parse_qml_classes(raster_style_file)

    #style_json_path = os.path.join(raster_dir, "legend.json")
    legend_filename = f"{os.path.basename(raster_path).replace('.tif', '')}_legend.json"
    style_json_path = os.path.join(raster_dir, legend_filename)
    with open(style_json_path, "w") as f:
        json.dump(style_info, f, indent=2)

    item = pystac.Item(
        id=constants.raster_lulc_id,
        geometry=geom,
        bbox=bbox,
        datetime=datetime.now(),
        start_datetime=start_date,
        end_datetime=end_date,
        properties={
            "title": constants.raster_lulc_title,
            "description": constants.raster_lulc_description,
            "lulc:classes": style_info
        }
    )

    item.stac_extensions.append(ClassificationExtension.get_schema_uri())

    item.add_asset("data", Asset(
        href=f"{constants.data_url}/{filename}",
        media_type=MediaType.GEOTIFF,
        roles=["data"],
        title="Raster Layer"
    ))

    #classification_asset = ClassificationExtension.ext(item.assets["data"], add_if_missing=True)
    #categories = []
    #for cls in style_info:
    #    value = int(cls["value"])
    #    name = cls.get("label") or cls.get("name", "")
    #    entry = {"value": value, "name": name}
    #    if "description" in cls:
    #        entry["description"] = cls["description"]
    #    categories.append(entry)
    #classification_asset.classes = categories

    item.add_asset("thumbnail", Asset(
        href=f"{constants.base_url}/raster/{os.path.basename(raster_thumbnail)}",
        media_type=MediaType.PNG,
        roles=["thumbnail"],
        title="Raster Thumbnail"
    ))

    item.add_asset("legend", Asset(
        href=f"{constants.base_url}/raster/{legend_filename}",
        media_type=MediaType.JSON,
        roles=["metadata"],
        title="Legend JSON"
    ))

    item.add_asset("style", Asset(
        href=f"{constants.data_url}/../{raster_style_file}",
        media_type=MediaType.XML,
        roles=["metadata"],
        title="Raster Style (QML)"
    ))

    item.set_self_href(os.path.join(raster_dir, "item.json"))
    item.save_object()
    return item

def create_vector_item(vector_filename, vector_path, vector_dir, vector_thumbnail, vector_style_file):
    start_date = constants.DEFAULT_START_DATE
    end_date = constants.DEFAULT_END_DATE
    gdf = gpd.read_file(vector_path)
    geom = mapping(gdf.unary_union)
    bounds = gdf.total_bounds
    bbox = [float(b) for b in bounds]
    generate_vector_thumbnail(vector_path, vector_thumbnail)

    item = pystac.Item(
        id=constants.swb_vector_id,
        geometry=geom,
        bbox=bbox,
        datetime=start_date,
        start_datetime=start_date,
        end_datetime=end_date,
        properties={
            "title": constants.swb_vector_title,
            "description": constants.swb_vector_description,
        }
    )

    table_ext = TableExtension.ext(item, add_if_missing=True)
    table_ext.columns = [
        {"name": col, "type": str(dtype)}
        for col, dtype in gdf.dtypes.items()
    ]
    item.properties["table:summary"] = {
        "number_of_records": gdf.shape[0]
    }

    item.add_asset("data", Asset(
        href=f"{constants.data_url}/{vector_filename}",
        media_type=MediaType.GEOJSON,
        roles=["data"],
        title="Vector Layer"
    ))

    item.add_asset("thumbnail", Asset(
        href=f"{constants.base_url}/vector/{os.path.basename(vector_thumbnail)}",
        media_type=MediaType.PNG,
        roles=["thumbnail"],
        title="Vector Thumbnail"
    ))

    item.add_asset("style", Asset(
        href=f"{constants.data_url}/../{vector_style_file}",
        media_type=MediaType.XML,
        roles=["style"],
        title="Vector Style"
    ))

    item.set_self_href(os.path.join(vector_dir, "item.json"))
    item.save_object()
    return item

def generate_stac_for_block(info):
    base_dir = 'data/'
    corestack_dir = os.path.join(base_dir, 'CorestackCatalogs')
    block = info['block_name']
    raster_filename = info['raster_file']
    vector_filename = info['vector_file']
    raster_style_file = os.path.join(base_dir, info['raster_qml'])
    vector_style_file = os.path.join(base_dir, info['vector_qml'])
    raster_path = os.path.join(base_dir, raster_filename)
    vector_path = os.path.join(base_dir, vector_filename)
    block_dir = os.path.join(corestack_dir, block)
    raster_dir = os.path.join(block_dir, 'raster')
    vector_dir = os.path.join(block_dir, 'vector')
    os.makedirs(raster_dir, exist_ok=True)
    os.makedirs(vector_dir, exist_ok=True)
    raster_thumbnail = os.path.join(raster_dir, f'{block}_raster_thumbnail.png')
    vector_thumbnail = os.path.join(vector_dir, f'{block}_vector_thumbnail.png')

    raster_item = create_raster_item(raster_filename, raster_path, raster_dir, raster_thumbnail, raster_style_file)
    vector_item = create_vector_item(vector_filename, vector_path, vector_dir, vector_thumbnail, vector_style_file)

    catalog = pystac.Catalog(
        id=block,
        title=f"STAC for {block}",
        description=f"STAC catalog for {block} block"
    )
    catalog.add_item(raster_item)
    catalog.add_item(vector_item)
    catalog.set_self_href(os.path.join(block_dir, 'catalog.json'))
    catalog.normalize_and_save(block_dir, catalog_type=pystac.CatalogType.SELF_CONTAINED)
    print(f"✅ STAC catalog created for block: {block}")

def generate_root_catalog(blocks_info, base_dir, corestack_dir):
    root_catalog = pystac.Catalog(
        id="corestack",
        title="CorestackCatalogs",
        description="Root catalog containing all subcatalogs"
    )
    for info in blocks_info:
        block = info["block_name"]
        block_catalog_path = os.path.join(corestack_dir, block, "catalog.json")
        if os.path.exists(block_catalog_path):
            block_catalog = pystac.read_file(block_catalog_path)
            root_catalog.add_child(block_catalog)
    root_catalog.set_self_href(os.path.join(corestack_dir, "catalog.json"))
    root_catalog.normalize_and_save(corestack_dir, catalog_type=pystac.CatalogType.SELF_CONTAINED)
    print(f"✅ Root catalog generated at {os.path.join(corestack_dir, 'catalog.json')}")

# 🧱 Define blocks
blocks_info = [
    {
        "block_name": "gobindpur",
        "raster_file": "saraikela-kharsawan_gobindpur_2023-07-01_2024-06-30_LULCmap_10m.tif",
        "vector_file": "swb2_saraikela-kharsawan_gobindpur.geojson",
        "raster_qml": "style_file.qml",
        "vector_qml": "swb_style.qml"
    },
    {
        "block_name": "mirzapur",
        "raster_file":"Mirzapur_Mirzapur_2023-07-01_2024-06-30_LULCmap_10m.tif",
        "vector_file":"surface_waterbodies_mirzapur_mirzapur.geojson",
        "raster_qml": "style_file.qml",
        "vector_qml": "swb_style.qml"
    },
    {
        "block_name": "koraput",
        "raster_file": "Narayanpatana_Koraput_2023-07-01_2024-06-30_LULCmap_10m.tif",
        "vector_file": "surface_waterbodies_koraput_narayanpatana.geojson",
        "raster_qml": "style_file.qml",
        "vector_qml": "swb_style.qml"
    }
]

# 🔁 Generate STAC for each block
for block_info in blocks_info:
    print(f"🔄 Processing block: {block_info['block_name']}")
    generate_stac_for_block(block_info)

# 🔗 Generate root catalog
generate_root_catalog(blocks_info, base_dir="data/", corestack_dir="data/CorestackCatalogs")

