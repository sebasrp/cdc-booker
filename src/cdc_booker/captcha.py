import pytesseract
import argparse

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from subprocess import check_output


def resolve_1(path):
    return pytesseract.image_to_string(
        Image.open(path),
        config='--oem 3 --psm 7 -c tessedit_char_whitelist="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"',
    )


def resolve_2(path):
    im = Image.open(path)
    im = im.filter(ImageFilter.MedianFilter())
    enhancer = ImageEnhance.Contrast(im)
    im = enhancer.enhance(2)
    im = im.convert("1")
    im.save("captcha2.jpg")
    # config_string = "--psm 7"
    config_string = "--oem 1 --psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return pytesseract.image_to_string(Image.open("captcha2.jpg"), config=config_string)


def resolve_3(path):
    """https://stackoverflow.com/questions/37745519/use-pytesseract-ocr-to-recognize-text-from-an-image"""
    # Grayscale, Gaussian blur, Otsu's threshold
    image = cv2.imread(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Morph open to remove noise and invert image
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    invert = 255 - thresh
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    ero = cv2.erode(invert, kernel, iterations=3)
    cv2.imwrite("captcha3.jpg", ero)

    # Perform text extraction
    return pytesseract.image_to_string(ero, config="--psm 7")


def resolve_3_1(path):
    """https://stackoverflow.com/questions/68941358/unable-to-ocr-alphanumerical-image-with-tesseract/68942691#68942691"""
    # Grayscale, Gaussian blur, Otsu's threshold
    img = cv2.imread(path)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)

    cv2.imwrite("captcha3_1.jpg", img)

    # Perform text extraction
    return pytesseract.image_to_string(img, config="--psm 7")


def resolve_4(path):
    "https://stackoverflow.com/questions/61327857/how-to-extract-individual-letters-from-image-with-pytesseract"
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    items = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = items[0] if len(items) == 2 else items[1]

    img_contour = img.copy()
    for i in range(len(contours)):
        area = cv2.contourArea(contours[i])
        if 100 < area < 10000:
            cv2.drawContours(img_contour, contours, i, (0, 0, 255), 2)

    detected = ""
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        ratio = h / w
        area = cv2.contourArea(c)
        base = np.ones(thresh.shape, dtype=np.uint8)
        if ratio > 0.9 and 100 < area < 10000:
            base[y : y + h, x : x + w] = thresh[y : y + h, x : x + w]
            segment = cv2.bitwise_not(base)

            custom_config = r'-l eng --oem 3 --psm 10 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ" '
            c = pytesseract.image_to_string(segment, config=custom_config)
            print(c)
            detected = detected + c
            cv2.imshow("segment", segment)
            cv2.waitKey(0)
    cv2.imwrite("captcha4.jpg", img_contour)
    print("detected: " + detected)


def resolve_5(path):
    """https://stackoverflow.com/questions/61224108/tesseract-ocr-not-recognizing-multiple-characters-in-a-single-image"""
    img = cv2.imread(path)
    cv2.imshow("original", img)

    # turn into gray for next processing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV * cv2.THRESH_OTSU)[1]
    thresh = cv2.bitwise_not(thresh)

    # dilate to make the line thicker
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 12))
    dilation = cv2.dilate(thresh, kernel, iterations=1)

    # find the contour
    cntrs = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cntrs = cntrs[0] if len(cntrs) == 2 else cntrs[1]

    result = img.copy()
    for c in cntrs:
        # for each letter, create red rectangle
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(result, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # prepare letter for OCR
        box = thresh[y : y + h - 2, x : x + w]
        box = cv2.bitwise_not(box)
        box = cv2.GaussianBlur(box, (3, 3), 0)

        # retreive the angle. For the meaning of angle, see below
        # https://namkeenman.wordpress.com/2015/12/18/open-cv-determine-angle-of-rotatedrect-minarearect/
        rect = cv2.minAreaRect(c)
        angle = rect[2]

        # put angle below letter
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (x, y + h + 20)
        fontScale = 0.6
        fontColor = (255, 0, 0)
        lineType = 2
        cv2.putText(
            result,
            str(angle),
            bottomLeftCornerOfText,
            font,
            fontScale,
            fontColor,
            lineType,
        )

        # do the OCR
        custom_config = r"-l eng --oem 3 --psm 10"
        text = pytesseract.image_to_string(box, config=custom_config)
        print("Detected :" + text + ", angle: " + str(angle))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("path", help="Captcha file path")
    args = argparser.parse_args()
    path = args.path
    print("Resolving Captcha")
    captcha_text = resolve_5(path)
    print("Extracted Text", captcha_text)
