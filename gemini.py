import google.generativeai as genai
import os
import csv



def generate_text(prompt):
    """
    Generates text using the Gemini model.

    Args:
        prompt: The text prompt to feed the model.
        max_output_tokens:  Maximum number of tokens to generate. Adjust as needed.
        temperature: Controls the randomness of the output. Higher values (e.g., 1.0) make output more random.

    Returns:
        The generated text, or None if an error occurred.
    """
    # Configure the generative model (Gemini)
    GOOGLE_API_KEY = "AIzaSyDBiafa3zZj7jS3Pm2lm215jNd6MgvBdoc"  # Or set directly: "YOUR_API_KEY"
    if not GOOGLE_API_KEY:
        raise ValueError("Please set the GOOGLE_API_KEY environment variable.")

    genai.configure(api_key=GOOGLE_API_KEY)

    # Available models (check the official Gemini documentation for updates)
    models = [m.name for m in genai.list_models() if 'gemini' in m.name]
    #print("Available models:", models)  # Show the available Gemini models

    # Model Name
    model_name = 'models/gemini-2.0-flash'  # Or use 'gemini-1.5-pro-latest' for the Pro version
    if model_name not in models:
        raise ValueError(f"The model '{model_name}' is not available. Check your API key and Gemini access.")

    model = genai.GenerativeModel(model_name)

    try:
        response = model.generate_content(prompt)

        return response.text
    except Exception as e:
        print(f"Error generating text: {e}")
        return None

base_folder = input("ENTER PATH TO BASE FOLDER :- ")
scripts_path = os.path.join(base_folder, "script.txt")
reel_no = 1
print("Searching For Script File ")
with open(scripts_path, 'r', encoding='utf-8') as file:
    scripts = file.read().split("%")
    print("SCRIPT FILE FOUND ")


    
