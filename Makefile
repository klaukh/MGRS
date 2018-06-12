
all: MGRS

MGRS: gzd zones labels outlines

gzd:
	gzip -d MGRS_GZD.tar.gz
	7z e MGRS_GZD.tar

zones:
	7z e -oMGRS_100km MGRS_100km_1_20.tar
	7z e -oMGRS_100km MGRS_100km_21_40.tar
	7z e -oMGRS_100km MGRS_100km_41_60.tar
	for shp in MGRS_100km/*.shp ; do \
		echo $$shp ; \
		ogr2ogr -append -update -t_srs EPSG:3857 -wrapdateline MGRS_100km_world_tmp.shp $$shp ; \
	done
	ogr2ogr -t_srs EPSG:3857 MGRS_100km_world.shp MGRS_100km_world_tmp.shp
	rm MGRS_100km_world_tmp.*
	rmdir /S MGRS_100km

labels:
	py labels.py

outlines:
	py outlines.py


clean:
	rm -f MGRS_100km/
	rm MGRS_100km_world_tmp.*

