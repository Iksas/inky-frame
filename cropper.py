#!/usr/bin/env python3

import sys
import os
import pygame
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image  # install the "Pillow" package to use PIL

# TODO: better handling of images that can't be read

# disable DoS warning
Image.MAX_IMAGE_PIXELS = None

DEFAULT_WIDTH = "600"
DEFAULT_HEIGHT = "448"


class FolderCropper:
    def __init__(self):
        self.sourceFolder = None
        self.destFolder = None

        self.targetWidth = None
        self.targetHeight = None

        window = tk.Tk()
        window.title("cropper")
        window.minsize(450, 150)

        label1 = ttk.Label(window, text="Source Folder: ")
        label1.grid(column=0, row=1)
        label2 = ttk.Label(window, text="Destination Folder: ")
        label2.grid(column=0, row=2)
        label3 = ttk.Label(window, text="Width: ")
        label3.grid(column=0, row=3)
        label4 = ttk.Label(window, text="Height: ")
        label4.grid(column=0, row=4)

        def setSourceFolder():
            self.sourceFolder = filedialog.askdirectory(initialdir=sys.argv[0])
            sourceFolderField.config(state="normal")
            sourceFolderField.delete(0, tk.END)
            sourceFolderField.insert(0, self.sourceFolder)
            sourceFolderField.config(state="readonly")
            return

        def setDestFolder():
            self.destFolder = filedialog.askdirectory(initialdir=sys.argv[0])
            destFolderField.config(state="normal")
            destFolderField.delete(0, tk.END)
            destFolderField.insert(0, self.destFolder)
            destFolderField.config(state="readonly")
            return

        def runCommand():
            try:
                self.sourceFolder = sourceFolderField.get()
                self.destFolder = destFolderField.get()
                self.targetHeight = int(heightTextField.get())
                self.targetWidth = int(widthTextField.get())

                assert self.sourceFolder != ""
                assert self.destFolder != ""

            except Exception as e:
                print(e)
                messagebox.showwarning("Error", "Invalid input.")
                return

            window.destroy()
            self.cropAllImages()

        sourceFolderField = ttk.Entry(window, state="readonly")
        sourceFolderField.grid(column=1, row=1)
        destFolderField = ttk.Entry(window, state="readonly")
        destFolderField.grid(column=1, row=2)
        widthTextField = ttk.Entry(window, width=6)
        widthTextField.insert(0, DEFAULT_WIDTH)
        widthTextField.grid(column=1, row=3)
        heightTextField = ttk.Entry(window, width=6)
        heightTextField.insert(0, DEFAULT_HEIGHT)
        heightTextField.grid(column=1, row=4)

        sourceButton = ttk.Button(window, text="Browse...", command=lambda: setSourceFolder())
        sourceButton.grid(column=2, row=1)
        destButton = ttk.Button(window, text="Browse...", command=lambda: setDestFolder())
        destButton.grid(column=2, row=2)

        runButton = ttk.Button(window, text="Run", command=lambda: runCommand())
        runButton.grid(column=2, row=5)

        window.mainloop()
        exit(0)

    def cropAllImages(self):
        imagesToProcess = []

        for filename in os.listdir(self.sourceFolder):
            filePath = os.path.join(self.sourceFolder, filename)

            if os.path.isfile(filePath) and filePath[-4:].lower() in [".png", ".jpg"]:
                imagesToProcess.append((filePath, os.path.join(self.destFolder, filename)))

        for pair in imagesToProcess:
            if not os.path.exists(pair[1]):
                ic = ImageCropper(pair[0])
                ic.interactive_crop(pair[1], self.targetWidth, self.targetHeight)
            else:
                print("{} has been skipped because {} already exists".format(pair[0], pair[1]))

        exit(0)


