"""
gif2Asci.py

Author: Miquel Prieto Moline
Version: 0.1
Date: 2025-06-11

Description:
    This script converts a gif file into an ASCII art representation, and prints it into the terminal.

Usage:
    python gif2Asci.py <videoFile> [options]
"""

import argparse
import sys
from os import makedirs
from pathlib import Path
from PIL import Image, ImageSequence
from time import sleep, time


# Constants
OUTPUT_DIR = Path(__file__).parent.parent / "out"  # Directory to store output frames
TIME_PER_FRAME = 0.065  # Time to wait per frame in seconds (15 FPS)
GRAYSCALE_GRADIENTS = ["@%#*+=-:. ", 
                       "██▓▒░  ",
                       "■■▣▩▨▢  "]
GRAYSCALE_CHARS = GRAYSCALE_GRADIENTS[0]  # Default gradient

# Flags
SAVE_ENABLED = False  # Save frames to files instead of printing them


def PrintFrame(asciiImg:list[str]):
    """
    Print the ASCII art representation of the GIF to the terminal.
    Args:
        asciiImg (list[str]): List of strings representing the ASCII art.
    """
    for line in asciiImg:
        print(line)


def GetAverageBrightness(tile:Image.Image) -> int:
    """
    Calculate the average brightness of a tile.
    Args:
        tile (PIL.Image): The image tile to process.
    Returns:
        int: Average brightness value (0-255).
    """
    # Convert the tile to grayscale
    grayscaleTile = tile.convert('L')
    # Get pixel data
    pixels = list(grayscaleTile.getdata())
    # Calculate average brightness
    avgBrightness = sum(pixels) // len(pixels)
    return avgBrightness


def GetFrameData(frame:Image.Image, width:int, scale:float) -> tuple[int, int, float, float, int]:
    """
    Get the dimensions of the frame for processing.
    Args:
        frame (PIL.Image): The image frame to process.
        width (int): Width of the ASCII art output.
        scale (float): Scale factor for height.
    Returns:
        tuple: (tileWidth, tileHeight, height)
    """
    # Get image dimensions
    imgWidth, imgHeight = frame.size[0], frame.size[1]
    print(f"Image size: {imgWidth}x{imgHeight}")
    # Compute width of a tile
    tileWidth = imgWidth / width
    # Compute height of a tile
    tileHeight = tileWidth / scale
    print(f"Tile size: {tileWidth}x{tileHeight}")
    # Compute new height
    height = int(imgHeight/tileHeight)
    print(f"Total height: {height}")

    # Check if the image is too small
    if imgWidth < width or height < 1:
        print("Image is too small to process.")
        exit(1)

    return imgWidth, imgHeight, tileWidth, tileHeight, height


def ProcessFrame(frame:Image.Image, imgWidth:int, imgHeight:int, tileWidth:float, tileHeight:float, width:int, 
                 height:int, inverse:bool) -> list[str]:
    """
    Process a single frame of the GIF and convert it to ASCII art.
    Args:
        frame (PIL.Image): The frame to process.
        imgWidth (int): Width of the original image.
        imgHeight (int): Height of the original image.
        tileWidth (float): Width of each tile in the ASCII art.
        tileHeight (float): Height of each tile in the ASCII art.
        width (int): Width of the ASCII art output.
        scale (float): Scale factor for height.
        inverse (bool): Whether to invert the ASCII gradient.
    """
    # ASCII image generation
    aImg = []

    # Loop through the image pixel windows
    for y in range(0, height):
        y1 = int(y * tileHeight)
        y2 = int((y + 1) * tileHeight)

        # Ensure y2 does not exceed the image height
        if y == height - 1:
            y2 = imgHeight

        aImg.append("")

        for x in range(0, width):
            x1 = int(x * tileWidth)
            x2 = int((x + 1) * tileWidth)

            # Ensure x2 does not exceed the image width
            if x == width - 1:
                x2 = imgWidth

            # Get the pixel data for the current tile
            tile = frame.crop((x1, y1, x2, y2))
            # Get the average brightness of the tile
            avgBrightness = GetAverageBrightness(tile)

            # Map brightness to ASCII character using the whole gradient
            if inverse:
                asciiChar = GRAYSCALE_CHARS[round((1 - (avgBrightness / 255)) * (len(GRAYSCALE_CHARS) - 1))]
            else:
                # Normal mapping
                asciiChar = GRAYSCALE_CHARS[round((avgBrightness / 255) * (len(GRAYSCALE_CHARS) - 1))]
            aImg[y] += asciiChar
    
    return aImg


