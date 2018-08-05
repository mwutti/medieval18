Custom Object Detection using tensorflow and ssd_mobilenet_v1

Tensorboard
tensorboard --logdir ='/training'

Export inferenceGraph
within object_detection
python export_inference_graph.py --input_type image_tensor  --pipeline_config_path medieval-object-detection/training/pipeline.config --trained_checkpoint_prefix medieval-object-detection/training/model.ckpt-7778 --output_directory medieval-object-detection/training/inference_graph