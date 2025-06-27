import ee
import time

try:
    ee.Initialize(project='ee-corestackdev')
except Exception as e:
    ee.Authenticate()
    ee.Initialize(project='ee-corestackdev')

asset_id = "projects/ee-corestackdev/assets/apps/mws/jharkhand/saraikela-kharsawan/gobindpur/swb2_saraikela-kharsawan_gobindpur"


lulc_fc = ee.FeatureCollection(asset_id)
aoi = lulc_fc.geometry().bounds()


task = ee.batch.Export.table.toDrive(
    collection=lulc_fc,
    description='Gobindpur_SWB2_Export',
    folder='GEE_Exports',
    fileNamePrefix='Gobindpur_SWB2_2023_24',
    fileFormat='GeoJSON'
)

task.start()
print("🚀 Export started to Google Drive > GEE_Exports")

while task.active():
    print("⏳ Exporting... Please wait...")
    time.sleep(30)

print(" Export task finished with state:", task.status()['state'])
