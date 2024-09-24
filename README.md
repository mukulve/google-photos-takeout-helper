# Google Photos Takeout Helper

This Python script helps process and organize Google Photos takeout data by adding metadata to images and moving them to a designated folder.

## Table of Contents

- [About](#about)
- [Features](#features)
- [Usage](#usage)
- [Requirements](#requirements)
- [Contributing](#contributing)

## About

The Google Photos Takeout Helper is designed to process Google Photos takeout data by extracting relevant information from JSON files and applying it as metadata to corresponding image files. It also organizes these files into a specified folder structure.

## Features

- Extracts metadata from Google Photos JSON files
- Adds GPS coordinates, camera model, and creation date to image metadata
- Generates unique filenames for processed images
- Moves processed images to a designated folder
- Handles both JPEG and video files

## Usage

1. Clone the repository
2. Install required dependencies
3. run the script
   
## Requirements

- `Python`
- `piexif` 
- `shutil` 
- `glob` 
- `json` 
- `os` 
- `fractions` 
- `uuid` 

## Contributing

Contributions are welcome! Please feel free to submit pull requests or issues.

