#!/usr/bin/env python
# coding: utf-8

# ## Python notebook for generating the STAC catalog json and corresponding Item json for Raster & Vector layers
# 
# ### Tools:
# 1. Pystac 
# 2. Rasterio
# 3. Geopandas
# 4. Matplotlib
# 
# This notebook returns Catalog json for Raster and Vector layers.

# ### 1. Importing the required modules

# In[2]:


import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime

import rasterio
import geopandas as gpd
import matplotlib.pyplot as plt
import pystac
import sys
import constants
from shapely.geometry import mapping, box
from pystac.extensions.table import TableExtension
from pystac import Asset, MediaType





# ### 2. Defining the variables used in the notebook

# In[3]:


base_dir="data/"
qml_path="data/style_file_new.qml"
vector_qml_file ="data/swb_style.qml"

raster_filename="saraikela-kharsawan_gobindpur_2023-07-01_2024-06-30_LULCmap_10m.tif"
vector_filename="swb2_saraikela-kharsawan_gobindpur.geojson"

corestack_dir = os.path.join(base_dir, "CorestackCatalogs")
gobindpur_dir = os.path.join(corestack_dir, "gobindpur")
raster_dir = os.path.join(gobindpur_dir, "raster")
vector_dir = os.path.join(gobindpur_dir, "vector")

os.makedirs(raster_dir, exist_ok=True)
os.makedirs(vector_dir, exist_ok=True)


raster_path = os.path.join(base_dir, raster_filename)
vector_path = os.path.join(base_dir, vector_filename)

raster_thumbnail = os.path.join(raster_dir, "raster_thumbnail.png")
vector_thumbnail = os.path.join(vector_dir, "vector_thumbnail.png")

raster_style_file = os.path.join(base_dir, "style_file.qml")
vector_style_file = os.path.join(base_dir, "swb_style.qml")


# ### 3. For Raster layers the data range fecthed from filename

# In[4]:


def extract_raster_dates_from_filename(filename):
    try:
        print(filename)
        parts = filename.split('_')
        start_date = datetime.strptime(parts[2], "%Y-%m-%d")
        end_date = datetime.strptime(parts[3], "%Y-%m-%d")
        print(start_date)
        print(end_date)
    except Exception as e:
        raise ValueError(f"Failed to extract raster dates from filename '{filename}': {e}")
        
    return start_date, end_date    


# In[5]:


extract_raster_dates_from_filename(filename=raster_filename)


# ### 4. Parsing the QML file for Raster Layers

# In[6]:


import os
import json
import rasterio
import pystac
from shapely.geometry import box, mapping
from xml.etree import ElementTree as ET
from pystac.extensions.classification import ClassificationExtension

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


# ### 5. Generating the thumbnails from the files 

# In[7]:


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


# ### 6. Creating the Raster items and adding the assets

# In[ ]:


def create_raster_item(filename):
    try:
        start_date, end_date = extract_raster_dates_from_filename(filename=raster_filename)
    except ValueError as e:
        raise RuntimeError(f"Raster item creation failed: {str(e)}")

    with rasterio.open(raster_path) as src:
        bounds = src.bounds
        geom = mapping(box(*bounds))
        bbox = [bounds.left, bounds.bottom, bounds.right, bounds.top]

    # Generate thumbnail
    generate_raster_thumbnail(raster_path, raster_thumbnail)

    # Parse QML style
    style_info = parse_qml_classes(raster_style_file)
    print(style_info)

    # Save legend as JSON
    style_json_path = os.path.join(raster_dir, "legend.json")
    with open(style_json_path, "w") as f:
        json.dump(style_info, f, indent=2)

    # Create STAC item
    item = pystac.Item(
        id=constants.raster_lulc_id,
        geometry=geom,
        bbox=bbox,
        datetime=datetime,
        start_datetime=start_date,
        end_datetime=end_date,
        properties={
            "title": constants.raster_lulc_title,
            "description": constants.raster_lulc_description,
            "lulc:classes": style_info  # Optional custom property
        }
    )

    # Declare classification extension
    
    item.stac_extensions.append(ClassificationExtension.get_schema_uri())

# Add raster asset (GeoTIFF)
item.add_asset("data", pystac.Asset(
    href=f"{constants.data_url}/{raster_filename}",
    media_type=pystac.MediaType.GEOTIFF,
    roles=["data"],
    title="Raster Layer"
))

