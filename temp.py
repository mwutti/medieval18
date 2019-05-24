
dest_video_path = "/path/to/video/folder"
begin = start_pos - clipping_offset_before
dest_video_name = 'killstreak_' + killstreak_length + '_round_' + round + '_begin_' + begin +
                  '_' + stream_name


cut_video_within_boundaries(target_video_path, begin,  killstreak_length + clipping_offset_after,
                            dest_video_path + '/' + killstreak_length + '/' + player_stream + '/' + dest_video_name)

def cut_video_within_boundaries(target_video_path, begin_sec, duration, dest_video_path):
    subprocess.call(['ffmpeg', '-loglevel', 'warning', '-ss', str(begin_sec - 30), '-i',
                     target_video_path, '-ss', '30', '-t', duration, dest_video_path])

