import argparse
import datetime
import os
import cv2
import traceback


def check_color_profile(color_profile):
    """
    Checks whether the color profile is valid. Raises an Exception if not valid.

    :param color_profile: the color profile to check (cv2.COLOR_BAYER_*)
    :type color_profile: str
    """
    if not color_profile.startswith("COLOR_BAYER_"):
        raise Exception("Unexpected profile '%s', should have started with 'COLOR_BAYER_'" % color_profile)
    try:
        eval("cv2.%s" % color_profile)
    except:
        raise Exception("Invalid color profile '%s'?" % color_profile)


def eval_color_profile(color_profile):
    """
    Evaluates the color profile string, returning the cv2 integer constant. Raises an Exception if not valid.

    :param color_profile: the color profile
    :type color_profile: str
    :return: the color profile integer constant
    :rtype: int
    """
    check_color_profile(color_profile)
    return eval("cv2.%s" % color_profile)


def check_params(input_dir, output_dir, color_profile):
    """
    Performs checks on the parameters and raises an Exception if not valid.

    :param input_dir: the input directory
    :type input_dir: str
    :param output_dir: the output directory
    :type output_dir: str
    :param color_profile: the color profile to check (cv2.COLOR_BAYER_*)
    :type color_profile: str
    """
    check_color_profile(color_profile)
    if not os.path.exists(input_dir) or not os.path.isdir(input_dir):
        raise Exception("Input directory '%s' does not exist or not a directory!" % input_dir)
    if output_dir is not None:
        if not os.path.exists(output_dir) or not os.path.isdir(output_dir):
            raise Exception("Output directory '%s' does not exist or not a directory!" % input_dir)


def calculate_remaining_time(start, processed, total):
    """
    Generates the number of seconds the processing will still take.

    :param start: the start time
    :type start: datetime.dateime
    :param processed: the number of images processed so far
    :type processed: int
    :param total: the total number of images to process
    :type total: int
    :return: the time still left for finishing the remainder of the files
    :rtype: datetime.timedelta
    """

    now = datetime.datetime.now()
    per_image = (now - start) / processed
    return (total - processed) * per_image


def read_image(input):
    """
    Reads the raw image.

    :param input: the image file to read
    :type input: str
    :return: the image
    :rtype: ndarray
    """
    return cv2.imread(input, cv2.IMREAD_GRAYSCALE | cv2.IMREAD_ANYDEPTH)


def write_image(img, output):
    """
    Writes the image object to the specified output file.

    :param img: the image to write to disk
    :type img: ndarray
    :param output: the file to write to
    :type output: str
    """
    cv2.imwrite(output, img)


def debayer_image(img, color_profile):
    """
    Debayers the image using the specified profile.

    :param img: the image to debayer
    :type img: ndarray
    :param color_profile: the color profile to use (cv2.COLOR_BAYER_*)
    :type color_profile: int
    :return: the debayered image
    :rtype: ndarray
    """
    return cv2.cvtColor(img, color_profile)


def debayer_file(input, output, color_profile):
    """
    Debayers a single image file using the specified color profile and writes it to the supplied output file.

    :param input: the input image to debayer
    :type input: str
    :param output: the output image to write
    :type output: str
    :param color_profile: the color profile to use (cv2.COLOR_BAYER_*)
    :type color_profile: int
    """

    raw = read_image(input)
    rgb = debayer_image(raw, color_profile)
    write_image(rgb, output)


