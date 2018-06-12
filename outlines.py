# a python script to create center points for labels for the
# Military Grid Reference System (MGRS) zones

from osgeo import ogr
from osgeo import osr
import os
import sys

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + ' ' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def PolygonOutlines(inLayer, outLayer, outLayerName):

   # we're working only with Shapefiles
   driver = ogr.GetDriverByName("ESRI Shapefile")
   
   # set shapefile, driver, and datasource (ds) for the input
   in_layer = inLayer
   in_ds = driver.Open(in_layer, 0)
   in_layer = in_ds.GetLayer()
   in_srs = in_layer.GetSpatialRef()

   # output SpatialReference
   out_srs = osr.SpatialReference()
   out_srs.ImportFromEPSG(3857)
   
   # create the CoordinateTransformation
   coordTrans = osr.CoordinateTransformation(in_srs, out_srs)

   # set and create the output layer (shapefile)
   # remove output file if already there
   output_layer = outLayer
   if os.path.exists(output_layer):
       driver.DeleteDataSource(output_layer)

   out_ds = driver.CreateDataSource(output_layer)
   out_layer = out_ds.CreateLayer(output_layer, out_srs, 
               geom_type = ogr.wkbLineString)

   # get the label layer feature definition
   in_layer_defs = in_layer.GetLayerDefn()

   # add input file fields to output file
   for i in range(0, in_layer_defs.GetFieldCount()):
       defn = in_layer_defs.GetFieldDefn(i)
       out_layer.CreateField(defn)

       # finally, we need to rename the 100km_SQ column so that it doesn't start
       # with a number

   # get the new output layer feature definition
   feat_def = out_layer.GetLayerDefn()

   # grab totals for progress bar
   field_count = in_layer_defs.GetFieldCount()
   total = in_layer.GetFeatureCount() * field_count

   # loop create the new layer
   for i in range(0, in_layer.GetFeatureCount()):

       # grab current in_layer feature and define new out_layer feature
       in_feat = in_layer.GetFeature(i);
       out_feat = ogr.Feature(feat_def)

       # change input feature to geometry collection
       # get the geometry, convert to ring..
       geom_poly = in_feat.geometry()
       geom_poly.Transform(coordTrans)
       ring = geom_poly.GetGeometryRef(0)
       line_poly = ogr.Geometry(ogr.wkbMultiLineString)
       line_poly.AddGeometry(ring)


       #... then put in out_layer
       out_feat.SetGeometry(line_poly)
       out_layer.CreateFeature(out_feat)

       # populate the feature field data
       for j in range(0, field_count):
           out_feat.SetField(feat_def.GetFieldDefn(j).GetNameRef(),
                   in_feat.GetField(j))

           progress(i*field_count + j, total, "processed")


       # reset for the next
       out_feat = None
       in_feat = None
       geom_poly = None
       line_poly = None

   # close and reset
   in_layer.ResetReading()
   in_ds = None
   out_ds = None


# apply the function to the two sets
print("\nProcessing MGRS 100km Zones")
PolygonOutlines("MGRS_100km_world.shp", "MGRS_100km_world_outlines.shp", "MGRS_100km_outlines")
print("\nProcessing MGRS Grid Zone Designators (GZD)")
PolygonOutlines("MGRS_GZD_world.shp", "MGRS_GZD_world_outlines.shp", "MGRS_GZD_outlines")


