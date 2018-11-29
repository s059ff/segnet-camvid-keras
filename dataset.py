import glob
import os

import numpy as np

import cv2


def load(folder='train'):

    # Load dataset.
    originals = []
    annotations = []
    for filename in map(lambda path: os.path.basename(path), glob.glob(f'./dataset/{folder}/*.png')):
        path1 = f'./dataset/{folder}/' + filename
        path2 = f'./dataset/{folder}annot/' + filename

        if not os.path.exists(path1):
            raise Exception(f'{path1} is not found.')
        if not os.path.exists(path2):
            raise Exception(f'{path2} is not found.')

        def split(image):
            # Split region 3x2.
            yield image[0:128, 0:128]
            yield image[0:128, 160:160 + 128]
            yield image[0:128, 320:320 + 128]
            yield image[180:180 + 128, 0:128]
            yield image[180:180 + 128, 160:160 + 128]
            yield image[180:180 + 128, 320:320 + 128]

        def crop(image, interpolation):
            h, w, *d = image.shape
            x = w // 2
            image = image[:, x - h // 2:x + h // 2]
            image = cv2.resize(
                src=image,
                dsize=(128, 128),
                interpolation=interpolation)
            yield image

        image = cv2.imread(path1)
        # images = split()
        images = crop(image, cv2.INTER_LINEAR)
        for image in images:
            image[:, :, 0] = cv2.equalizeHist(image[:, :, 0])
            image[:, :, 1] = cv2.equalizeHist(image[:, :, 1])
            image[:, :, 2] = cv2.equalizeHist(image[:, :, 2])
            image = image.astype(np.float) / 255.
            originals.append(image)

        image = cv2.imread(path2)[:, :, 0]
        # images = split()
        images = crop(image, cv2.INTER_NEAREST)
        for image in images:
            label = 8
            positive = np.where(image == label, 1, 0)
            negative = 1 - positive
            annotation = np.dstack((negative, positive))
            annotations.append(annotation)

    originals = np.array(originals, dtype=np.float)
    annotations = np.array(annotations, dtype=np.float)

    # For debug.
    # N = 10
    # for i, x in zip(range(N), originals[:N]):
    #     cv2.imwrite(f'./temp/original-{i}.png', x * 255)
    # for i, y in zip(range(N), map(lambda image: image[:, :, 1], annotations[:N])):
    #     cv2.imwrite(f'./temp/annotation-{i}.png', y * 255)

    return (originals, annotations)