def SaveFrame(asciiImg:list[str], filename:str, frameNumber:int, writeMode:str = 'a') -> None:
    """
    Save the ASCII art representation of a frame to a file.
    Args:
        asciiImg (list[str]): List of strings representing the ASCII art.
        filename (str): Name of the file to save the ASCII art.
        frameNumber (int): Frame number to save.
        writeMode (str): Mode to open the file.
    """
    # Write/append the ASCII art to a file
    with open(f"{OUTPUT_DIR}/{filename}.txt", writeMode) as f:
        f.write(f"Frame {frameNumber}\n")
        for line in asciiImg:
            f.write(line + '\n')


def ProcessGif(videoPath:str, width:int, scale:float, frameToPrint:int = 0, inverse:bool = False) -> None:
    """
    Process a GIF file converting each frame to an ASCII art representation.
    Args:
        videoPath (str): Path to the GIF file.
        width (int): Width of the ASCII art output.
        scale (float): Scale factor for height.
        inverse (bool): Whether to invert the ASCII characters.
    """
    # Create a directory to store the frames if it doesn't exist
    videoName = videoPath.split('/')[-1].split('.')[0]

    im = Image.open(videoPath)
    imgWidth, imgHeight, tileWidth, tileHeight, height = GetFrameData(im, width, scale)

    if frameToPrint != 0:
        frame = frameToPrint - 1  # Convert to zero-based index
        # If a specific frame is requested, seek to that frame
        if frame < 0 or frame >= im.n_frames: # type: ignore
            print(f"Frame {frameToPrint} is out of range. Total frames: {im.n_frames}") # type: ignore
            exit(1)
        im.seek(frame)
        grayscale = im.convert('L')
        asciiImg = ProcessFrame(grayscale, imgWidth, imgHeight, tileWidth, tileHeight, width, height, inverse)
        PrintFrame(asciiImg) if not SAVE_ENABLED else SaveFrame(asciiImg, videoName, frame, 'w')
    
    else:
        prevTime = time()
        # Process each frame of the GIF
        for frame in ImageSequence.Iterator(im):

            currentTime = time()
            deltaTime = currentTime - prevTime
            prevTime = currentTime

            print(f"Frame number: {frame.tell()}")
            
            grayscale = frame.convert('L')
            asciiImg = ProcessFrame(grayscale, imgWidth, imgHeight, tileWidth, tileHeight, width, height, inverse)
            
            if SAVE_ENABLED:
                SaveFrame(asciiImg, videoName, frame.tell(), 'a')
            else:
                PrintFrame(asciiImg)
                if frame.tell() != im.n_frames - 1: # type: ignore
                    sys.stdout.write(f"\033[{len(asciiImg) + 1}A")  # Move cursor up to overwrite the previous frame

            if deltaTime < TIME_PER_FRAME:
                sleep(TIME_PER_FRAME - deltaTime)  # Sleep to maintain frame rate


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert a gif file into ASCII art.')
    parser.add_argument('video_file', type=str, help='Path to the video file to convert.')
    parser.add_argument('-w', '--width', type=int, default=80, help='Width of the ASCII art output (default: 80).')
    parser.add_argument('-s', '--scale', type=float, default=0.5, help='Scale factor for height (default: 0.42).')
    parser.add_argument('-i', '--inverse', action='store_true', help='Invert the ASCII characters (default: False).')
    parser.add_argument('-g', '--gradient', type=int, default=0, choices=[0, 1, 2])
    parser.add_argument('-f', '--frame', type=int, default=0, help='Frame to print in a non-zero index. If not '
                        'specified, all frames will be printed one after the other.')
    parser.add_argument('-sv', '--save', action='store_true', 
                        help='Save the ASCII art frames to a file instead of printing them.')
    
    args = parser.parse_args()
    
    # Placeholder for video processing logic
    print(f"Converting {args.video_file} to ASCII art with dimensions {args.width}x{args.scale}.")

    # Create output directory if it doesn't exist 
    makedirs(OUTPUT_DIR, exist_ok=True)

    # Set the grayscale gradient based on user input
    GRAYSCALE_CHARS = GRAYSCALE_GRADIENTS[args.gradient]
    SAVE_ENABLED = args.save

    ProcessGif(args.video_file, args.width, args.scale, args.frame, args.inverse)
