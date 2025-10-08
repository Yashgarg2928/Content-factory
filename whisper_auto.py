import os

def process_reels(base_folder): #makes a list of paths of reel folders
    reel_paths = []
    for reel_folder in os.listdir(base_folder): #get path of each folder one by one
        if reel_folder.isdigit():  #checks if its a folder of reel or not 
            reel_paths.append(os.path.join(base_folder, reel_folder))

    return reel_paths

base_folder = input("Enter Base folder : ")
folders = process_reels(base_folder)
for i in folders:
    print(i)
    os.chdir(i)  # Change to your desired directory
    print(os.getcwd())  # Verify the current directory
    print(f"nevigating to {i}")
    print("starting whisper")
    os.system("whisper audio.wav --output_format srt")
    print(i)
#os.system("dir")