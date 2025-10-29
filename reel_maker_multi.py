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
# For Windows (update the path to where you installed ImageMagick)
# change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

def process_reels(base_folder): #makes a list of paths of reel folders
    reel_paths = []
    for reel_folder in os.listdir(base_folder): #get path of each folder one by one
        if reel_folder.isdigit():  #checks if its a folder of reel or not 
            reel_paths.append(os.path.join(base_folder, reel_folder))

    return reel_paths


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


#------------------------effects-----------------------------------------------
def zoom_in(clip, zoom_factor = 1.5, duration=None):
    from moviepy.editor import VideoFileClip
    from PIL import Image
    import numpy as np
    
    """
    Apply a zoom effect to a video clip.

    :param clip: The video clip to apply the zoom effect to.
    :param zoom_factor: The factor by which to zoom (e.g., 1.5 for zoom in).
    :param duration: The duration over which to apply the zoom effect in seconds.
    :return: The video clip with the zoom effect applied.
    """

    if duration is None:
        duration = clip.duration
    # Calculate the scaling factor over time
    def scaling_factor(t):
        # Linear interpolation from 1 to zoom_factor over the duration
        if t <= duration:
            return 1 + (zoom_factor - 1) * t / duration
        else:
            return zoom_factor

    # Apply the scaling factor to each frame
    def frame_transform(get_frame, t):
        frame = get_frame(t)
        scale = scaling_factor(t)
        h, w = frame.shape[:2]
        new_h, new_w = int(h / scale), int(w / scale)
        center_h, center_w = h // 2, w // 2
        start_h, start_w = center_h - new_h // 2, center_w - new_w // 2
        # Crop the frame to apply the zoom effect
        zoomed_frame = frame[start_h:start_h + new_h, start_w:start_w + new_w]
        # Resize the cropped frame back to the original dimensions
        zoomed_frame = np.array(Image.fromarray(zoomed_frame).resize((w, h)))
        return zoomed_frame

    # Apply the transformation to the clip
    zoomed_clip = clip.fl(frame_transform)
    return zoomed_clip


def zoom_out(clip, start_zoom=1.5, end_zoom=1.0, duration=None):
    from moviepy.editor import VideoFileClip
    import numpy as np
    from PIL import Image

    """
    Create a zoom out effect for a video clip using PIL for resizing.
    
    Parameters:
    input_file (str): Path to the input video file
    output_file (str): Path for the output video file
    duration (float, optional): Duration of the effect in seconds. If None, uses the full clip duration.
    start_zoom (float): Initial zoom level (e.g., 1.5 = 150% zoom)
    end_zoom (float): Final zoom level (typically 1.0 = 100% or original size)
    """
    
    # Set duration to full clip length if not specified
    if duration is None:
        duration = clip.duration
    
    # Define the zoom function
    def zoom_effect(get_frame, t):
        # Calculate current zoom level based on time (linear interpolation)
        current_zoom = start_zoom + (end_zoom - start_zoom) * t / duration
        
        # Get the frame at the current time
        frame = get_frame(t)
        
        # Get dimensions of the frame
        h, w = frame.shape[:2]
        
        # Calculate the crop size based on zoom
        crop_h = int(h / current_zoom)
        crop_w = int(w / current_zoom)
        
        # Calculate top-left corner of crop to keep it centered
        top = int((h - crop_h) / 2)
        left = int((w - crop_w) / 2)
        
        # Crop the frame
        cropped = frame[top:top + crop_h, left:left + crop_w]
        
        # Convert to PIL Image for resizing
        pil_img = Image.fromarray(cropped)
        
        # Resize back to original dimensions
        resized_img = pil_img.resize((w, h), Image.LANCZOS)
        
        # Convert back to numpy array
        resized = np.array(resized_img)
        
        return resized
    
    # Apply the effect
    zoomed_clip = clip.fl(zoom_effect)
    
    return zoomed_clip



def panLR(clip, zoom_factor=1.2):
    """
    Applies a pan effect from left to right while maintaining a zoomed-in state.
    
    :param clip: The video clip to apply the pan effect to.
    :param zoom_factor: How much to zoom in before panning.
    :return: Video clip with the pan effect applied.
    """

    duration = clip.duration  # Get the clip's actual duration

    def frame_transform(get_frame, t):
        frame = get_frame(t)
        h, w = frame.shape[:2]

        # Calculate zoomed-in dimensions
        new_h, new_w = int(h / zoom_factor), int(w / zoom_factor)
        center_h = h // 2
        start_h = center_h - new_h // 2  # Keep vertical centered
        start_w = 0  # Start from leftmost
        end_w = w - new_w  # Rightmost position

        # Compute the horizontal shift over time
        pan_x = int(start_w + (end_w - start_w) * (t / duration))

        # Crop to zoom in
        cropped_frame = frame[start_h:start_h + new_h, pan_x:pan_x + new_w]

        # Resize back to original dimensions
        resized_frame = np.array(Image.fromarray(cropped_frame).resize((w, h)))

        return resized_frame

    return clip.fl(frame_transform)




