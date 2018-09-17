import os
import inspect
import cv2
import numpy as np
import json
from PIL import Image, ImageDraw, ImageFont
from operator import itemgetter
import subprocess


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

def write_header_action(image, txt):
    fontsize = 35  # starting font size
    font = ImageFont.truetype("arial.ttf", fontsize)

    draw = ImageDraw.Draw(image)
    w, h = draw.textsize(txt, font=font)

    draw.text(((W_dest - w) / 2, 35), txt, fill=font_color, font=font)
    return image


def add_description_event_stream(image, txt='Event Stream'):
    fontsize = 20  # starting font size
    font = ImageFont.truetype("arial.ttf", fontsize)

    draw = ImageDraw.Draw(image)
    w, h = draw.textsize(txt, font=font)

    draw.text(((W_dest - w) // 4 - 80, 375), txt, fill=font_color, font=font)
    return image


def add_description_player_one(image, txt=''):
    fontsize = 25  # starting font size
    txt = "'" + txt + "'"
    font = ImageFont.truetype("arial.ttf", fontsize)

    draw = ImageDraw.Draw(image)
    w, h = draw.textsize(txt, font=font)

    draw.text(((W_dest - w) // 4 - 65, 685), txt, fill=font_color, font=font)
    return image

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


def add_image_one(image, image_left):
    resize_factor = 0.75
    w_src, h_src = (int(image_left.shape[1] * resize_factor), int(image_left.shape[0] * resize_factor))

    image_left = cv2.resize(image_left, dsize=(w_src, h_src), interpolation=cv2.INTER_CUBIC)

    height_begin = 100
    height_end = height_begin + h_src

    width_begin = 30
    width_end = width_begin + w_src

    image[height_begin:height_end, width_begin:width_end] = image_left
    return image


def add_image_two(image, image_left):
    resize_factor = 0.75
    w_src, h_src = (int(image_left.shape[1] * resize_factor), int(image_left.shape[0] * resize_factor))

    image_left = cv2.resize(image_left, dsize=(w_src, h_src), interpolation=cv2.INTER_CUBIC)

    height_begin = 410
    height_end = height_begin + h_src

    width_begin = 30
    width_end = width_begin + w_src

    image[height_begin:height_end, width_begin:width_end] = image_left
    return image


def add_image_three(image, image_left):
    resize_factor = 0.5
    w_src, h_src = (int(image_left.shape[1] * resize_factor), int(image_left.shape[0] * resize_factor))

    image_left = cv2.resize(image_left, dsize=(w_src, h_src), interpolation=cv2.INTER_CUBIC)

    height_begin = 100
    height_end = height_begin + h_src

    width_begin = 550
    width_end = width_begin + w_src

    image[height_begin:height_end, width_begin:width_end] = image_left
    return image


def add_image_four(image, image_left):
    resize_factor = 0.5
    w_src, h_src = (int(image_left.shape[1] * resize_factor), int(image_left.shape[0] * resize_factor))

    image_left = cv2.resize(image_left, dsize=(w_src, h_src), interpolation=cv2.INTER_CUBIC)

    height_begin = 100
    height_end = height_begin + h_src

    width_begin = 920
    width_end = width_begin + w_src

    image[height_begin:height_end, width_begin:width_end] = image_left
    return image


def add_image_five(image, image_left):
    resize_factor = 0.5
    w_src, h_src = (int(image_left.shape[1] * resize_factor), int(image_left.shape[0] * resize_factor))

    image_left = cv2.resize(image_left, dsize=(w_src, h_src), interpolation=cv2.INTER_CUBIC)

    height_begin = 300
    height_end = height_begin + h_src

    width_begin = 920
    width_end = width_begin + w_src

    image[height_begin:height_end, width_begin:width_end] = image_left
    return image


def add_image_six(image, image_left):
    resize_factor = 0.5
    w_src, h_src = (int(image_left.shape[1] * resize_factor), int(image_left.shape[0] * resize_factor))

    image_left = cv2.resize(image_left, dsize=(w_src, h_src), interpolation=cv2.INTER_CUBIC)

    height_begin = 300
    height_end = height_begin + h_src

    width_begin = 550
    width_end = width_begin + w_src

    image[height_begin:height_end, width_begin:width_end] = image_left
    return image


def add_image_seven(image, image_left):
    resize_factor = 0.5
    w_src, h_src = (int(image_left.shape[1] * resize_factor), int(image_left.shape[0] * resize_factor))

    image_left = cv2.resize(image_left, dsize=(w_src, h_src), interpolation=cv2.INTER_CUBIC)

    height_begin = 500
    height_end = height_begin + h_src

    width_begin = 920
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


def do_for_5_killstreak(cap1, cap2, cap_v_1, cap_v_2, cap_v_3, cap_v_4, cap_v_5, action_label=None):
    i = 0
    while True:
        image = Image.new('RGB', (W_dest, H_dest))

        ret1, image_np1 = cap1.read()
        ret2, image_np2 = cap2.read()

        ret_v_1, image_v_1 = cap_v_1.read()
        ret_v_2, image_v_2 = cap_v_2.read()
        ret_v_3, image_v_3 = cap_v_3.read()
        ret_v_4, image_v_4 = cap_v_4.read()
        ret_v_5, image_v_5 = cap_v_5.read()

        if image_np1 is None or image_np2 is None or image_v_1 is None or \
                image_v_2 is None or image_v_3 is None or image_v_4 is None or image_v_5 is None:
            break

        image = write_header_action(image, action_label)
        image = add_description_event_stream(image)
        image = add_description_player_one(image, action_label.split("'")[1])
        image = np.array(image)

        if image_np1 is not None:
            image = add_image_one(image, image_np1)

        if image_np2 is not None:
            image = add_image_two(image, image_np2)

        if image_v_1 is not None:
            image = add_image_three(image, image_v_1)

        if image_v_2 is not None:
            image = add_image_four(image, image_v_2)

        if image_v_3 is not None:
            image = add_image_five(image, image_v_3)

        if image_v_4 is not None:
            image = add_image_six(image, image_v_4)

        if image_v_5 is not None:
            image = add_image_seven(image, image_v_5)

        cv2.imwrite(tmp_image_folder + '/' + str(i) + 'img.png', image)

        i += 1


def do_for_4_killstreak(cap1, cap2, cap_v_1, cap_v_2, cap_v_3, cap_v_4, action_label=None):
    i = 0
    while True:
        image = Image.new('RGB', (W_dest, H_dest))

        ret1, image_np1 = cap1.read()
        ret2, image_np2 = cap2.read()

        ret_v_1, image_v_1 = cap_v_1.read()
        ret_v_2, image_v_2 = cap_v_2.read()
        ret_v_3, image_v_3 = cap_v_3.read()
        ret_v_4, image_v_4 = cap_v_4.read()

        if image_np1 is None or image_np2 is None or image_v_1 is None or \
                image_v_2 is None or image_v_3 is None or image_v_4 is None:
            break

        image = write_header_action(image, action_label)
        image = add_description_event_stream(image)
        image = add_description_player_one(image, action_label.split("'")[1])
        image = np.array(image)
        if image_np1 is not None:
            image = add_image_one(image, image_np1)

        if image_np2 is not None:
            image = add_image_two(image, image_np2)

        if image_v_1 is not None:
            image = add_image_three(image, image_v_1)

        if image_v_2 is not None:
            image = add_image_four(image, image_v_2)

        if image_v_3 is not None:
            image = add_image_five(image, image_v_3)

        if image_v_4 is not None:
            image = add_image_six(image, image_v_4)

        cv2.imwrite(tmp_image_folder + '/' + str(i) + 'img.png', image)

        i += 1


def do_for_3_killstreak(cap1, cap2, cap_v_1, cap_v_2, cap_v_3, action_label=None):
    i = 0
    while True:
        image = Image.new('RGB', (W_dest, H_dest))

        ret1, image_np1 = cap1.read()
        ret2, image_np2 = cap2.read()

        ret_v_1, image_v_1 = cap_v_1.read()
        ret_v_2, image_v_2 = cap_v_2.read()
        ret_v_3, image_v_3 = cap_v_3.read()

        if image_np1 is None or image_np2 is None or image_v_1 is None or \
                image_v_2 is None or image_v_3 is None:
            break

        image = write_header_action(image, action_label)
        image = add_description_event_stream(image)
        image = add_description_player_one(image, action_label.split("'")[1])
        image = np.array(image)
        if image_np1 is not None:
            image = add_image_one(image, image_np1)

        if image_np2 is not None:
            image = add_image_two(image, image_np2)

        if image_v_1 is not None:
            image = add_image_three(image, image_v_1)

        if image_v_2 is not None:
            image = add_image_four(image, image_v_2)

        if image_v_3 is not None:
            image = add_image_five(image, image_v_3)

        cv2.imwrite(tmp_image_folder + '/' + str(i) + 'img.png', image)

        i += 1


def extract_temp_images(src_video_path_0, src_video_1, src_video_path_victim_1,
                        src_video_path_victim_2,
                        src_video_path_victim_3,
                        src_video_path_victim_4=None,
                        src_video_path_victim_5=None, action_label=''):

    cap0 = cv2.VideoCapture(src_video_path_0)
    cap1 = cv2.VideoCapture(src_video_1)

    cap_v_1 = cv2.VideoCapture(src_video_path_victim_1)
    cap_v_2 = cv2.VideoCapture(src_video_path_victim_2)
    cap_v_3 = cv2.VideoCapture(src_video_path_victim_3)
    cap_v_4 = None
    cap_v_5 = None

    if src_video_path_victim_4 is not None:
        cap_v_4 = cv2.VideoCapture(src_video_path_victim_4)

    if src_video_path_victim_5 is not None:
        cap_v_5 = cv2.VideoCapture(src_video_path_victim_5)
        do_for_5_killstreak(cap0, cap1, cap_v_1, cap_v_2, cap_v_3, cap_v_4, cap_v_5, action_label=action_label)
        return

    if src_video_path_victim_4 is not None:
        do_for_4_killstreak(cap0, cap1, cap_v_1, cap_v_2, cap_v_3, cap_v_4, action_label=action_label)
        return

    do_for_3_killstreak(cap0, cap1, cap_v_1, cap_v_2, cap_v_3,  action_label=action_label)


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

        victim_base_base = killstreak_path + '/' + killstreak_length + '/'

        if killstreak_length == '5':
            extract_temp_images(src_commentator, src_player,
                                victim_base_base + killstreak[2]['file_name'].split('.')[0].split('_')[-1] + '/' + killstreak[2]['file_name'],
                                victim_base_base + killstreak[3]['file_name'].split('.')[0].split('_')[-1] + '/' + killstreak[3]['file_name'],
                                victim_base_base + killstreak[4]['file_name'].split('.')[0].split('_')[-1] + '/' + killstreak[4]['file_name'],
                                victim_base_base + killstreak[5]['file_name'].split('.')[0].split('_')[-1] + '/' + killstreak[5]['file_name'],
                                victim_base_base + killstreak[6]['file_name'].split('.')[0].split('_')[-1] + '/' + killstreak[6]['file_name'], action_label=action_label)

        if killstreak_length == '4':
            extract_temp_images(src_commentator, src_player,
                                victim_base_base + killstreak[2]['file_name'].split('.')[0].split('_')[-1] + '/' +
                                killstreak[2]['file_name'],
                                victim_base_base + killstreak[3]['file_name'].split('.')[0].split('_')[-1] + '/' +
                                killstreak[3]['file_name'],
                                victim_base_base + killstreak[4]['file_name'].split('.')[0].split('_')[-1] + '/' +
                                killstreak[4]['file_name'],
                                victim_base_base + killstreak[5]['file_name'].split('.')[0].split('_')[-1] + '/' +
                                killstreak[5]['file_name'], action_label=action_label)
        if killstreak_length == '3':
            extract_temp_images(src_commentator, src_player,
                                victim_base_base + killstreak[2]['file_name'].split('.')[0].split('_')[-1] + '/' +
                                killstreak[2]['file_name'],
                                victim_base_base + killstreak[3]['file_name'].split('.')[0].split('_')[-1] + '/' +
                                killstreak[3]['file_name'],
                                victim_base_base + killstreak[4]['file_name'].split('.')[0].split('_')[-1] + '/' +
                                killstreak[4]['file_name'], action_label=action_label)

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

    # summarize_last_round()

summarize_all()

