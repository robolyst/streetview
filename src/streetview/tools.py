from PIL import Image


def get_pixel_from_bw_image(img: Image.Image, x: int, y: int) -> float:
    """
    Get the pixel value from a black and white image.
    """
    bw_img = img.convert("L")
    pixel = bw_img.getpixel((x, y))
    if pixel is None or isinstance(pixel, tuple):
        raise ValueError("Invalid pixel value")
    return pixel


def crop_bottom_and_right_black_border(img: Image.Image) -> Image.Image:
    """
    Crop the black border at the bottom and right of the panorama.
    When you download streetviews get_panorama(), it's common to see
    black borders at the bottom and right of the image. This is because
    he dimensions of the panorama are not always correct / multiple of
    512, a common issue with user-contributed panoramas.

    The implementation is not perfect, but it works for most cases.
    """
    (width, height) = img.size
    bw_img = img.convert("L")
    black_luminance = 4

    # Find the bottom of the panorama
    pixel_cursor = (0, height - 1)
    valid_max_y = height - 1
    while pixel_cursor[0] < width and pixel_cursor[1] >= 0:
        pixel_color = get_pixel_from_bw_image(bw_img, *pixel_cursor)

        if pixel_color > black_luminance:
            # Found a non-black pixel
            # Double check if all the pixels below this one are black
            all_pixels_below = list(
                bw_img.crop((0, pixel_cursor[1] + 1, width, height)).getdata()
            )
            all_black = True
            for pixel in all_pixels_below:
                if pixel > black_luminance:
                    all_black = False

            if all_black:
                valid_max_y = pixel_cursor[1]
                break
            else:
                # A false positive, probably the actual valid bottom pixel is
                # very close to black Reset the cursor to the next vertical
                # line to the right
                pixel_cursor = (pixel_cursor[0] + 1, height - 1)

        else:
            pixel_cursor = (pixel_cursor[0], pixel_cursor[1] - 1)

    # Find the right of the panorama
    pixel_cursor = (width - 1, 0)
    valid_max_x = width - 1
    while pixel_cursor[1] < height and pixel_cursor[0] >= 0:
        pixel_color = get_pixel_from_bw_image(bw_img, *pixel_cursor)

        if pixel_color > black_luminance:
            # Found a non-black pixel
            # Double check if all the pixels to the right of this one are black
            all_pixels_to_the_right = list(
                bw_img.crop((pixel_cursor[0] + 1, 0, width, height)).getdata()
            )
            all_black = True
            for pixel in all_pixels_to_the_right:
                if pixel > black_luminance:
                    all_black = False
            if all_black:
                valid_max_x = pixel_cursor[0]
                break
            else:
                # A false positive, probably the actual valid right pixel
                # is very close to black Reset the cursor to the next
                # horizontal line below
                pixel_cursor = (width - 1, pixel_cursor[1] + 1)

        else:
            pixel_cursor = (pixel_cursor[0] - 1, pixel_cursor[1])

    valid_height = valid_max_y + 1
    valid_width = valid_max_x + 1

    if valid_height == height and valid_width == width:
        # No black border found
        return img

    print(
        "Found black border."
        f" Cropping from {width}x{height} to {valid_width}x{valid_height}"
    )
    return img.crop((0, 0, valid_width, valid_height))
