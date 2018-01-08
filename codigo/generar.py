#!/usr/bin/python
#! -*- encoding: utf-8 -*-


OPENMVG_SFM_BIN = "/home/juanjo/openMVG_Build/Linux-x86_64-RELEASE"

CAMERA_SENSOR_WIDTH_DIRECTORY = "/home/juanjo/openMVG/src/software/SfM" + "/../../openMVG/exif/sensor_width_database"

input_dir = "/home/juanjo/Escritorio/grafica/entrada/"#entrada
output_dir ="/home/juanjo/Escritorio/grafica/salida/"#salida

import os
import subprocess
import sys
import cv2
import time

def generar_imagenes(mirror=False):
	i=0;
	cam = cv2.VideoCapture(0)

	while True:
		ret_val, img = cam.read()
		if mirror: 
			img = cv2.flip(img, 1)
		#cv2.imshow('Web Cam', img)
		cv2.imwrite(os.path.join(input_dir,"img%d.jpg"%i),img)
		if cv2.waitKey(1) == 27:		
			break  # esc para salir
		i=i+1
		time.sleep(1)
	cv2.destroyAllWindows()
		
	
def reconstruccion_3d():
	
	
	matches_dir = os.path.join(output_dir, "matches")
	reconstruction_dir = os.path.join(output_dir, "reconstruction_sequential")
	camera_file_params = os.path.join(CAMERA_SENSOR_WIDTH_DIRECTORY, "sensor_width_camera_database.txt")

	print ("Using input dir  : ", input_dir)
	print ("      output_dir : ", output_dir)

	#Se crean las carpetas si no estan presentes
	if not os.path.exists(output_dir):
	  os.mkdir(output_dir)
	if not os.path.exists(matches_dir):
	  os.mkdir(matches_dir)

	print ("1. Intrinsics analysis")
	pIntrisics = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfMInit_ImageListing"),  "-i", input_dir, "-o", matches_dir, "-d", camera_file_params,"-f","140"] )
	pIntrisics.wait()

	print ("2. Compute features")
	pFeatures = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeFeatures"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir, "-m", "SIFT"] )
	pFeatures.wait()

	print ("3. Compute matches")
	pMatches = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeMatches"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir] )
	pMatches.wait()

	if not os.path.exists(reconstruction_dir):
	    os.mkdir(reconstruction_dir)

	print ("4. Do Sequential/Incremental reconstruction")
	pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_IncrementalSfM"),  "-i", matches_dir+"/sfm_data.json", "-m", matches_dir, "-o", reconstruction_dir] )
	pRecons.wait()

	print ("5. Colorize Structure")
	pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"),  "-i", reconstruction_dir+"/sfm_data.bin", "-o", os.path.join(reconstruction_dir,"colorized.ply")] )
	pRecons.wait()

	# optional, compute final valid structure from the known camera poses
	print ("6. Structure from Known Poses (robust triangulation)")
	pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeStructureFromKnownPoses"),  "-i", reconstruction_dir+"/sfm_data.bin", "-m", matches_dir, "-f", os.path.join(matches_dir, "matches.f.bin"), "-o", os.path.join(reconstruction_dir,"robust.bin")] )
	pRecons.wait()

	pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"),  "-i", reconstruction_dir+"/robust.bin", "-o", os.path.join(reconstruction_dir,"robust_colorized.ply")] )
	pRecons.wait()


if __name__ == '__main__':
	#generar_imagenes(mirror=True)
	reconstruccion_3d()
