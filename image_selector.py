import google.generativeai as genai
from PIL import Image  # Pillow library for image handling
import os
from concurrent.futures import ProcessPoolExecutor


def generate_content_with_images(api_key, image_paths, prompt):
    """
    Generates content using the Gemini Pro Vision model with multiple images and text prompt.

    Args:
        api_key: Your Google Gemini API key.
        image_paths: A list of paths to the image files.
        prompt: The text prompt to guide the content generation.

    Returns:
        The generated text content, or None if an error occurred.
    """

    genai.configure(api_key=api_key)

    # Load the Gemini Pro Vision model (multimodal)
    model = genai.GenerativeModel('gemini-2.5-flash')

    images = []
    for image_path in image_paths:
        try:
            img = Image.open(image_path)
            images.append(img)
        except FileNotFoundError:
            print(f"Error: Image file not found at {image_path}")
            return None  # Or raise the exception, depending on desired behavior
        except Exception as e:
            print(f"Error: Could not open image {image_path}: {e}")
            return None  # Or raise the exception

    # Send the prompt and images to the model
    try:
        input_data = [prompt] + images  # Create a list: [text, image1, image2, image3, ...]
        response = model.generate_content(
            input_data,
                safety_settings={
                    "HARASSMENT": "BLOCK_NONE",
                    "HATE_SPEECH": "BLOCK_NONE",
                    "SEXUAL": "BLOCK_NONE",
                    "DANGEROUS": "BLOCK_NONE"
                }
        )
        response.resolve()
        for b in images:
            b.close()
        return response.text
    except Exception as e:
        print(f"An error occurred during content generation: {e}")
        for b in images:
            b.close()        
        return None  # Or raise the exception


def image_path_process(reel_folder): #makes a list of paths of reel folders
    image_paths = []
    items_list = os.listdir(reel_folder)
    final_list = []
    for i in items_list:
        final_list.append(os.path.join(reel_folder,i))
    for item in final_list: #get path of each folder one by one
        present = False
        image_no = 0
        if item[-4:] == ".jpg":
            for image in image_paths:
                if item[:-5] == image[0][:-5]:
                    present = True
                    image_no = image_paths.index(image)
            if present:
                image_paths[image_no].append(item)

            else:
                a = [item]
                image_paths.append(a)
                
    return image_paths

def process_reels(base_folder): #makes a list of paths of reel folders
    reel_paths = []
    for reel_folder in os.listdir(base_folder): #get path of each folder one by one
        if reel_folder.isdigit():  #checks if its a folder of reel or not 
            reel_paths.append(os.path.join(base_folder, reel_folder))
    return reel_paths


def multi_fn(data_list):
    reel, api_key = data_list
    final_images = []
    with open(os.path.join(reel,"prompts.txt"), 'r', encoding='utf-8') as file:
        img_prompts = [line.strip() for line in file if line.strip()]
        img_prompts = [prompt for line in img_prompts for prompt in (line,line,line,line)]

    if not img_prompts:
        print("No prompts found in the file.")

        
    image_paths = image_path_process(reel)
    for image in image_paths:
        image_prompt = ""
        for j in img_prompts:
            if image[:-5] == j.split()[0]:
                image_prompt = j
                break

        prompt = '''You will be provided with 3 to 4 images, all generated using the same prompt.

                Your task is to analyze all the images visually and identify the single image that appears the most natural, aesthetically pleasing, and realistic from a human perspective.

                Specifically, look for the image that has the least amount of visible deformities or strange artifacts. Deformities include (but are not limited to):

                * Extra or missing body parts (e.g., 5 legs, 3 arms, fused limbs)
                * Anatomical errors (e.g., broken limbs, unnatural bone bends, twisted posture)
                * Distorted or melted faces
                * Unrealistic or unsettling features (e.g., hands growing from heads, eyes in the wrong place, finger-like textures on skin)
                * Any other strange or unnatural elements that would make a viewer uncomfortable or confused

                You must return only the serial number (e.g., 1, 2, etc.) of the single best image that looks the most human-like and clean to the eye.

                ⚠️ Do not include any explanation, comparison, or multiple choices. Return only and only one plain number — the serial number of the image that stands out as the most natural and visually correct. Do not include any special characters like '#' — just the number itself.

                ''' 

        generated_text = generate_content_with_images(api_key, image, prompt)

        if generated_text:
            print("Generated Text:")
            print(generated_text)
        else:
            print("Content generation failed.")

        
        final_images.append(image.pop(int(generated_text)-1))
        
        #deleting
        for k in image:
            os.remove(k)
        print(final_images)
        
    #Fixing the names
    for image_name in final_images:
        os.rename(image_name, (image_name[:-5] + image_name[-4:]))
    
        
# Example usage:
if __name__ == "__main__":

    with open("api_keys.txt","r",encoding='utf-8') as api_file:
        google_api_key_list = api_file.read().split("\n")
    print(google_api_key_list)

    base_folder = input("Enter Base folder : ")
    reel_folders = process_reels(base_folder)

    data_list = [
        (reel_folders[i],google_api_key_list[i%8])
        for i in range(len(reel_folders))
    ]
    
    with ProcessPoolExecutor(max_workers=8) as executor:
        results = executor.map(multi_fn, data_list)
    print("ALL REEL DONE ")
