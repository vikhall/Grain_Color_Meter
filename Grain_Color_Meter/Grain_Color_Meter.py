from matplotlib import pyplot as plt
import cv2
import numpy as np


def grain_Color_Meter(image: str, preproc_1: str = None, preproc_2: str = None, res_img: str = None) -> list:
    """
    Функция, которая измеряет цвет зерен
    :param image:
    :param preproc_1:
    :param preproc_2:
    :param res_img:
    :return:
    """
    img = cv2.imread(image)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Подготовка изображения, перед поиском контуров
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # удаление шумов
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    # гарантированные области фона
    sure_bg = cv2.dilate(opening, kernel, iterations=5)
    mask = sure_bg
    if preproc_1:
        plt.imshow(mask)
        plt.show()

    # Поиск контуров колосьев и запись их в список true_cnts
    cnts, h = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    true_cnts = []
    for i in range(len(cnts)):
        cnt = cnts[i]
        area = cv2.contourArea(cnt)
        if 1000 < area < 150000:  # Индекс контура
            true_cnts.append(cnt)

    # print(f'Количество контуров = {len(true_cnts)}')

    # Удаление из изображения всего кроме зерен
    mask = np.zeros(img.shape[:2], np.uint8)
    for i in range(len(true_cnts)):
        cv2.drawContours(mask, [true_cnts[i]], -1, 255, -1)
        dst = cv2.bitwise_and(rgb, rgb, mask=mask)
    if preproc_2:
        plt.imshow(dst)
        plt.show()

    # Измерение цвета при помощи алгоритма k-means
    Z = dst.reshape((-1, 3))
    Z = np.float32(Z)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = 2
    ret, label, center = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    center = np.uint8(center)
    color = list(filter(lambda x: x[:][:].all() != 0, center))[0].tolist()
    res = center[label.flatten()]
    res2 = res.reshape((img.shape))
    if res_img:
        plt.imshow(res2)
        plt.show()

    return color



