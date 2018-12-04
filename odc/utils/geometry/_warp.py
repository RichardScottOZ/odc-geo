import rasterio.warp
import rasterio.crs
from affine import Affine

_WRP_CRS = rasterio.crs.CRS.from_epsg(3857)


def resampling_s2rio(name):
    """
    Convert from string to rasterio.warp.Resampling enum, raises ValueError on bad input.
    """
    try:
        return getattr(rasterio.warp.Resampling, name)
    except AttributeError:
        raise ValueError('Bad resampling parameter: {}'.format(name))


def warp_affine_rio(src, dst, A, resampling, **kwargs):
    """
    Perform Affine warp using rasterio as backend library.

    :param        src: image as ndarray
    :param        dst: image as ndarray
    :param          A: Affine transformm, maps from dst_coords to src_coords
    :param resampling: str|rasterio.warp.Resampling resampling strategy

    **kwargs -- any other args to pass to ``rasterio.warp.reproject``

    :returns: dst
    """
    crs = _WRP_CRS
    src_transform = Affine.identity()
    dst_transform = A

    if isinstance(resampling, str):
        resampling = resampling_s2rio(resampling)

    dst0 = dst

    # TODO: GDAL doesn't support signed 8-bit values, so we coerce to uint8,
    # *BUT* this is only valid for nearest|mode resampling strategies, proper
    # way is to perform warp in int16 space and then convert back to int8 with
    # clamping.
    if dst.dtype.name == 'int8':
        dst = dst.view('uint8')
    if src.dtype.name == 'int8':
        src = src.view('uint8')

    rasterio.warp.reproject(src,
                            dst,
                            src_transform=src_transform,
                            dst_transform=dst_transform,
                            src_crs=crs,
                            dst_crs=crs,
                            resampling=resampling,
                            **kwargs)

    return dst0


def warp_affine(src, dst, A, resampling, **kwargs):
    """
    Perform Affine warp using best available backend (GDAL via rasterio is the only one so far).

    :param        src: image as ndarray
    :param        dst: image as ndarray
    :param          A: Affine transformm, maps from dst_coords to src_coords
    :param resampling: str resampling strategy

    **kwargs -- any other args to pass to implementation

    :returns: dst
    """
    return warp_affine_rio(src, dst, A, resampling, **kwargs)
