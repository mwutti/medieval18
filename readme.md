Custom Object Detection using tensorflow and ssd_mobilenet_v1

Tensorboard
tensorboard --logdir ='/training'

Export inferenceGraph
within object_detection
python export_inference_graph.py --input_type image_tensor  --pipeline_config_path medieval-object-detection/training/pipeline.config --trained_checkpoint_prefix medieval-object-detection/training/model.ckpt-7778 --output_directory medieval-object-detection/training/inference_graph

Video-sequence types:
'match_start', 'summary', 'highlight', 'intro', 'show', 'interview', 'lag', 'match', 'matth_start'

link to videos
https://drive.google.com/open?id=1y79eT0StSrkNbynwD5p9C9S3WAei1c8p

ffmpeg
ffmpeg -ss 9:45:08 -i train_set\2018-03-02_P11.mp4 -t 3 -c copy videos_cut\trophies\5_trophy_2018-03-02_end.mp4