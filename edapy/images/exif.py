#!/usr/bin/env python

"""Obtaining and parsing EXIF data from images."""

# 3rd party modules
from PIL.ExifTags import TAGS, GPSTAGS


def get_exif_data(image):
    """
    Extract and parse EXIF data from an image.

    Paramters
    ---------
    image : PIL object

    Returns
    -------
    exif_data : dict
    """
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == 'GPSInfo':
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
                exif_data[decoded] = gps_data
                lat, lon = get_lat_lon(exif_data)
                if not (-180.0 <= lat <= 180.0):
                    lat = None
                if not (-180.0 <= lon <= 180.0):
                    lon = None
                exif_data['latitude'] = lat
                exif_data['longitude'] = lon
            else:
                exif_data[decoded] = value
    return exif_data


def _get_if_exist(data, key):
    if key in data:
        return data[key]

    return None


def _convert_to_degress(value):
    """
    Convert the GPS coordinates in the EXIF to degress in float format.

    Source: https://gist.github.com/erans/983821/
    ... cce3712b82b3de71c73fbce9640e25adef2b0392

    Parameters
    ----------
    value : tuple
    """
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)


def get_lat_lon(exif_data):
    """
    Return the latitude and longitude, if available, from exif_data.

    Parameters
    ----------
    exif_data : dict

    Returns
    -------
    lat, long : tuple
    """
    lat = None
    lon = None

    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]

        gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
        gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
        gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')

        has_gps_data = (gps_latitude and gps_latitude_ref and
                        gps_longitude and gps_longitude_ref)

        if has_gps_data:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":
                lat = 0 - lat

            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon

    return lat, lon