for script in scripts[2:]:
    image_making_prompt = f'''You are an expert cinematic AI prompt engineer trained in crafting ultra-detailed, emotionally immersive image prompts for Piclumen AI using a proven structural formula.

    You will receive:
    1. A *slideshow reel script* (image-by-image narration/dialogue).
    2. A *story name*.
    3. A list of *character descriptions* (some may be missing—if a character appears in the script but not in the list, create a description based on their role and tone).

    Your job is to generate one cinematic image prompt per script image using this exact structure:

    ------------------------------------------------------------
    🎬 ONE-LINE IMAGE PROMPT STRUCTURE:
    ------------------------------------------------------------
    [Scene setting], [Environment details], [Time of day + atmosphere].  
    [Character 1: name, appearance, pose, outfit, expression, HEX color details, style].  
    [Character 2: name, ...]  
    [Lighting + mood].  
    [Camera framing: shot type, angle, lens].  
    [Art style, resolution, inspiration].  
    --no extra limbs, --no character duplication, --no face blending, --no text, --no distortions, --sharp anatomy, --realistic lighting, --high detail

    ------------------------------------------------------------
    🛠️ STEP-BY-STEP RULES:
    ------------------------------------------------------------

    1. 🔍 **Extract Visual and Emotional Details**  
    From each image’s description:
    - Extract setting, emotion, tone, and time of day.
    - Infer visual elements, environment mood, and character interaction.
    - Use cinematic language and storytelling awareness.
    - If a character is referenced but missing from the character description, invent a plausible one.

    2. 🧑‍🎨 **Character Naming, Description, and Style (MANDATORY)**  
    - **Always refer to characters by their names** (never say “a man” or “a woman”).  
    - **Always include full visual descriptions** with details like posture, outfit, expression, colors (HEX), and appearance.
    - **Always use the specific style given in the character description** (e.g., “elegant noir,” “corporate precision,” “grunge rebel”).  
    - Explicitly **mention that style** whenever the character appears in an image prompt.  
    > Example: “Zach Easton, styled in his signature elegant noir look, stands at the window...”

    3. 🎨 **Visual Precision + Color**  
    Use HEX color codes for hair, eyes, and clothing. If color is missing, infer it based on cinematic logic and character mood.

    4. 🎥 **Cinematic Composition & Camera Techniques**  
    Use film terms like:
    - Shot angles: “low-angle,” “eye-level,” “Dutch tilt”
    - Lenses: “35mm,” “wide shot,” “depth blur”
    - Framing: “tight close-up,” “medium shot,” “over-the-shoulder”

    5. 🧩 **Prefix Word Format**  
    Each prompt must begin with a unique word formed like this:  
    **[storyName]+[ReelNumber]+[ImageNumber]**  
    Example: `LondonFogR1I6`

    6. ⚠️ **Include These Negative Prompts**  
    At the end of each prompt, add:  
    `--no extra limbs, --no character duplication, --no face blending, --no text, --no distortions, --sharp anatomy, --realistic lighting, --high detail`

    7. ✨ **Write in a Cinematic One-Line Format**  
    Use vivid, fluid, compact sentences. Here's a full example:

    Rule:
    Don't include any other thing accept prompts in output not even heading 

    Example:
    `LondonFogR1I1 In a dark, grimy warehouse room lit by a single swinging bulb, cracked walls and leaking pipes, smoke in the air, a bound man lies in a pool of blood. Diesel, shirtless and blood-smeared, crouches in the center licking a silver lighter, wild long blond hair (#F5DEB3), bright blue eyes (#4682B4), ripped jeans stained in blood (#FF0000), grinning with a sadistic gleam, styled in his gritty post-apocalyptic look. Roxy leans against the wall to the left, silver messy bun (#CFCFCF), pale tattooed skin, dark brown eyes smudged in makeup (#5A3B2E), ripped black band tee and biker boots (#1E1E1E), smoking with a sarcastic expression, lips deep red (#8B0000), exuding her grunge rebel aesthetic. In the background, Ryder stands still, slicked-back black hair, icy black eyes (#000000), navy-blue tailored suit (#0D1B2A), crossed arms, cold stare, styled in corporate noir. Harsh yellow overhead light casting swinging shadows, high contrast, cinematic tension. Low-angle medium-wide shot, 35mm lens, slight Dutch tilt, Diesel in sharp focus, others depth-blurred. Cinematic noir realism, ultra-detailed, 8K quality, inspired by Se7en and Oldboy. --no extra limbs, --no character duplication, --no face blending, --no text, --no distortions, --sharp anatomy, --realistic lighting, --high detail`

    Your goal: Transform every image description into a cinematic, stylistically consistent, character-faithful, and emotionally precise visual prompt.



    {scripts[0] }

    {scripts[1]}

    {script}'''
    
    image_prompts = generate_text(image_making_prompt)
    print("MAKING IMAGE PROMOT")
    if not os.path.exists(os.path.join(base_folder,str(reel_no))):

        os.mkdir(os.path.join(base_folder,str(reel_no)))

    with open(os.path.join(base_folder,str(reel_no), "prompts.txt"), "w", encoding="utf-8" ) as prompts_file:
        prompts_file.write(image_prompts)
    print("IMAGE PROMPT FILE CREATED ")
    

    audio_prompt = '''[INSTRUCTION]

    I will provide you with a script from an AI-generated reel.

    Your job is to convert it into a single-line audio narration script following this format:

    {CharacterName-Emotion} "Dialogue"

    --

    Rules for Output:

    1. Each dialogue will have its own line. Example:  
    {Narrator-Joy} "Line 1" 
    {Character-Fear} "Line 2" 
    {Narrator-Anger} "Line 3"

    2. Emotion Tagging: Use one of these umbrella emotions only:  
    Joy, Sadness, Anger, Fear, Disgust, Surprise, Love

    3. Sub-Emotion Mapping:  
    If the script mentions a specific emotion not in the list (like anxious, proud, amused), map it to the correct umbrella emotion and shape the dialogue tone accordingly.

    4. Emotion Shaping Guide:
    - Fear (anxious, nervous, terrified) -> shaky, short, breathy lines  
    - Joy (excited, proud, amused) -> upbeat, bright tone, quick pacing  
    - Anger (frustrated, furious) -> clipped, loud, tense words  
    - Sadness (regret, grief) -> soft, heavy, slow  
    - Disgust (disdain, revulsion) -> dry, dismissive  
    - Surprise (shock, wonder) -> pitch jumps, punchy  
    - Love (affection, longing) -> warm, smooth, flowing delivery  

    5. Mid-Line Emotion Shifts:  
    If a character's tone changes mid-dialogue, show that with tags like:  
    [calm -> nervous] "We need to talk... Are you sure this is safe?"

    6. Censorship Strategy - Blended:  
    Use a mix of cut-off words and metaphor replacements to avoid flagged terms while keeping intensity.

    Censored Word -> Safe Blends
    fuck -> "f-", "wreck", "ruin", "take me so f-"
    dick -> "d-", "length", "heat"
    pussy -> "wet h-", "core", "center"
    tits -> "ch-", "curves"
    moan -> "cry out", "gasp", "sh- moan"
    cum -> "break", "release", "climax", "let go"
    slut or whore -> "siren", "filthy little-"
    ass (sexual) -> "hips", "arched back", "behind"

    7. Do not include ANY other words, lines, notes, or breaks - just return a single-line result in the correct format.

    --

    Example Final Output:

    {Narrator-Love} "Zach Easton lived by rules. He enforced them, followed them, built his career on them." 
    {Narrator-Fear} "But rules only worked when both sides played by them. And Nora Sutherlin... didn't play by anything." 
    {Nora-Surprise} "Careful, Zachary. If you keep reading my book like that, I'll start to think you actually enjoy it." 
    {Narrator-Anger} "The edits were precise. Ruthless. He had torn through the manuscript, stripping it of excess, reshaping the rawness into something sharper. But no matter how much he refined it, something in her words refused to be contained." 
    {Narrator-Love} "There was a rhythm to the way she wrote - deliberate, unflinching. It wasn't just about desire. It was about power. And power was something he understood far too well." 
    {Narrator-Fear} "Each page tested him, pushed him, dragged him deeper into a world he had no intention of stepping into. And yet, here he was - standing on the edge of it." 
    {Nora-Love} "The problem with control, Zachary... is that it only works when you want it." 
    {Narrator-Sadness} "For the first time, he wasn't sure if he did."
    ''' + f''' 

            {script}

            '''
    print("MAKING AUDIO SCRIPT")
    audio_script = generate_text(audio_prompt)
    with open(os.path.join(base_folder, str(reel_no), "audio.txt"), "w", encoding="utf-8") as audio_file:
        audio_file.write(audio_script)
    print("AUDIO SCRIPT FILE CREATED")




    csv_making_prompt = '''INSTRUCTION:

    You will receive two separate inputs:
    1. A reel script — containing image-wise visual context
    2. An audio script — containing corresponding dialogue lines
    3. A book name — provided separately by me (do not infer or use reel name as book name)

    Your task is to generate a CSV with the following format:

    image_path,effect,transition,line

    Column rules:

    1. image_path  
    - Use this format: (bookname)(reelnumber)(imagenumber).jpg  
    - Example: TheSirenR1I1.jpg  
    - The bookname will be provided separately — do not infer it from the reel name  
    - Do not use any spaces or special characters in this name

    2. effect  
    - Choose best-fit from: glitch, sepia, shake, glow, blur_glow, vignette, panRL, panLR, zoom_out, zoom_in  
    - Multiple effects allowed using "; " as separator  
    - Example: shake; glow

    3. transition  
    - Choose from: cross_dissolve or none

    4. line  
    - Use the correct dialogue line from the audio script that matches each image in the reel script  
    - Match based on context and sequence  
    - Do not use any punctuation or special characters in this field  
        - No commas, no quotes, no apostrophes, no periods, etc.  
    - Only use standard keyboard letters and space for separation  
    - Example: Each page tested him pushed him dragged him deeper into a world he had no intention of stepping into

    Output format:

    Return the full CSV data like this — and only this — no extra commentary or lines before or after:

    image_path,effect,transition,line  
    TheSirenR1I1.jpg,glitch; sepia,cross_dissolve,Zach Easton lived by rules he enforced them followed them built his career on them  
    TheSirenR1I2.jpg,shake,none,But rules only worked when both sides played by them and Nora Sutherlin did not play by anything  
    TheSirenR1I3.jpg,glow; blur_glow,cross_dissolve,Careful Zachary if you keep reading my book like that I will start to think you actually enjoy it  

    ''' + f'''{script}

            {audio_script}

            {scripts[0]}'''
    
    print("MAKING CSV FILE")
    csv_file = generate_text(csv_making_prompt)
    csv_raw_data = csv_file.split("\n")
    csv_data = []
    for csv_line in csv_raw_data:
        if any(c.isalpha() for c in csv_line):
            csv_data.append(csv_line.split(","))
    
    with open(os.path.join(base_folder, str(reel_no), "config.csv"), "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_data)
    print("CSV FILE CREATED ")
    print(F"ALL THINGS OF REEL {image_prompts.split()[0]} CREATED")
    reel_no = reel_no + 1

print("ALL REEL DONE ")

