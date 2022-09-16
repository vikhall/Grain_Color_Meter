from matplotlib import pyplot as plt
import cv2
import numpy as np


def prerpoc(img: str, open_iter: int = 1, bg_iter: int = 5, preproc_1: str = None):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Подготовка изображения, перед поиском контуров
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # удаление шумов
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=open_iter)
    # гарантированные области фона
    sure_bg = cv2.dilate(opening, kernel, iterations=bg_iter)
    mask = sure_bg
    if preproc_1:
        plt.imshow(mask)
        plt.show()

    return mask


def is_contour_rectangle(c):
    # Определение того, является ли контур квадратным
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)

    return len(approx) == 4


def grain_contour_find(mask):
    # Поиск контуров колосьев и запись их в список true_cnts
    cnts, h = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    true_cnts = []
    for i in range(len(cnts)):
        if not is_contour_rectangle(cnts[i]):
            true_cnts.append(cnts[i])

    return true_cnts


def delete_all_but_grains(img, true_cnts, preproc_2: str = None):
    # Удаление из изображения всего кроме зерен
    mask = np.zeros(img.shape[:2], np.uint8)
    for i in range(len(true_cnts)):
        cv2.drawContours(mask, [true_cnts[i]], -1, 255, -1)
        dst = cv2.bitwise_and(img, img, mask=mask)
    if preproc_2:
        plt.imshow(dst)
        plt.show()

    return dst


def color_meter(dst, img, k: int, res_img: str = None):
    # Измерение цвета при помощи алгоритма k-means
    m = dst.reshape((-1, 3))
    m = np.float32(m)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret, label, center = cv2.kmeans(m, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    center = np.uint8(center)
    color = list(filter(lambda x: x[:][:].all() != 0, center))[0].tolist()
    res = center[label.flatten()]
    res2 = res.reshape(img.shape)
    if res_img:
        plt.imshow(res2)
        plt.show()

    return color


def measure_color(image: str, preproc_1: str = None, preproc_2: str = None, res_img: str = None,
                  open_iter: int = 1, bg_iter: int = 4, k: int = 2) -> list:
    """
    This function measures the color of the grains in the petri dish.
    :param image: Image of the grains in the petri dish. In addition to a petri dish with grains, only rectangular
    objects (for example, a colorchecker) can be present in the photo.
    :param preproc_1: If True (or any string), preprocessed photo 1 (after deleting background) will be shown.
    :param preproc_2: It True (or any string), preprocessed photo 2 (after deleting all but grains) will be shown.
    :param res_img: If True (or any string), final photo (with grains in only one, main color that will be returned)
    will be shown.
    :param open_iter: The number of cv2.morphologyEx iterations (default 4)
    :param bg_iter: The number of cv2.dilate iterations (default 2)
    :param k: The number of cluster to find using k-means algorithm
    :return: list containing color in RGB
    """
    img = cv2.imread(image)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    mask = prerpoc(img,  open_iter, bg_iter, preproc_1)

    true_cnts = grain_contour_find(mask)

    dst = delete_all_but_grains(rgb, true_cnts, preproc_2)

    color = color_meter(dst, img, k, res_img)

    return color
