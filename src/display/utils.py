from .cutils import compare_images as c_compare_images
from .cutils import compare_images_readonly


def compare_images(image1, image2):
    if image1.shape != image2.shape:
        return False
    if image1.flags['WRITEABLE'] and image2.flags['WRITEABLE']:
        ret = c_compare_images(image1, image2)
    elif image1.flags['WRITEABLE'] and not image2.flags['WRITEABLE']:
        ret = compare_images_readonly(image2, image1)
    elif not  image1.flags['WRITEABLE'] and image2.flags['WRITEABLE']:
        ret = compare_images_readonly(image1, image2)
    else:
        raise Exception('bad args')
    return bool(ret)

