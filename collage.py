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



def write_header_teams(image, txt):
    img_fraction = 0.25
    fontsize = 1  # starting font size
    font = ImageFont.truetype("arial.ttf", fontsize)

    # portion of image width you want text width to be
    while font.getsize(txt)[0] < img_fraction * image.size[0]:
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        font = ImageFont.truetype("arial.ttf", fontsize)

    # optionally de-increment to be sure it is less than criteria
    fontsize -= 1

    draw = ImageDraw.Draw(image)
    w, h = draw.textsize(txt, font=font)

    draw.text(((W_dest - w) / 2, 20), txt, fill=(255, 0, 0), font=font)
    return image


def write_header_round(image, round):
    txt = 'Round ' + round
    img_fraction = 0.10
    fontsize = 1  # starting font size
    font = ImageFont.truetype("arial.ttf", fontsize)

    # portion of image width you want text width to be
    while font.getsize(txt)[0] < img_fraction * image.size[0]:
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        font = ImageFont.truetype("arial.ttf", fontsize)

    # optionally de-increment to be sure it is less than criteria
    fontsize -= 1

    draw = ImageDraw.Draw(image)
    w, h = draw.textsize(txt, font=font)

    draw.text(((W_dest - w) / 2, 60), txt, fill=(255, 0, 0), font=font)
    return image

def write_header_action(image, action):
    if action == 3:
        txt = 'Triple-Kill'
    elif action == 4:
        txt = 'Quad-Kill'
    else:
        txt = action

    img_fraction = 0.10
    fontsize = 1  # starting font size
    font = ImageFont.truetype("arial.ttf", fontsize)

    # portion of image width you want text width to be
    while font.getsize(txt)[0] < img_fraction * image.size[0]:
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        font = ImageFont.truetype("arial.ttf", fontsize)

    # optionally de-increment to be sure it is less than criteria
    fontsize -= 1

    draw = ImageDraw.Draw(image)
    w, h = draw.textsize(txt, font=font)

    draw.text(((W_dest - w) / 2, 95), txt, fill=(255, 0, 0), font=font)
    return image


def add_image_left(image, image_left):
    w_src, h_src = (640, 360)
    height_begin = (H_dest - h_src) // 2
    height_end = height_begin + h_src
    image[height_begin:height_end, 0:640] = image_left
    return image

def add_image_right(image, image_right):
    w_src, h_src = (640, 360)
    height_begin = (H_dest - h_src) // 2
    height_end = height_begin + h_src
    image[height_begin:height_end, 640:1280] = image_right
    return image


i = 0
while True:
    image = Image.new('RGB', (W_dest, H_dest))
    image = write_header_teams(image, 'Fnatic vs FaZeClan')
    image = write_header_round(image, '41')
    image = write_header_action(image, 4)

    ret1, image_np1 = cap1.read()
    ret2, image_np2 = cap2.read()

    image = np.array(image)

    image = add_image_left(image, image_np1)
    image = add_image_right(image, image_np2)


    cv2.imwrite(dest_folder + '/' + str(i) + 'img.png', image)

    i += 1
    if not ret1 or not ret2 or i >= 100:
        break












