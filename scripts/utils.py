import cv2


def load_mask(fpath, thresh=127):
    mask = cv2.imread(fpath, cv2.IMREAD_GRAYSCALE)
    _, binary_mask = cv2.threshold(mask, thresh=thresh, maxval=255, type=cv2.THRESH_BINARY)
    return binary_mask
