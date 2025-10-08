import os 
os.chdir(r"C:\Users\y29ga\OneDrive\Documents\F5-tts\F5-TTS")
os.system("conda activate f5-tts")
os.system("set KMP_DUPLICATE_LIB_OK=TRUE")
os.system("python batch_tts.py --base_folder C:\\Users\\y29ga\\OneDrive\\Desktop\\instagram\\dark-romance\\test")
