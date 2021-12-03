cimport numpy as np
from cython.operator import dereference


def compare_images(np.ndarray image1, np.ndarray image2):
    cdef unsigned char [:, :, :] i1 = image1
    cdef unsigned char [:, :, :] i2 = image2
    cdef int H = i1.shape[0]
    cdef int W = i1.shape[1]
    ret = _compare_images(i1, i2, H, W)
    return ret

cdef int _compare_images(
    unsigned char [:, :, :] i1,
    unsigned char [:, :, :] i2,
    int H, 
    int W
):
    cdef int y, x, z
    for y in range(H):
        for x in range(W):
            for z in range(3):
                if i1[y][x][z] != i2[y][x][z]:
                    return 0
    return 1

def compare_images_readonly(np.ndarray image1, np.ndarray image2):
    cdef const unsigned char [:, :, :] i1 = image1
    cdef unsigned char [:, :, :] i2 = image2
    cdef int H = i1.shape[0]
    cdef int W = i1.shape[1]
    ret = _compare_images_readonly(i1, i2, H, W)
    return ret

cdef int _compare_images_readonly(
    const unsigned char [:, :, :] i1,
    unsigned char [:, :, :] i2,
    int H, 
    int W
):
    cdef int y, x, z
    for y in range(H):
        for x in range(W):
            for z in range(3):
                if i1[y][x][z] != i2[y][x][z]:
                    return 0
    return 1


def find_first_template(np.ndarray tpl, np.ndarray src):
    cdef unsigned char [: ,:, :] t = tpl
    cdef const unsigned char [: ,:, :] i = src
    cdef int H = i.shape[0]
    cdef int W = i.shape[1]
    cdef int h = t.shape[0]
    cdef int w = t.shape[1]

    cdef unsigned int ret = 0

    ret = _compare(t, i, H, W, h, w)
    if ret == 0:
        return None
    else:
        y = ret >> 16
        x = ret - y*2**16
        y -= 1
        return x, y


cdef int _compare(
    unsigned char [:, :, :] t,
    const unsigned char [:, :, :] i,
    int H, int W, int h, int w
):
    cdef int h_range = H-h+1
    cdef int w_range = W-w+1
    cdef int y = 0
    cdef int x = 0
    cdef unsigned int ret = 0

    for y in range(h_range):
        for x in range(w_range):
            if _compare_win(t, i, y, x, h, w) == 1:
                ret = y + 1
                ret <<= 16
                ret += x
                return ret
    return 0

cdef int _compare_win(
    unsigned char [:, :, :] t,
    const unsigned char [:, :, :] i,
    int y, int x,
    int h, int w
):
    cdef int y0 = 0
    cdef int x0 = 0
    cdef int z0 = 0
    for y0 in range(h):
        for x0 in range(w):
            for z0 in range(3):
                if i[y+y0, x+x0, z0] != t[y0, x0, z0]:
                    return 0
    return 1
