import os
import inspect
import cv2
import numpy as np
import json
from PIL import Image, ImageDraw, ImageFont
from operator import itemgetter
import subprocess
import util.detection_utils as util

base_dir = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
collage_dir = 'D:/gamestory18-data/collage'
final_dir = 'D:/gamestory18-data/final'
tmp_image_folder = 'D:/gamestory18-data/collage/tmp'
tmp_video_folder = 'D:/gamestory18-data/collage/videos'
tmp_audio_folder = 'D:/gamestory18-data/collage/audio'
killstreak_path = 'D:/gamestory18-data/killstreaks'
killstreak_3_path = os.path.join(killstreak_path, '3')

dest_folder = collage_dir + '/out'
nr_of_frames = 600
W_dest, H_dest = (1280, 720)
resize_factor = 0.95
font_color = (255, 255, 255)

action_label_map = {'3': 'Triple Kill', '4': 'Quad Kill', '5': 'Ace'}


def get_map_sorted_by_round():
    result = {}
    temp = {}
    with open(os.path.join(killstreak_3_path, 'metadata.json'), 'r') as f:
        metadata = json.load(f)
        killstreaks = metadata['killstreaks']
        for nr_killstreaks in killstreaks:
            for video_name in killstreaks[nr_killstreaks]:
                streak = killstreaks[nr_killstreaks][video_name]
                round_nr = streak['round']
                if int(round_nr) not in temp:
                    temp[int(round_nr)] = []

                streak['killstreak_nr'] = nr_killstreaks
                streak['file_name'] = video_name
                temp[int(round_nr)].append(streak)

    for round_nr in sorted(temp):
        result[round_nr] = sorted(temp[int(round_nr)], key=itemgetter('round'))

    return result


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

    draw.text(((W_dest - w) // 4 - 65, 385), txt, fill=font_color, font=font)
    return image


def add_description_right(image, txt):
    fontsize = 25  # starting font size
    font = ImageFont.truetype("arial.ttf", fontsize)

    draw = ImageDraw.Draw(image)
    w, h = draw.textsize(txt, font=font)

    draw.text(((W_dest - w) // 4 * 3 - 80, 635), txt, fill=font_color, font=font)
    return image


def add_image_left(image, image_left):
    resize_factor_left = 0.5
    w_src, h_src = (int(image_left.shape[1] * resize_factor_left), int(image_left.shape[0] * resize_factor_left))

    image_left = cv2.resize(image_left, dsize=(w_src, h_src), interpolation=cv2.INTER_CUBIC)

    height_begin = 200
    height_end = height_begin + h_src

    width_begin = 130
    width_end = width_begin + w_src

    image[height_begin:height_end, width_begin:width_end] = image_left
    return image


def add_image_right(image, image_right):
    w_src, h_src = (int(image_right.shape[1] * resize_factor), int(image_right.shape[0] * resize_factor))

    image_right = cv2.resize(image_right, dsize=(w_src, h_src), interpolation=cv2.INTER_CUBIC)

    height_begin = (H_dest - h_src) // 2 + 100
    height_end = height_begin + h_src

    width_begin = (W_dest - w_src) // 2 + 200
    width_end = width_begin + w_src

    image[height_begin:height_end, width_begin:width_end] = image_right
    return image


def extract_temp_images(src_video_path_left, src_video_path_right, action_label, actor_name):
    cap1 = cv2.VideoCapture(src_video_path_left)
    cap2 = cv2.VideoCapture(src_video_path_right)

    i = 0
    while True:
        image = Image.new('RGB', (W_dest, H_dest))
        image = write_header_teams(image, 'Fnatic vs FaZe Clan')
        image = write_header_action(image, action_label)
        image = add_description_left(image, 'Player View')
        image = add_description_right(image, "Event Stream")

        ret1, image_np1 = cap1.read()
        ret2, image_np2 = cap2.read()

        if image_np1 is None or image_np2 is None:
            break

        image = np.array(image)

        image = add_image_left(image, image_np2)
        image = add_image_right(image, image_np1)

        cv2.imwrite(tmp_image_folder + '/' + str(i) + 'img.png', image)

        i += 1


def summarize_video_for_round(round, sorted_by_match_map):
    if os.path.exists(os.path.join(killstreak_path, '3')):
        total_duration_sec = sum([sorted_by_match_map[round][0]['duration'] for round in sorted_by_match_map])

        killstreak = sorted_by_match_map[round]
        killstreak_length = killstreak[0]['killstreak_nr']
        actor_name = killstreak[0]['actor_name']

        file_name_commentator = killstreak[0]['file_name']
        if 'P11' not in file_name_commentator:
            file_name_commentator = killstreak[1]['file_name']

        file_name_player = killstreak[0]['file_name']
        if 'P11' in file_name_commentator:
            file_name_player = killstreak[1]['file_name']

        # extract tmp images
        src_commentator = killstreak_path + '/' + killstreak_length + '/' + 'P11' + '/' + file_name_commentator
        player_stream = 'P' + killstreak[0]['actor_stream_nr']
        src_player = killstreak_path + '/' + killstreak_length + '/' + player_stream + '/' + file_name_player
        action_label = action_label_map[str(killstreak_length)] + ' by ' + "'" + actor_name + "' at Round " + str(round)

        extract_temp_images(src_commentator, src_player, action_label, actor_name)

        # extract audio file from stream
        # ffmpeg -i 1.mp4 -ab 160k -ac 2 -ar 44100 -vn audio.mp3
        audio_folder = tmp_audio_folder + '/' + str(round) + '.mp3'
        subprocess.call('ffmpeg -i ' + src_commentator + ' -ac 2 -ar 44100 -vn ' + audio_folder, shell=True)

        # merge tmp images together
        # ffmpeg -r 60 -f image2 -s 1280x720 -i img%d.png -i audio.wav -vcodec libx264 -crf 25 -b 4M -vpre normal -pix_fmt yuv420p -acodec copy test.mp4
        subprocess.call(
            'ffmpeg -r 60 -f image2 -s 1280x720 -i ' + tmp_image_folder + '/%dimg.png -i ' + tmp_audio_folder + '/' + str(
                round) + '.mp3 -vcodec libx264 -crf 25 -pix_fmt yuv420p -acodec copy ' + tmp_video_folder + '/' + str(
                round) + '.mp4')

        # cleanup tmp image folder
        cleanup_tmp_folder()


def cleanup_tmp_folder():
    for the_file in os.listdir(tmp_image_folder):
        file_path = os.path.join(tmp_image_folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def summarize_last_round():
    with open(os.path.join(killstreak_3_path, 'metadata.json'), 'r') as f:
        metadata = json.load(f)
        last_rounds = metadata['last_round']

        src_commentator = ''
        src_player = ''
        player_name = ''

        for src_path in last_rounds:
            player_name = last_rounds[src_path]['actor_name']
            if 'P11' in src_path:
                src_commentator = src_path
            else:
                src_player = src_path

        extract_temp_images(src_commentator, src_player, 'Fnatic wins the Tournament', actor_name=player_name)

        # extract audio file from stream
        # ffmpeg -i 1.mp4 -ab 160k -ac 2 -ar 44100 -vn audio.mp3
        audio_folder = tmp_audio_folder + '/99.mp3'
        subprocess.call('ffmpeg -i ' + src_commentator + ' -ac 2 -ar 44100 -vn ' + audio_folder, shell=True)

        # ffmpeg -r 60 -f image2 -s 1280x720 -i img%d.png -i audio.wav -vcodec libx264 -crf 25 -b 4M -vpre normal -pix_fmt yuv420p -acodec copy test.mp4
        subprocess.call(
            'ffmpeg -r 60 -f image2 -s 1280x720 -i ' + tmp_image_folder + '/%dimg.png -i ' + tmp_audio_folder + '/99.mp3 -vcodec libx264 -crf 25 -pix_fmt yuv420p -acodec copy ' + tmp_video_folder + '/99.mp4')

        # cleanup tmp image folder
        cleanup_tmp_folder()


def concat_videos():
    videos_path = os.path.join(collage_dir, 'videos')
    all_files = os.listdir(videos_path)
    all_files_numbers = [int(file.split('.')[0]) for file in all_files if file != 'files.txt']
    all_files_numbers = sorted(all_files_numbers)

    # create List file for ffmpeg concatenation
    with open(os.path.join(videos_path, 'files.txt'), 'w+') as file:
        for file_nr in all_files_numbers:
            line = "file '" + os.path.join(videos_path, str(file_nr) + '.mp4') + "'"
            file.write(line + '\n')

    # concat videos
    # ffmpeg -f concat -safe 0 -i mylist.txt -c copy output
    list_path = os.path.join(videos_path, 'files.txt')
    output_path = os.path.join(final_dir, 'final.mp4')
    subprocess.call('ffmpeg -f concat -safe 0 -i ' + list_path + ' -c copy ' + output_path, shell=True)


def summarize_all():
    sorted_by_match_map = get_map_sorted_by_round()
    for round in sorted_by_match_map:
        summarize_video_for_round(round, sorted_by_match_map)

    summarize_last_round()

summarize_all()