def panRL(clip, zoom_factor=1.2):
    """
    Applies a pan effect from right to left while maintaining a zoomed-in state.
    
    :param clip: The video clip to apply the pan effect to.
    :param zoom_factor: How much to zoom in before panning.
    :return: Video clip with the pan effect applied.
    """

    duration = clip.duration  # Get the clip's actual duration

    def frame_transform(get_frame, t):
        frame = get_frame(t)
        h, w = frame.shape[:2]

        # Calculate zoomed-in dimensions
        new_h, new_w = int(h / zoom_factor), int(w / zoom_factor)
        center_h = h // 2
        start_h = center_h - new_h // 2  # Keep vertical centered
        start_w = w - new_w  # Start from rightmost
        end_w = 0  # Move to leftmost

        # Compute the horizontal shift over time (moving right to left)
        pan_x = int(start_w - (start_w - end_w) * (t / duration))

        # Crop to zoom in
        cropped_frame = frame[start_h:start_h + new_h, pan_x:pan_x + new_w]

        # Resize back to original dimensions
        resized_frame = np.array(Image.fromarray(cropped_frame).resize((w, h)))

        return resized_frame

    return clip.fl(frame_transform)









def vignette(clip, intensity=0.9, feathering=0.8, radius=0.8):
    """
    Applies a soft vignette effect to the clip with bright center and dark edges.
    
    Args:
        clip: MoviePy video clip
        intensity: How dark the vignette edges will be (0.0-1.0)
        feathering: How gradual the transition from center to edge is (0.0-1.0)
        radius: Determines the size of the bright center area (0.0-1.0, smaller = smaller bright area)
        
    Returns:
        A new clip with the vignette effect applied
    """
    # Create the vignette mask once
    
    def create_vignette_mask(size, intensity=0.9, feathering=0.8, radius=0.8):

        from moviepy.editor import VideoFileClip, vfx
        import numpy as np
        
        """
        Creates a vignette mask with bright center and dark edges.
        
        Args:
            size: Tuple of (width, height) for the mask
            intensity: How dark the vignette edges will be (0.0-1.0)
            feathering: How gradual the transition from center to edge is (0.0-1.0)
            radius: Determines the size of the bright center area (0.0-1.0, smaller = smaller bright area)
            
        Returns:
            A numpy array representing the vignette mask
        """
        width, height = size
        center_x, center_y = width / 2, height / 2
        
        # Create coordinate grids
        y, x = np.ogrid[:height, :width]
        
        # Calculate normalized distance from center
        dist_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # Normalize distances
        max_dist = np.sqrt(center_x**2 + center_y**2)
        normalized_dist = dist_from_center / max_dist
        
        # Scale by radius to control size of bright area
        scaled_dist = normalized_dist / radius
        
        # Create mask with smoother transition using cosine function
        # This correctly makes center bright and edges dark
        transition = np.clip((scaled_dist - (1-feathering)) / feathering, 0, 1)
        mask = 1 - intensity * transition**2  # Proper vignette calculation
        
        return mask.reshape(height, width, 1)  # Reshape for broadcasting


    
    mask = create_vignette_mask(clip.size, intensity, feathering, radius)
    
    # Define the function to apply to each frame
    def vignette_frame(frame):
        return np.array(frame * mask, dtype='uint8')
    
    # Return the modified clip
    return clip.fl_image(vignette_frame)




def blur_with_glow(clip, blur_intensity=300, glow_intensity=1):
    def apply_blur(get_frame, t):
        frame = get_frame(t)
        blurred = cv2.GaussianBlur(frame, (blur_intensity, blur_intensity), 0)
        return np.clip(blurred * glow_intensity, 0, 255).astype(np.uint8)
    return clip.fl(apply_blur)





def shake_effect(clip, max_shake=5):
    def shake(get_frame, t):
        frame = get_frame(t)
        dx = random.randint(-max_shake, max_shake)
        dy = random.randint(-max_shake, max_shake)
        return np.roll(frame, (dx, dy), axis=(0, 1))
    return clip.fl(shake)