class ImageCropper:
    def __init__(self, imagePath):
        self.imagePath = imagePath
        self.image = Image.open(imagePath)

        self.savePath = None
        self.targetWidth = None
        self.targetHeight = None

    # print("Opened Image of size {}x{}".format(self.image.width, self.image.height))

    def interactive_crop(self, savePath, targetWidth, targetHeight):
        self.savePath = savePath
        self.targetWidth = targetWidth
        self.targetHeight = targetHeight

        wfactor = self.image.width / targetWidth
        hfactor = self.image.height / targetHeight

        if (wfactor / hfactor) > 1:
            # the height doesn't need cropping
            cropMode = "horizontal"
            displayHeight = targetHeight
            displayWidth = displayHeight * self.image.width // self.image.height
            cropMargin = (displayWidth - targetWidth) // 2

            # the image has to be filled vertically to expand it
            fillMode = "vertical"
            fillWidth = targetWidth
            fillHeight = fillWidth * self.image.height // self.image.width
            fillMargin = (targetHeight - fillHeight) // 2
        else:
            # the width doesn't need cropping
            cropMode = "vertical"
            displayWidth = targetWidth
            displayHeight = displayWidth * self.image.height // self.image.width
            cropMargin = (displayHeight - targetHeight) // 2

            # the image has to be filled horizontally to expand it
            fillMode = "horizontal"
            fillHeight = targetHeight
            fillWidth = fillHeight * self.image.width // self.image.height
            fillMargin = (targetWidth - fillWidth) // 2

        pygame.init()
        pygame.display.set_caption('cropper')
        clock = pygame.time.Clock()
        pg_image = pygame.image.load(self.imagePath)
        crop_image = pygame.transform.scale(pg_image, (displayWidth, displayHeight))
        fill_image = pygame.transform.scale(pg_image, (fillWidth, fillHeight))

        screen = pygame.display.set_mode(size=(displayWidth, displayHeight))
        screen.fill((0, 0, 0))

        frames = 0
        mouseDown = False
        rectColor = [255, 0, 0]
        color = (0, 0, 0)
        displayMode = "vcenter" if cropMode == "vertical" else "hcenter"

        while True:

            frames += 1
            if frames > 5:
                frames = 0
                rectColor = [255, 0, 0] if rectColor == [255, 255, 0] else [255, 255, 0]

            # render the preview
            if displayMode == "fill":
                screen.fill(color)

                if fillMode == "vertical":
                    imagePosition = (0, fillMargin)
                else:
                    imagePosition = (fillMargin, 0)

                screen.blit(fill_image, imagePosition)
            else:
                screen.blit(crop_image, [0, 0])

                if displayMode == "hcenter":
                    imagePosition = (cropMargin, 0)
                elif displayMode == "left":
                    imagePosition = (0, 0)
                elif displayMode == "right":
                    imagePosition = (2 * cropMargin, 0)
                elif displayMode == "vcenter":
                    imagePosition = (0, cropMargin)
                elif displayMode == "up":
                    imagePosition = (0, 0)
                elif displayMode == "down":
                    imagePosition = (0, 2 * cropMargin)
                else:
                    imagePosition = (0, 0)

                pygame.draw.rect(screen, rectColor, [imagePosition[0], imagePosition[1],
                                                     targetWidth, targetHeight], width=3)

            # handle events
            oldDisplayMode = displayMode
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:

                        if displayMode == "fill":
                            self.save((fillWidth, fillHeight), imagePosition, color)
                        else:
                            self.save((displayWidth, displayHeight),
                                      (-imagePosition[0], -imagePosition[1]))

                        pygame.quit()
                        return
                    elif event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_RIGHT and cropMode == "horizontal":
                        displayMode = "right" if displayMode in ["hcenter", "right"] else "hcenter"
                    elif event.key == pygame.K_LEFT and cropMode == "horizontal":
                        displayMode = "left" if displayMode in ["hcenter", "left"] else "hcenter"
                    elif event.key == pygame.K_UP and cropMode == "vertical":
                        displayMode = "up" if displayMode in ["vcenter", "up"] else "vcenter"
                    elif event.key == pygame.K_DOWN and cropMode == "vertical":
                        displayMode = "down" if displayMode in ["vcenter", "down"] else "vcenter"
                    elif event.key == pygame.K_w:
                        displayMode = "fill"
                        color = (255, 255, 255)
                    elif event.key == pygame.K_b:
                        displayMode = "fill"
                        color = (0, 0, 0)
                if event.type == pygame.MOUSEBUTTONUP:
                    mouseDown = False
                    position = pygame.mouse.get_pos()
                    color = screen.get_at(position)
                    displayMode = "fill"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouseDown = True

            if displayMode == "fill" and mouseDown is True:
                position = pygame.mouse.get_pos()
                color = screen.get_at(position)

            pygame.display.flip()
            clock.tick(20)

            # set new display mode only if the mode changed
            if displayMode != oldDisplayMode:
                if displayMode == "fill":
                    screen = pygame.display.set_mode(size=(targetWidth, targetHeight))
                else:
                    screen = pygame.display.set_mode(size=(displayWidth, displayHeight))

    def save(self, imageSize, imagePosition, color=(0, 0, 0)):
        self.image = self.image.resize(imageSize, Image.LANCZOS)
        output = Image.new("RGB", (self.targetWidth, self.targetHeight), color[:3])
        output.paste(self.image, imagePosition)
        output.save(self.savePath)


if __name__ == "__main__":
    fc = FolderCropper()
