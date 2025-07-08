# constants.py
from datetime import datetime

DEFAULT_START_DATE = datetime(2017, 7, 1)
DEFAULT_END_DATE = datetime(2024, 6, 30)


base_url="https://raw.githubusercontent.com/vishnus4059/STAC_common/master/data/CorestackCatalogs/gobindpur"
data_url="https://raw.githubusercontent.com/vishnus4059/STAC_common/master/data/"
raster_lulc_id="lulc_raster"
raster_lulc_description="Land Use Land Cover raster map"
raster_lulc_title="Raster layer"
swb_vector_id="SWB vector"
swb_vector_title="SWB Vector"
swb_vector_description="SWB vector layer"
id_main="gobindpur"
title_main="GobindpurCatalog"
description_main="Gobindpur catalog with LULC raster and SWB vector layers"