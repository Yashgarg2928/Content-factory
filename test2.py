a = [i for i in range(20)]
print(a)
n = 0
for j in range(2,len(a),8):
    for k in range(j,len(a)):
        if n<8:

            print(k)
            n+=1
        else:
            n = 0
            print("----------------")
            break
