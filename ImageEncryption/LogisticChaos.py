from PIL import Image
import numpy as np
import os
from matplotlib.pyplot import imshow
from skimage.metrics import structural_similarity as ssim
import cv2

def getImageMatrix(imageName):
    im = Image.open(imageName)
    pix = im.load()
    color = 1
    if type(pix[0,0]) == int:
      color = 0
    image_size = im.size
    image_matrix = []
    for width in range(int(image_size[0])):
        row = []
        for height in range(int(image_size[1])):
                row.append((pix[width,height]))
        image_matrix.append(row)
    return image_matrix,image_size[0],color

def getImageMatrix_gray(imageName):
    im = Image.open(imageName).convert('LA')
    pix = im.load()
    image_size = im.size
    image_matrix = []
    for width in range(int(image_size[0])):
        row = []
        for height in range(int(image_size[1])):
                row.append((pix[width,height]))
        image_matrix.append(row)
    return image_matrix,image_size[0]


def LogisticEncryption_Binary(imageName, binary_sequence):
    key_list = []
    #print(binary_sequence[8:16])
    i = 0
    while (i < len(binary_sequence)):
        key_list.append(binary_sequence[i:i + 8])
        i += 8
    N = 256
    key_list = [int(f,2) for f in key_list]
    G = [key_list[0:4], key_list[4:8], key_list[8:12]]
    g = []
    R = 1
    for i in range(1, 4):
        s = 0
        for j in range(1, 5):
            s += G[i - 1][j - 1] * (10 ** (-j))
        g.append(s)
        R = (R * s) % 1

    L = (R + key_list[12] / 256) % 1
    S_x = round(((g[0] + g[1] + g[2]) * (10 ** 4) + L * (10 ** 4)) % 256)
    V1 = sum(key_list)
    V2 = key_list[0]
    for i in range(1, 13):
        V2 = V2 ^ key_list[i]
    V = V2 / V1

    L_y = (V + key_list[12] / 256) % 1
    S_y = round((V + V2 + L_y * 10 ** 4) % 256)
    C1_0 = S_x
    C2_0 = S_y
    C = round((L * L_y * 10 ** 4) % 256)
    C_r = round((L * L_y * 10 ** 4) % 256)
    C_g = round((L * L_y * 10 ** 4) % 256)
    C_b = round((L * L_y * 10 ** 4) % 256)
    x = 4 * (S_x) * (1 - S_x)
    y = 4 * (S_y) * (1 - S_y)

    imageMatrix, dimension, color = getImageMatrix(imageName)
    LogisticEncryptionIm = []
    #print("Dimension: ",dimension)
    for i in range(dimension):
        #print("i: ",i)
        row = []
        for j in range(dimension):
            #print("j: ", j)
            while x < 0.8 and x > 0.2: #Waiting indefinetly
                x = 4 * x * (1 - x)
                if x == 0.75:
                    break
                #print(x)
            while y < 0.8 and y > 0.2: #Waiting indefinetly
                y = 4 * y * (1 - y)
                if y == 0.75:
                    break
                #print(y)

            x_round = round((x * (10 ** 4)) % 256)
            y_round = round((y * (10 ** 4)) % 256)

            C1 = x_round ^ ((key_list[0] + x_round) % N) ^ ((C1_0 + key_list[1]) % N)
            C2 = x_round ^ ((key_list[2] + y_round) % N) ^ ((C2_0 + key_list[3]) % N)

            if color:
                C_r = ((key_list[4] + C1) % N) ^ ((key_list[5] + C2) % N) ^ (
                            (key_list[6] + imageMatrix[i][j][0]) % N) ^ ((C_r + key_list[7]) % N)
                C_g = ((key_list[4] + C1) % N) ^ ((key_list[5] + C2) % N) ^ (
                            (key_list[6] + imageMatrix[i][j][1]) % N) ^ ((C_g + key_list[7]) % N)
                C_b = ((key_list[4] + C1) % N) ^ ((key_list[5] + C2) % N) ^ (
                            (key_list[6] + imageMatrix[i][j][2]) % N) ^ ((C_b + key_list[7]) % N)
                row.append((C_r, C_g, C_b))
                C = C_r

            else:
                C = ((key_list[4] + C1) % N) ^ ((key_list[5] + C2) % N) ^ ((key_list[6] + imageMatrix[i][j]) % N) ^ (
                            (C + key_list[7]) % N)
                row.append(C)

            x = (x + C / 256 + key_list[8] / 256 + key_list[9] / 256) % 1
            y = (x + C / 256 + key_list[8] / 256 + key_list[9] / 256) % 1

            for ki in range(12):
                key_list[ki] = (key_list[ki] + key_list[12]) % 256
                key_list[12] = key_list[12] ^ key_list[ki]
        LogisticEncryptionIm.append(row)
    im = Image.new("L", (dimension, dimension))
    if color:
        im = Image.new("RGB", (dimension, dimension))
    else:
        im = Image.new("L", (dimension, dimension))  # L is for Black and white pixels

    pix = im.load()
    for x in range(dimension):
        for y in range(dimension):
            pix[x, y] = LogisticEncryptionIm[x][y]
    im.save(imageName.split('.')[0] + "_Encryption.png", "PNG")
    print("Image saved.")