def fade_in_out(clip, duration=0.7):
    return clip.fadein(duration).fadeout(duration)



def sepia_effect(clip, intensity=0.3):
    return clip.fx(colorx, intensity)


def glitch_effect(clip, intensity=3):
    def glitch(get_frame, t):
        frame = get_frame(t)
        if random.random() > 0.9:  # Random glitch effect
            frame[:, :, 0] = np.roll(frame[:, :, 0], intensity, axis=1)
            frame[:, :, 2] = np.roll(frame[:, :, 2], -intensity, axis=0)
        return frame
    return clip.fl(glitch)



def glow_effect(clip, glow_intensity=1):
    """
    Adds a soft glow effect without blurring.
    
    :param clip: The video clip to modify.
    :param glow_intensity: How much brightness to add (1.0 = normal, higher = glowing).
    :return: The modified video clip.
    """
    return clip.fx(colorx, glow_intensity)

 #-------------------------------transistion-------------------------------------

def cross_dissolve(clip1, clip2, duration=1):
    """
    Creates a cross dissolve transition between two video clips.
    
    Parameters:
    -----------
    clip1 : VideoFileClip
        The first video clip (ending clip)
    clip2 : VideoFileClip
        The second video clip (starting clip)
    duration : float
        Duration of the transition in seconds
    
    Returns:
    --------
    CompositeVideoClip
        A composite clip with the cross-dissolve transition
    """
    # Get the duration of each clip
    clip1_duration = clip1.duration
    clip2_duration = clip2.duration
    
    # Create a copy of the second clip with a fade-in effect
    clip2_fadein = clip2.copy().fadein(duration)
    
    # Create a copy of the first clip with a fade-out effect
    clip1_fadeout = clip1.copy().fadeout(duration)
    
    # Position the second clip to start at the end of the first clip minus the transition duration
    clip2_fadein = clip2_fadein.set_start(clip1_duration - duration)
    
    # Set the total duration
    total_duration = clip1_duration + clip2_duration - duration
    
    # Create the composite clip with both clips
    final_clip = CompositeVideoClip([clip1_fadeout, clip2_fadein], size=clip1.size)
    
    # Set the duration of the final clip
    final_clip = final_clip.set_duration(total_duration)
    
    return final_clip





 #--------------------------------reel maker---------------------------------------

