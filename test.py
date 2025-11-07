# import os 
# os.chdir(r"C:\Users\y29ga\OneDrive\Documents\F5-tts\F5-TTS")
# os.system("conda activate f5-tts")
# os.system("set KMP_DUPLICATE_LIB_OK=TRUE")
# os.system("python batch_tts.py --base_folder C:\\Users\\y29ga\\OneDrive\\Desktop\\instagram\\dark-romance\\test")

# class test:
#     h = "helpl"
#     def test2(self):
#         print(self.h)

# obj = test()
# obj.test2()

# try:
#     print("sdbjgdgv")
#     print(2/0)
#     print("sdfvsdg")
# except:
#     print("e")
# with open("test.txt","r") as f:
#     l = [i.strip() for i in f if i.strip()]
# print(l)

# import time
# s = time.time()
# time.sleep(4)
# print(time.time()-s)
# import logging
# try:
#     logging.error("hello")
#     print("jii")
# except:
#     print("hi")

from multiprocessing import Process
import time

def task():
    print("Process working")
    time.sleep(3)

for _ in range(4):
    Process(target=task).start()