def LogisticEncryption(imageName, key):
    N = 256
    key_list = [ord(x) for x in key]
    G = [key_list[0:4], key_list[4:8], key_list[8:12]]
    g = []
    R = 1
    for i in range(1, 4):
        s = 0
        for j in range(1, 5):
            s += G[i - 1][j - 1] * (10 ** (-j))
        g.append(s)
        R = (R * s) % 1

    L = (R + key_list[12] / 256) % 1
    S_x = round(((g[0] + g[1] + g[2]) * (10 ** 4) + L * (10 ** 4)) % 256)
    V1 = sum(key_list)
    V2 = key_list[0]
    for i in range(1, 13):
        V2 = V2 ^ key_list[i]
    V = V2 / V1

    L_y = (V + key_list[12] / 256) % 1
    S_y = round((V + V2 + L_y * 10 ** 4) % 256)
    C1_0 = S_x
    C2_0 = S_y
    C = round((L * L_y * 10 ** 4) % 256)
    C_r = round((L * L_y * 10 ** 4) % 256)
    C_g = round((L * L_y * 10 ** 4) % 256)
    C_b = round((L * L_y * 10 ** 4) % 256)
    x = 4 * (S_x) * (1 - S_x)
    y = 4 * (S_y) * (1 - S_y)

    imageMatrix, dimension, color = getImageMatrix(imageName)
    LogisticEncryptionIm = []
    for i in range(dimension):
        row = []
        for j in range(dimension):
            while x < 0.8 and x > 0.2:
                x = 4 * x * (1 - x)
            while y < 0.8 and y > 0.2:
                y = 4 * y * (1 - y)
            x_round = round((x * (10 ** 4)) % 256)
            y_round = round((y * (10 ** 4)) % 256)
            C1 = x_round ^ ((key_list[0] + x_round) % N) ^ ((C1_0 + key_list[1]) % N)
            C2 = x_round ^ ((key_list[2] + y_round) % N) ^ ((C2_0 + key_list[3]) % N)
            if color:
                C_r = ((key_list[4] + C1) % N) ^ ((key_list[5] + C2) % N) ^ (
                            (key_list[6] + imageMatrix[i][j][0]) % N) ^ ((C_r + key_list[7]) % N)
                C_g = ((key_list[4] + C1) % N) ^ ((key_list[5] + C2) % N) ^ (
                            (key_list[6] + imageMatrix[i][j][1]) % N) ^ ((C_g + key_list[7]) % N)
                C_b = ((key_list[4] + C1) % N) ^ ((key_list[5] + C2) % N) ^ (
                            (key_list[6] + imageMatrix[i][j][2]) % N) ^ ((C_b + key_list[7]) % N)
                row.append((C_r, C_g, C_b))
                C = C_r

            else:
                C = ((key_list[4] + C1) % N) ^ ((key_list[5] + C2) % N) ^ ((key_list[6] + imageMatrix[i][j]) % N) ^ (
                            (C + key_list[7]) % N)
                row.append(C)

            x = (x + C / 256 + key_list[8] / 256 + key_list[9] / 256) % 1
            y = (x + C / 256 + key_list[8] / 256 + key_list[9] / 256) % 1
            for ki in range(12):
                key_list[ki] = (key_list[ki] + key_list[12]) % 256
                key_list[12] = key_list[12] ^ key_list[ki]
        LogisticEncryptionIm.append(row)

    im = Image.new("L", (dimension, dimension))
    if color:
        im = Image.new("RGB", (dimension, dimension))
    else:
        im = Image.new("L", (dimension, dimension))  # L is for Black and white pixels

    pix = im.load()
    for x in range(dimension):
        for y in range(dimension):
            pix[x, y] = LogisticEncryptionIm[x][y]
    im.save(imageName.split('.')[0] + "_Encryption.png", "PNG")