def editor(csv_path, output_path, path, words, srt_file, audio_path = None):
    image_durations = []
    image_effects = []
    image_transition = []
    lines = [] 
    # Read the CSV file
    image_number = 0
    word_number = 0
    with open(csv_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        
        for row in reader:

            #----------------------lines------------------------------------------
            line = row['line']
            
            lines.append(line)
            

            #---------------------image path----------------------------------
            image_path = os.path.join(path, row['image_path']) #image path
            

            #--------------------duration finder--------------------------------
            duration = 0
            if row['transition'] == "cross_dissolve":

                if len(lines[image_number]) == 0:
                    image_durations.append((image_path, 3))
                    image_number = image_number + 1

                else:
                
                    for word in words[word_number : word_number + len(lines[image_number].split())]:
                        
                        duration = duration + word[1]
                    word_number = word_number + len(lines[image_number].split())
                    image_number = image_number + 1
                    image_durations.append((image_path, duration + 1))
                print("image_durations :----" , image_durations)

            else:
                if len(lines[image_number]) == 0:
                    image_durations.append((image_path, 2))
                    image_number = image_number + 1

                else:
                
                    for word in words[word_number : word_number + len(lines[image_number].split())]:
                        
                        duration = duration + word[1]
                    word_number = word_number + len(lines[image_number].split())
                    image_number = image_number + 1
                    image_durations.append((image_path, duration + 0.3))
                print("image_durations :----" , image_durations)

            
            

            #---------------------effect finder----------------------------------
            effect = row['effect'].split(';')  #image effects
            image_effects.append(effect)
            

            #----------------------transition-------------------------------------
            transition = row['transition']  #image transition
            image_transition.append(transition)
            
        
        total_duration = sum([d for _, d in image_durations])
        print("Expected video length:", total_duration)



    # Create video clips for each image with specified durations
    video_clips = [ImageClip(image_path).set_duration(duration) for image_path, duration in image_durations]
    

    #adding effects
    effect_videos = []
    for clips in video_clips:
        effect_clip = clips
        for e in image_effects[video_clips.index(clips)]:
                
            if e == 'zoom_in':
                effect_clip = zoom_in(effect_clip)
            elif e == "zoom_out":
                effect_clip = zoom_out(effect_clip)
            elif e == "panLR":
                effect_clip = panLR(effect_clip)
            elif e == "panRL":
                effect_clip = panRL(effect_clip)
            elif e == "vignette":
                effect_clip = vignette(effect_clip)
            elif e == "blur_glow":
                effect_clip = blur_with_glow(effect_clip, blur_intensity=5, glow_intensity=1.6)
            elif e == "glow":
                effect_clip = glow_effect(effect_clip)
            elif e == "shake":
                effect_clip = shake_effect(effect_clip, max_shake=1)
            elif e == "sepia":
                effect_clip = sepia_effect(effect_clip, intensity=0.8)
            elif e == "glitch":
                effect_clip = glitch_effect(effect_clip, intensity=1)

        effect_videos.append(effect_clip)
        

        
    #tranitions
    transition_video = effect_videos[0]

    for idx, i in enumerate(effect_videos[1:]):
        t = image_transition[idx]  # Get the transition for this specific pair

        if t == 'cross_dissolve':
            transition_video = cross_dissolve(transition_video, i)
        
        else:  
            transition_video = cross_dissolve(transition_video, i, 0.3)
    print("Duration After Trabsitions :---", transition_video.duration)
                

                
                    
    # Add background music if audio_path is provided
    if audio_path:
        audio = AudioFileClip(audio_path)
        transition_video = transition_video.set_audio(audio)




    # Load the IM Fell English font (ensure it's installed or use a .ttf file)
    FONT_PATH = "Ubuntu-Bold"

    # Define subtitle style
    def subtitle_generator(txt):
        return TextClip(
            txt,
            fontsize=60, 
            color="white",
            font=FONT_PATH,  # Use IM Fell English
            bg_color="black"
        ).set_opacity(0.5)  # Semi-transparent background

    # Load the formatted SRT file
        
    subs = pysrt.open(srt_file)

    # Convert SRT subtitles to a list of tuples
    subtitles_list = [
        ((sub.start.ordinal / 1000, sub.end.ordinal / 1000), sub.text.replace("\n", " ")) 
        for sub in subs
    ]

    # Load subtitles into MoviePy
    subtitles = SubtitlesClip(subtitles_list, subtitle_generator)

    # Overlay subtitles on video at custom position
    final_video = CompositeVideoClip([
        transition_video, 
        subtitles.set_position(("center", transition_video.h * 0.8))  # Adjust position for a better match
    ])
        
    # # Outro clip (if provided)
    
    # extra_clip = VideoFileClip("C:/Users/y29ga/OneDrive/Desktop/instagram/dark-romance/outro_clip.mp4")
    # # Resize and match FPS
    # extra_clip = extra_clip.resize(height=transition_video.h).set_fps(transition_video.fps).set_audio(None)

    # # Convert to the same codec
    # extra_clip = extra_clip.set_duration(extra_clip.duration)  

    # # Ensure both clips are RGB format (some videos may use YUV)
    # extra_clip = extra_clip.set_opacity(1)

    # # Concatenate safely
    # final_video = concatenate_videoclips([transition_video, extra_clip], method="compose")  
    
   


    
    # Generate a unique temporary audio file for each folder
    temp_audiofile = os.path.join(path, f"temp_audio_{uuid.uuid4().hex}.mp3")
    
    # Write the final video with a unique temp audio file
    final_video.write_videofile(output_path, codec='libx264', fps=24, temp_audiofile=temp_audiofile)

    # Ensure the temporary file is deleted after processing
    if os.path.exists(temp_audiofile):
        try:
            os.remove(temp_audiofile)
        except PermissionError:
            print(f"Warning: Could not delete {temp_audiofile}, it may still be in use.")

    print("✅ Reel Created Successfully!")

    print("FUCKING REEL CREATED !!!!!!!!!! ")



base_folder = input("ENTER BASE FOLDER :-")
folders = process_reels(base_folder)
import concurrent.futures

def process_reel(path):
    a = path.split(os.sep)
    csv_path = os.path.join(path, "config.csv")
    output_path = os.path.join(path, f"reel{a[-1]}.mp4")
    srt_file = os.path.join(path, "audio.srt")
    audio_file = os.path.join(path, "audio.wav")

    print("Processing reel: ----", path)

    # Call subtitle maker function
    subtitles, words = subtitle_maker(srt_file, path)

    # Call video editor function
    editor(csv_path, output_path, path, words, subtitles, audio_file)

    return f"Done processing: {path}"

# Run processing in parallel
if __name__ == '__main__':
    with concurrent.futures.ProcessPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(process_reel, folders))

    print("All reels processed:", results)


