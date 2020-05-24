# simple-image-debayer
Simple library for debayering images with OpenCV.

See the Wikipedia article on the [Bayer filter](https://en.wikipedia.org/wiki/Bayer_filter)
for more information.


## Installation

```commandline
pip install simple-image-debayer
```

## Usage

### Command-line

You can use the `sid-debayer` command-line tool for debayering directories:

```
usage: sid-debayer [-h] -i DIR [-I EXT] [-r] [-o DIR] [-O EXT] [-c PROFILE]
                   [-p NUM] [-v] [-n]

Debayers images in a directory.

optional arguments:
  -h, --help            show this help message and exit
  -i DIR, --input_dir DIR
                        the directory to process
  -I EXT, --input_ext EXT
                        the extension to look for in the input directory
  -r, --recursive       whether to look for images recursively
  -o DIR, --output_dir DIR
                        the directory to store the debayered images in;
                        performs in-place debayering if not specified
  -O EXT, --output_ext EXT
                        the extension to use for the generated images
  -c PROFILE, --color_profile PROFILE
                        the OpenCV color profile to use for debayering
                        (cv2.COLOR_BAYER_*)
  -p NUM, --progress_interval NUM
                        the interval of processed images to output progress
                        information in the console
  -v, --verbose         whether to be more verbose in the output
  -n, --dry_run         whether to perform a dry-run; --verbose should be used
                        in conjunction with this flag
```

### Python

Of course, the library can be used as a Python library as well.

The module `sid.debayer` contains the following methods:

* `debayer` - for debayering a directory
* `debayer_image` - for debayering a single image