def LogisticDecryption_Binary(imageName, binary_sequence):
    key_list = []
    #print(binary_sequence[8:16])
    i = 0
    while (i < len(binary_sequence)):
        key_list.append(binary_sequence[i:i + 8])
        i += 8
    N = 256
    key_list = [int(f, 2) for f in key_list]

    G = [key_list[0:4], key_list[4:8], key_list[8:12]]
    g = []
    R = 1
    for i in range(1, 4):
        s = 0
        for j in range(1, 5):
            s += G[i - 1][j - 1] * (10 ** (-j))
        g.append(s)
        R = (R * s) % 1

    L_x = (R + key_list[12] / 256) % 1
    S_x = round(((g[0] + g[1] + g[2]) * (10 ** 4) + L_x * (10 ** 4)) % 256)
    V1 = sum(key_list)
    V2 = key_list[0]
    for i in range(1, 13):
        V2 = V2 ^ key_list[i]
    V = V2 / V1

    L_y = (V + key_list[12] / 256) % 1
    S_y = round((V + V2 + L_y * 10 ** 4) % 256)
    C1_0 = S_x
    C2_0 = S_y

    C = round((L_x * L_y * 10 ** 4) % 256)
    I_prev = C
    I_prev_r = C
    I_prev_g = C
    I_prev_b = C
    I = C
    I_r = C
    I_g = C
    I_b = C
    x_prev = 4 * (S_x) * (1 - S_x)
    y_prev = 4 * (L_x) * (1 - S_y)
    x = x_prev
    y = y_prev
    imageMatrix, dimension, color = getImageMatrix(imageName)

    henonDecryptedImage = []
    for i in range(dimension):
        row = []
        for j in range(dimension):
            while x < 0.8 and x > 0.2:
                x = 4 * x * (1 - x)
                if x == 0.75:
                    break
            while y < 0.8 and y > 0.2:
                y = 4 * y * (1 - y)
                if y == 0.75:
                    break
            x_round = round((x * (10 ** 4)) % 256)
            y_round = round((y * (10 ** 4)) % 256)
            C1 = x_round ^ ((key_list[0] + x_round) % N) ^ ((C1_0 + key_list[1]) % N)
            C2 = x_round ^ ((key_list[2] + y_round) % N) ^ ((C2_0 + key_list[3]) % N)
            if color:
                I_r = ((((key_list[4] + C1) % N) ^ ((key_list[5] + C2) % N) ^ ((I_prev_r + key_list[7]) % N) ^
                        imageMatrix[i][j][0]) + N - key_list[6]) % N
                I_g = ((((key_list[4] + C1) % N) ^ ((key_list[5] + C2) % N) ^ ((I_prev_g + key_list[7]) % N) ^
                        imageMatrix[i][j][1]) + N - key_list[6]) % N
                I_b = ((((key_list[4] + C1) % N) ^ ((key_list[5] + C2) % N) ^ ((I_prev_b + key_list[7]) % N) ^
                        imageMatrix[i][j][2]) + N - key_list[6]) % N
                I_prev_r = imageMatrix[i][j][0]
                I_prev_g = imageMatrix[i][j][1]
                I_prev_b = imageMatrix[i][j][2]
                row.append((I_r, I_g, I_b))
                x = (x + imageMatrix[i][j][0] / 256 + key_list[8] / 256 + key_list[9] / 256) % 1
                y = (x + imageMatrix[i][j][0] / 256 + key_list[8] / 256 + key_list[9] / 256) % 1
            else:
                I = ((((key_list[4] + C1) % N) ^ ((key_list[5] + C2) % N) ^ ((I_prev + key_list[7]) % N) ^
                      imageMatrix[i][j]) + N - key_list[6]) % N
                I_prev = imageMatrix[i][j]
                row.append(I)
                x = (x + imageMatrix[i][j] / 256 + key_list[8] / 256 + key_list[9] / 256) % 1
                y = (x + imageMatrix[i][j] / 256 + key_list[8] / 256 + key_list[9] / 256) % 1
            for ki in range(12):
                key_list[ki] = (key_list[ki] + key_list[12]) % 256
                key_list[12] = key_list[12] ^ key_list[ki]
        henonDecryptedImage.append(row)
    if color:
        im = Image.new("RGB", (dimension, dimension))
    else:
        im = Image.new("L", (dimension, dimension))  # L is for Black and white pixels
    pix = im.load()
    for x in range(dimension):
        for y in range(dimension):
            pix[x, y] = henonDecryptedImage[x][y]
    im.save(imageName.split('_')[0] + "_Decryption.png", "PNG")
    print("Image saved.")

