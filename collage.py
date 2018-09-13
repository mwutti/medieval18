import os
import inspect
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

base_dir = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
collage_dir = 'D:/gamestory18-data/collage/test'

cap1 = cv2.VideoCapture(collage_dir + '/P11/1.mp4')
cap2 = cv2.VideoCapture(collage_dir + '/PN/1.mp4')
dest_folder = collage_dir + '/out'
nr_of_frames = 600
W_dest, H_dest = (1280, 720)
resize_factor = 0.95
font_color = (255, 255, 255)


def write_header_teams(image, txt):
    fontsize = 50  # starting font size
    font = ImageFont.truetype("arial.ttf", fontsize)


    draw = ImageDraw.Draw(image)
    w, h = draw.textsize(txt, font=font)

    draw.text(((W_dest - w) / 2, 40), txt, fill=font_color, font=font)
    return image


def write_header_action(image, txt):
    fontsize = 35  # starting font size
    font = ImageFont.truetype("arial.ttf", fontsize)

    draw = ImageDraw.Draw(image)
    w, h = draw.textsize(txt, font=font)

    draw.text(((W_dest - w) / 2, 100), txt, fill=font_color, font=font)
    return image


def add_description_left(image, txt):
    fontsize = 25  # starting font size
    font = ImageFont.truetype("arial.ttf", fontsize)

    draw = ImageDraw.Draw(image)
    w, h = draw.textsize(txt, font=font)

    draw.text(((W_dest - w) // 4 - 30, 540), txt, fill=font_color, font=font)
    return image


def add_description_right(image, txt):

    fontsize = 25  # starting font size
    font = ImageFont.truetype("arial.ttf", fontsize)

    draw = ImageDraw.Draw(image)
    w, h = draw.textsize(txt, font=font)

    draw.text(((W_dest - w ) // 4 * 3 + 30, 540), txt, fill=font_color, font=font)
    return image


def add_image_left(image, image_left):
    w_before, h_before = image_left.shape[1], image_left.shape[0]
    w_src, h_src = (int(image_left.shape[1] * resize_factor), int(image_left.shape[0] * resize_factor))

    image_left = cv2.resize(image_left, dsize=(w_src, h_src), interpolation=cv2.INTER_CUBIC)

    height_begin = (H_dest - h_src) // 2
    height_end = height_begin + h_src

    width_begin = (w_before - w_src) // 2
    width_end = width_begin + w_src

    image[height_begin:height_end, width_begin:width_end] = image_left
    return image


def add_image_right(image, image_right):
    w_before, h_before = image_right.shape[1], image_right.shape[0]
    w_src, h_src = (int(image_right.shape[1] * resize_factor), int(image_right.shape[0] * resize_factor))

    image_right = cv2.resize(image_right, dsize=(w_src, h_src), interpolation=cv2.INTER_CUBIC)

    height_begin = (H_dest - h_src) // 2
    height_end = height_begin + h_src

    width_begin = (W_dest // 2) + (w_before - w_src) // 2
    width_end = width_begin + w_src

    image[height_begin:height_end, width_begin:width_end] = image_right
    return image


i = 0
while True:
    image = Image.new('RGB', (W_dest, H_dest))
    image = write_header_teams(image, 'Fnatic vs FaZe Clan')
    image = write_header_action(image, 'Quad-Kill: Round 12')
    image = add_description_left(image, 'Event Stream')
    image = add_description_right(image, 'Actor: Niko')

    ret1, image_np1 = cap1.read()
    ret2, image_np2 = cap2.read()

    image = np.array(image)

    image = add_image_left(image, image_np1)
    image = add_image_right(image, image_np2)


    cv2.imwrite(dest_folder + '/' + str(i) + 'img.png', image)

    i += 1
    if not ret1 or not ret2:
        break












