import numpy as np
import cv2
import math
from scipy import ndimage
from PIL import Image, ImageChops
import os, os.path
import time
import subprocess
from shutil import move

def InitialSetup():
	if os.path.isdir("Crop") == False:
		os.makedirs("Crop")
	if os.path.isdir("Rotate") == False:
		os.makedirs("Rotate")
	if os.path.isdir("Raw") == False:
		os.makedirs("Raw")
	if os.path.isdir("CropRotate") == False:
		os.makedirs("CropRotate")

def RotateImage(image, outputFile):
	img_before = cv2.imread(image)

	#cv2.imshow("Before", img_before)    
	#key = cv2.waitKey(0)

	img_gray = cv2.cvtColor(img_before, cv2.COLOR_BGR2GRAY)
	img_edges = cv2.Canny(img_gray, 100, 100, apertureSize=3)
	lines = cv2.HoughLinesP(img_edges, 1, math.pi / 180.0, 100, minLineLength=100, maxLineGap=5)

	angles = []

	for x1, y1, x2, y2 in lines[0]:
	    cv2.line(img_before, (x1, y1), (x2, y2), 3)
	    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
	    angles.append(angle)

	median_angle = np.median(angles)
	print("Angle is {}".format(median_angle))
	if int(median_angle) in range(-190, -179) or int(median_angle) in range(-100, -79) or int(median_angle) in range(80, 101) or int(median_angle) in range(170, 191) or int(median_angle) in range(-1,5):
		print("Rotating")
		img_rotated = ndimage.rotate(img_before, median_angle)
		cv2.imwrite(outputFile, img_rotated)

def CropImage(image):
	bg = Image.new(image.mode, image.size, image.getpixel((0,0)))
	diff = ImageChops.difference(image, bg)
	diff = ImageChops.add(diff, diff, 2.0, -100)
	bbox = diff.getbbox()
	if bbox:
		return im.crop(bbox)

def ConvertPDF(exeLocation, inputFile, outputFile):
	subprocess.Popen('"%s" -png %s %s' % (exeLocation, inputFile, outputFile)).wait()

InitialSetup()
while True:
	if os.path.isdir("DeleteMe") == False:
		print("Resetting directories...")
		try:
			protected = ["main.py", "Raw", "Crop", "CropRotate", "Rotate", "poppler"]
			for item in os.listdir("Crop"):
				os.remove("Crop/" + item)
			for item in os.listdir("CropRotate"):
				os.remove("CropRotate/" + item)
			for item in os.listdir("Raw"):
				os.remove("Raw/" + item)
			for item in os.listdir("Rotate"):
				os.remove("Rotate/" + item)
			for item in os.listdir("."):
				if item not in protected:
					os.remove(item)
		except Exception as e:
			print(e)
		finally:
			os.makedirs("DeleteMe")
			print("Reset")
	else:
		toCrop = len([name for name in os.listdir('Crop')])
		toRotate = len([name for name in os.listdir('Rotate')])
		toCropAndRotate = len([name for name in os.listdir('CropRotate')])
		try:
			if toCrop > 0:
				print("Found item to crop")
				for item in os.listdir('Crop'):
					if item.lower().endswith(".pdf"):
						print("Converting pdf")
						ConvertPDF(r"..\poppler\bin\pdftoppm.exe", "Crop/" + item, "Crop/" + item.split('.')[0])
						print("Moving " + item + " to raw")
						move("Crop/" + item, "Raw/" + item)
						break
					print("Cropping")
					im = Image.open("Crop/" + item)
					im = CropImage(im)
					im.save(item)
					print("Moving " + item + " to raw")
					move("Crop/" + item, "Raw/" + item)
			if toRotate > 0:
				print("Found item to rotate")
				for item in os.listdir('Rotate'):
					if item.lower().endswith(".pdf"):
						print("Converting pdf")
						ConvertPDF(r"..\poppler\bin\pdftoppm.exe", "Rotate/" + item, "Rotate/" + item.split('.')[0])
						print("Moving " + item + " to raw")
						move("Rotate/" + item, "Raw/" + item)
						break

					RotateImage("Rotate/" + item, item)
					print("Moving " + item + " to raw")
					move("Rotate/" + item, "Raw/" + item)
			if toCropAndRotate > 0:
				print("Found item to crop and rotate")
				for item in os.listdir('CropRotate'):
					if item.lower().endswith(".pdf"):
						print("Converting pdf")
						#subprocess.Popen('"%s" -png %s %s' % (r"C:\Users\wethe\Desktop\DocumentOCR\poppler\bin\pdftoppm.exe", "Crop/" + item, "Crop/" + item.split('.')[0])).wait()
						ConvertPDF(r"..\poppler\bin\pdftoppm.exe", "CropRotate/" + item, "CropRotate/" + item.split('.')[0])
						print("Moving " + item + " to raw")
						move("CropRotate/" + item, "Raw/" + item)
						break

					print("Cropping")
					im = Image.open("CropRotate/" + item)
					im = CropImage(im)
					im.save("cropped.jpg")
					print("Rotating")
					RotateImage("cropped.jpg", item)
					print("Moving " + item + " to raw")
					os.remove("cropped.jpg")
					move("CropRotate/" + item, "Raw/" + item)
		except Exception as e:
			print(e)
	time.sleep(3)