def LogisticDecryption(imageName, key):
    N = 256
    key_list = [ord(x) for x in key]

    G = [key_list[0:4], key_list[4:8], key_list[8:12]]
    g = []
    R = 1
    for i in range(1, 4):
        s = 0
        for j in range(1, 5):
            s += G[i - 1][j - 1] * (10 ** (-j))
        g.append(s)
        R = (R * s) % 1

    L_x = (R + key_list[12] / 256) % 1
    S_x = round(((g[0] + g[1] + g[2]) * (10 ** 4) + L_x * (10 ** 4)) % 256)
    V1 = sum(key_list)
    V2 = key_list[0]
    for i in range(1, 13):
        V2 = V2 ^ key_list[i]
    V = V2 / V1

    L_y = (V + key_list[12] / 256) % 1
    S_y = round((V + V2 + L_y * 10 ** 4) % 256)
    C1_0 = S_x
    C2_0 = S_y

    C = round((L_x * L_y * 10 ** 4) % 256)
    I_prev = C
    I_prev_r = C
    I_prev_g = C
    I_prev_b = C
    I = C
    I_r = C
    I_g = C
    I_b = C
    x_prev = 4 * (S_x) * (1 - S_x)
    y_prev = 4 * (L_x) * (1 - S_y)
    x = x_prev
    y = y_prev
    imageMatrix, dimension, color = getImageMatrix(imageName)

    henonDecryptedImage = []
    for i in range(dimension):
        row = []
        for j in range(dimension):
            while x < 0.8 and x > 0.2:
                x = 4 * x * (1 - x)
            while y < 0.8 and y > 0.2:
                y = 4 * y * (1 - y)
            x_round = round((x * (10 ** 4)) % 256)
            y_round = round((y * (10 ** 4)) % 256)
            C1 = x_round ^ ((key_list[0] + x_round) % N) ^ ((C1_0 + key_list[1]) % N)
            C2 = x_round ^ ((key_list[2] + y_round) % N) ^ ((C2_0 + key_list[3]) % N)
            if color:
                I_r = ((((key_list[4] + C1) % N) ^ ((key_list[5] + C2) % N) ^ ((I_prev_r + key_list[7]) % N) ^
                        imageMatrix[i][j][0]) + N - key_list[6]) % N
                I_g = ((((key_list[4] + C1) % N) ^ ((key_list[5] + C2) % N) ^ ((I_prev_g + key_list[7]) % N) ^
                        imageMatrix[i][j][1]) + N - key_list[6]) % N
                I_b = ((((key_list[4] + C1) % N) ^ ((key_list[5] + C2) % N) ^ ((I_prev_b + key_list[7]) % N) ^
                        imageMatrix[i][j][2]) + N - key_list[6]) % N
                I_prev_r = imageMatrix[i][j][0]
                I_prev_g = imageMatrix[i][j][1]
                I_prev_b = imageMatrix[i][j][2]
                row.append((I_r, I_g, I_b))
                x = (x + imageMatrix[i][j][0] / 256 + key_list[8] / 256 + key_list[9] / 256) % 1
                y = (x + imageMatrix[i][j][0] / 256 + key_list[8] / 256 + key_list[9] / 256) % 1
            else:
                I = ((((key_list[4] + C1) % N) ^ ((key_list[5] + C2) % N) ^ ((I_prev + key_list[7]) % N) ^
                      imageMatrix[i][j]) + N - key_list[6]) % N
                I_prev = imageMatrix[i][j]
                row.append(I)
                x = (x + imageMatrix[i][j] / 256 + key_list[8] / 256 + key_list[9] / 256) % 1
                y = (x + imageMatrix[i][j] / 256 + key_list[8] / 256 + key_list[9] / 256) % 1
            for ki in range(12):
                key_list[ki] = (key_list[ki] + key_list[12]) % 256
                key_list[12] = key_list[12] ^ key_list[ki]
        henonDecryptedImage.append(row)
    if color:
        im = Image.new("RGB", (dimension, dimension))
    else:
        im = Image.new("L", (dimension, dimension))  # L is for Black and white pixels
    pix = im.load()
    for x in range(dimension):
        for y in range(dimension):
            pix[x, y] = henonDecryptedImage[x][y]
    im.save(imageName.split('_')[0] + "_LogisticDec.png", "PNG")

if __name__ == '__main__':
    image_name = "images/mona_Encryption"
    extension = ".png"
    key = "01001101001111010010010111111000011011100011101110001101101001011111100111111001011000001010101010000000"

    #Encryption
    '''LogisticEncryption_Binary(image_name + extension, key)
    im1=cv2.imread(image_name+extension,0)
    im2=cv2.imread(image_name+"_Encryption"+".png",0)
    print(ssim(im1,im2))'''

    #Decryption
    LogisticDecryption_Binary(image_name + extension, key)