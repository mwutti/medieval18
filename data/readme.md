# GameStory: Video Game Analytics Challenge

In this task we encourage participants to think and investigate ways to summarize how e-sport matches ramp up, evolve and play out over time. Instead of iterating highlights, the summary needs to present an engaging and captivating story, which boils down the thrill of the game to its mere essence. Training and test data for the task are provided in cooperation with ZNIPE.TV, which is a rapidly growing platform for e-sport streaming. 


## Access all content for free at Znipe TV
In addition to the structured dataset, Znipe TV provide free access to all produced content during the tournament ESL One Katowice 2018 from which the structured dataset has been created. We engourage participants to claim their free access and watch some of the produced content to get inspiration for the task. To claim your free accsses, follow these steps:

1. Go to: [znipe.tv](https://beta.znipe.tv/esl-katowice-2018/gate)
2. Click buy digital pass 
3. Create an account or login
4. Enter the promocode: MEDIAEVAL-KATOWICE


# Dataset
This dataset consist of a set of video streams, game logs and stream meta data. Each of these will be described in detail below.


## Video streams
There are 12 different streams labeled P1 - P12. P is short for player. 
There are 10 players in a CS:GO match, 5 in each of the two teams. 
P1 - P10 are each of these player's perspective in the match. 
P11 is the event stream, where the pre-show, interviews, commentator view etc. is shown. P12 is only showing the map of the matches and is without audio. 

Each of these streams are up during the full day, and therefore there are 12 video files for each day.  The training set includes the matches from 2018-03-02 and 2018-03-04. 


## Meta Data
The file metadata.csv contains information about the streams. Timestamps and durations of matches during the days and in what stream file the match is. Each column in the csv table is described in below.


***ID*** - An alphanumeric id of the clip that the row represents.

***start_time*** - Number of seconds into the day stream file when this clip starts.

***duration*** - Number of seconds that this clip last.

***type*** - The clips in this dataset have a descriptive type. For example it could be labeled match, meaning that the clip is the full match stream that is showed when users select to watch a match at Znipe TV. There are a few more interesting types and as the number of clips are not that many, we encourange you to investigate the different types to get inspiration of what you can do. 

***match_id*** The train set contains 11 matches. Each clip belongs to one of these 11 matches and the match_id is a number between 1 and 11.

***perspective*** - Which of the P1-P12 the clip is from.

***stream_file*** - Which video stream file the clip exist in.

***stream_timestamp*** - The same as the start_time but in the human readable format HH:MM:SS to be able to easier manually jump to the clip in the stream file for investigation.

***UTC_timestamp*** - The UTC timestamp of the starting time in the clip. This can be used to synchronize the video stream time with the timestamps from the game logs described below. 


## Game logs
In the timeline folder, a game log exist for each match in the dataset.
The name of the files matches the match_id in metadata.csv.

Each game log is a json object that includes events such as what each player purchased, who killed whom and where. All actions have UTC timestamps. 
These timestamps may unfortunately differ up to 40 seconds from the UTC timestamps in the metadata.csv.





# Video processing tips
A program that can separate, cut and concat videos is ffmpeg. This program can be very useful when working with video data and below follows a few tips.


You may want to split audio and video inte separate files. This can be done with the commands below. Note that you have to change the file names to the name of the file that you want to split. 

```
ffmpeg -i input.mp4 # show stream numbers and formats
ffmpeg -i input.mp4 -c copy audio.m4a # AAC
ffmpeg -i input.mp4 -c copy audio.mp3 # MP3
ffmpeg -i input.mp4 -c copy audio.ac3 # AC3
ffmpeg -i input.mp4 -an -c copy video.mp4
ffmpeg -i input.mp4 -map 0:1 -c copy audio.m4a # stream 1
```


Cutting clip can be done. This example cuts the input video, generating a new clip that starts 50 seconds into the original video and takes the next 400 seconds. 


You may want to cut out a clip from the full day stream files. This can be done with the following line of code.
```
ffmpeg -ss 50 -i input.mp4 -t 400 output.mp4 
```
This line of code generate a new video file, output.mp4, starting from 50 seconds into the original video and takes the next 400 seconds. 


There are ways to cut out several clips from a large video file and concatenate them into one as well. If you would like to do this we refer to the documentation of ffmpeg. 


# Video analytics tips
If this is your first time working with analytics of video data, and you want to do it with machine learning,  we recommend you to check out [this short article](https://towardsdatascience.com/deep-learning-with-tensorflow-part-4-face-classification-and-video-inputs-fa078f22c1e5) to get a quick introduction. 
