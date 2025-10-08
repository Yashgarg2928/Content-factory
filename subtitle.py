from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, VideoClip, VideoFileClip, CompositeVideoClip, TextClip
from moviepy.video.fx.all import resize , colorx
import cv2
import random
import os
import csv
import numpy as np
from PIL import Image
import pysrt
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.config import change_settings
import uuid
def subtitle_maker(srt_file, path):
    '''
    def remove_silent_subs(srt_file, min_duration_ms=500):
        subs = pysrt.open(srt_file)
        new_subs = pysrt.SubRipFile()
        
        for sub in subs:
            duration = sub.end.ordinal - sub.start.ordinal
            if duration > min_duration_ms and len(sub.text.split()) < 2:
                continue
            new_subs.append(sub)
        
        return new_subs
    '''
    def split_srt_into_chunks(srt_file, words_per_segment=4):
        subs = pysrt.open(srt_file)
        new_subs = pysrt.SubRipFile()
        word_durations = []
        
        index = 1
        prev_end_time = None
        
        for sub in subs:
            words = sub.text.split()
            num_chunks = len(words) // words_per_segment + (1 if len(words) % words_per_segment else 0)
            chunk_duration = (sub.end.ordinal - sub.start.ordinal) // max(1, num_chunks)
            
            if prev_end_time is not None and prev_end_time < sub.start.ordinal:
                silence_duration = sub.start.ordinal - prev_end_time
                new_sub = pysrt.SubRipItem(
                    index=index,
                    start=pysrt.SubRipTime(milliseconds=prev_end_time),
                    end=pysrt.SubRipTime(milliseconds=sub.start.ordinal),
                    text="silence"
                )
                new_subs.append(new_sub)
                
                if word_durations:
                    word_durations[-1][1] += silence_duration / 1000
                
                index += 1
            
            for i in range(0, len(words), words_per_segment):
                chunk_words = words[i:i + words_per_segment]
                start_time = sub.start.ordinal + (i // words_per_segment) * chunk_duration
                end_time = start_time + chunk_duration
                
                new_sub = pysrt.SubRipItem(
                    index=index,
                    start=pysrt.SubRipTime(milliseconds=start_time),
                    end=pysrt.SubRipTime(milliseconds=end_time),
                    text=" ".join(chunk_words)
                )
                new_subs.append(new_sub)
                index += 1
                
                for word in chunk_words:
                    word_durations.append([word, chunk_duration / len(chunk_words) / 1000])
            
            prev_end_time = sub.end.ordinal
        
        return new_subs, word_durations
    '''
    clean_subs = remove_silent_subs(srt_file)
    clean_srt_file = os.path.join(path, "clean_subs.srt")
    clean_subs.save(clean_srt_file, encoding = "utf-8")
    '''

    formatted_subs, word_durations = split_srt_into_chunks(srt_file)
    formatted_srt_file = os.path.join(path, "formatted_4_words.srt")
    formatted_subs.save(formatted_srt_file, encoding="utf-8")

    print("✅ Subtitles formatted with 4 words per screen!")
    print("Word durations:", word_durations)

    return formatted_srt_file, word_durations 

subtitle_maker(input("enter subtitle file : "),input("enter folder path:"))