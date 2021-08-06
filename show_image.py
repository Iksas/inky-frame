#!/usr/bin/env python

"""
Displays the image that is passed as the first argument to this script.

If a folder is passed as an argument, all images in the folder are searched 
recursively, and a random image is picked and displayed.

"""

import argparse
import os
import random
from PIL import Image
from inky.inky_uc8159 import Inky



""" Returns a list of all images in the path.
	It's assumed that the path exists.
"""
def returnImagesInPath(path):
	if os.path.isdir(path):
		imagePaths = []
		
		for path,dirs,files in os.walk(path):
			for filename in files:
				if filename.lower()[-4:] in [".jpg", ".png", "jpeg"]:
					imagePaths.append(os.path.join(path, filename))
		
		return imagePaths
		
	elif path.lower()[-4:] in [".jpg", ".png", "jpeg"]:
		return [path]
	else:
		return []


""" Receives a list of image file paths, chooses a random image,
	makes some color adjustments and displays the image.
"""
def displayRandomImage(imageList):
	limit = len(imageList)
	index = random.randrange(0, len(imageList))
	
	imagePath = imageList[index]
	
	print("Displaying {}".format(imagePath))
	
	inky = Inky()
	saturation = 0.5

	image = Image.open(imagePath)

	inky.set_image(image, saturation=saturation)
	inky.show()
	
	print("Done.")
	

""" Returns an error if the string is not a valid path
"""
def dir_path(string):
    if os.path.exists(string):
        return string
    else:
        raise NotADirectoryError(string)


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-p ", "--path", type=dir_path, required=True)
	arguments = parser.parse_args()
	
	images = returnImagesInPath(arguments.path)
	
	displayRandomImage(images)