# Attach classification extension to "data" asset
classification_asset = ClassificationExtension.ext(item.assets["data"], add_if_missing=True)

categories = []
for cls in style_info:
    value = int(cls["value"])
    name = cls.get("label") or cls.get("name", "")
    entry = {"value": value, "name": name}
    if "description" in cls:
        entry["description"] = cls["description"]
    categories.append(entry)

classification_asset.classes = categories

    # Add additional assets
    item.add_asset("thumbnail", pystac.Asset(
        href=f"{constants.base_url}/raster/thumbnail.png",
        media_type=pystac.MediaType.PNG,
        roles=["thumbnail"],
        title="Raster Thumbnail"
    ))

    item.add_asset("legend", pystac.Asset(
        href=f"{constants.base_url}/raster/legend.json",
        media_type=pystac.MediaType.JSON,
        roles=["metadata"],
        title="Legend JSON"
    ))

    item.add_asset("style", pystac.Asset(
        href=f"{constants.data_url}/../{raster_style_file}",
        media_type=pystac.MediaType.XML,
        roles=["metadata"],
        title="Raster Style (QML)"
    ))

    # Save the item
    item.set_self_href(os.path.join(raster_dir, "item.json"))
    item.save_object()

    return item


# In[13]:


raster_item=create_raster_item(filename=raster_filename)


# ### 7.Creating the Vector items and adding the assets

# In[ ]:


def create_vector_item(vector_filename, vector_path, vector_dir, vector_thumbnail, vector_style_file):
    start_date = constants.DEFAULT_START_DATE
    end_date = constants.DEFAULT_END_DATE

    
    gdf = gpd.read_file(vector_path)

   
    geom = mapping(gdf.unary_union)
    bounds = gdf.total_bounds
    bbox = [float(b) for b in bounds]

    
    generate_vector_thumbnail(vector_path, vector_thumbnail)



    # Create base item
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

    # Use table extension
    table_ext = TableExtension.ext(item, add_if_missing=True)

    table_ext.columns = [
        {
            "name": col,
            "type": str(dtype),
        }
        for col, dtype in gdf.dtypes.items()
    ]

    #table_ext.row_count = gdf.shape[0]
    #  Add a descriptive summary
    item.properties["table:summary"] = {
    "number_of_records": gdf.shape[0]
}


    # Add assets
    item.add_asset("data", Asset(
        href=f"{constants.data_url}/{vector_filename}",
        media_type=MediaType.GEOJSON,
        roles=["data"],
        title="Vector Layer"
    ))

    item.add_asset("thumbnail", Asset(
        href=f"{constants.base_url}/vector/thumbnail.png",
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

    # Save item
    item.set_self_href(os.path.join(vector_dir, "item.json"))
    item.save_object()

    return item


# In[ ]:


vector_item=create_vector_item(vector_filename, vector_path, vector_dir, vector_thumbnail, vector_style_file)
print(vector_item)


# In[ ]:





# In[ ]:


gdf = gpd.read_file(vector_path)


# In[ ]:


gdf.shape


# df.shape

# In[ ]:


gdf.columns


# In[ ]:


gdf.describe()


# In[ ]:


gdf.dtypes


# In[ ]:


vector_item = create_vector_item(vector_filename=vector_filename)


# ### 8. Using the raster and vector items created and generating the Catalog 

# In[ ]:


catalog = pystac.Catalog(
    id=constants.id_main,
    title=constants.title_main,
    description=constants.description_main
)
catalog.add_item(create_raster_item(filename=raster_filename))
catalog.add_item(create_vector_item(
    vector_filename=vector_filename,
    vector_path=vector_path,
    vector_dir=vector_dir,
    vector_thumbnail=vector_thumbnail,
    vector_style_file=vector_style_file
))
catalog.set_self_href(os.path.join(gobindpur_dir, "catalog.json"))

corestack_catalog = pystac.Catalog(
    id="corestack",
    title="CorestackCatalogs",
    description="Root catalog containing all subcatalogs"
)
corestack_catalog.add_child(catalog)
corestack_catalog.set_self_href(os.path.join(corestack_dir, "catalog.json"))
corestack_catalog.normalize_and_save(corestack_dir, catalog_type=pystac.CatalogType.SELF_CONTAINED)

print(f" Root STAC Catalog created at: {os.path.join(corestack_dir, 'catalog.json')}")