def debayer_dir(input_dir, input_ext="bmp", output_dir=None, output_ext="jpg", recursive=False,
                color_profile="COLOR_BAYER_BG2BGR", verbose=False, dry_run=False, progress_interval=100,
                delete=False, ignore_errors=False):
    """
    Debayers the images in the directory.

    :param input_dir: the directory to look for images to debayer
    :type input_dir: str
    :param input_ext: the extension to look for (no dot, default: bmp)
    :type input_ext: str
    :param output_dir: the directory to store the debayered images in, in-place conversion if None
    :type output_dir: str
    :param output_ext: the extension to use for the debayered images (no dot, defaultL jpg)
    :type output_ext: str
    :param recursive: whether to look for images recursively or not
    :type recursive: bool
    :param color_profile: the color profile to apply (cv2.COLOR_BAYER_*)
    :type color_profile: str
    :param verbose: whether to be more verbose with the processing (outputs dirs and progress indicator)
    :type verbose: bool
    :param verbose: whether to perform a dry-run, i.e., not actually convert any images
    :type verbose: bool
    :param progress_interval: the number of images to output progress information
    :type progress_interval: int
    :param delete: whether to delete the original file after successfully debayering it
    :type delete: bool
    :param ignore_errors: whether to ignore errors and keep debayering rather than raising exceptions
    :type ignore_errors: bool
    """

    # sanity checks
    check_params(input_dir, output_dir, color_profile)
    profile = eval_color_profile(color_profile)

    # determine input directories
    directories = []
    if recursive:
        for root, dirs, _ in os.walk(input_dir):
            for dir in dirs:
                full_dir = os.path.join(root, dir)
                directories.append(full_dir)
    else:
        directories.append(input_dir)

    # determine total number of images
    total = 0
    for dir in directories:
        files = [x for x in os.listdir(dir) if x.endswith("." + input_ext)]
        total += len(files)
    print("Total images to debayer: %d" % total)

    # convert images
    start = datetime.datetime.now()
    current = 0
    for dir in directories:
        files = [x for x in os.listdir(dir) if x.endswith("." + input_ext)]
        if verbose:
            print("%s: %d" % (dir, len(files)))

        for f in files:
            current += 1
            infile = os.path.join(dir, f)
            if output_dir is None:
                outfile = os.path.join(dir, f.replace("." + input_ext, "." + output_ext))
            else:
                outfile = os.path.join(output_dir, f.replace("." + input_ext, "." + output_ext))

            if not dry_run:
                try:
                    debayer_file(infile, outfile, profile)
                    if delete:
                        try:
                            os.remove(infile)
                        except Exception as e2:
                            print("Error deleting file: %s" % infile)
                            if ignore_errors:
                                print(traceback.format_exc())
                            else:
                                raise e2
                except Exception as e1:
                    print("Error debayering file: %s" % infile)
                    if delete:
                        print("Skipping deletion of file: %s" % infile)
                    if ignore_errors:
                        print(traceback.format_exc())
                    else:
                        raise e1

            if current % progress_interval == 0:
                print("Progress: %d / %d - ETA %s" % (current, total, str(calculate_remaining_time(start, current, total))))

    print("Total processing time: %s" % (datetime.datetime.now() - start))


def main(args=None):
    """
    Performs the debayering.
    Use -h to see all options.

    :param args: the command-line arguments to use, uses sys.argv if None
    :type args: list
    """

    parser = argparse.ArgumentParser(
        description='Debayers images in a directory.',
        prog="sid-debayer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input_dir", dest="input_dir", metavar="DIR", required=True, help="the directory to process")
    parser.add_argument("-I", "--input_ext", dest="input_ext", metavar="EXT", required=False, default="bmp", help="the extension to look for in the input directory")
    parser.add_argument("-r", "--recursive", action="store_true", dest="recursive", help="whether to look for images recursively")
    parser.add_argument("-o", "--output_dir", dest="output_dir", metavar="DIR", required=False, default=None, help="the directory to store the debayered images in; performs in-place debayering if not specified")
    parser.add_argument("-O", "--output_ext", dest="output_ext", metavar="EXT", required=False, default="jpg", help="the extension to use for the generated images")
    parser.add_argument("-c", "--color_profile", dest="color_profile", metavar="PROFILE", required=False, default="COLOR_BAYER_BG2BGR", help="the OpenCV color profile to use for debayering (cv2.COLOR_BAYER_*)")
    parser.add_argument("-p", "--progress_interval", dest="progress_interval", metavar="NUM", required=False, default=100, type=int, help="the interval of processed images to output progress information in the console")
    parser.add_argument("-e", "--ignore_errors", action="store_true", dest="ignore_errors", help="whether to ignore any errors and keep debayering")
    parser.add_argument("-d", "--delete", action="store_true", dest="delete", help="whether to delete the input file after successfully debayering it")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", help="whether to output directories being processed")
    parser.add_argument("-n", "--dry_run", action="store_true", dest="dry_run", help="whether to perform a dry-run; --verbose should be used in conjunction with this flag")
    parsed = parser.parse_args(args=args)
    debayer_dir(parsed.input_dir, input_ext=parsed.input_ext,
                output_dir=parsed.output_dir, output_ext=parsed.output_ext,
                recursive=parsed.recursive, verbose=parsed.verbose, dry_run=parsed.dry_run,
                progress_interval=parsed.progress_interval, delete=parsed.delete, ignore_errors=parsed.ignore_errors)


def sys_main():
    """
    Runs the main function using the system cli arguments, and
    returns a system error code.

    :return: 0 for success, 1 for failure.
    :rtype: int
    """

    try:
        main()
        return 0
    except Exception:
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc())
