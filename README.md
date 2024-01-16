<h1 align="center">CL Search </h1>
<p align="center" style="font-size: large;">Get <strong>everything</strong> from Craigslist</p>
<br>

## Table of contents
- [Features](#features)
- [Installation](#installation)
- [Commands](#Commands)
    - [Location](#location)
    - [Output](#output)
    - [Browser](#browser)
    - [Headless Mode](#headless)
    - [Search](#search)
    - [image](#image)

## Features
- Supports Chrome, Chromium, Edge, Firefox, & Safari
- Supports all Craigslist locations!
- Customize your desired locations in `locations.py`
- Supports a variety of formats to export data!
- Supports headless mode in all browsers!

## Installation

**Building from source**
```
gh repo clone gavink97/cl-search .
pip install --no-cache-dir -r requirements.txt
```

## Commands

### Location

**Location is a required flag**

Supports URLs, City Names, States, Provinces, Countries, Continents, or Craigslist!

`-L or --location foo`

<br>

Examples:

`-L 'New York'`

`-L https://austin.craigslist.org`


🦅 Use Lower 48 to search thru the Contiguous US 🦅

`-L 'Lower 48'`

You can customize locations by appending to the end of the dict in `locations.py`


### Output

**Defaults to CSV**

Supports many different formats!
- csv
- json
- html
- LaTex #requires Jinja2
- xml
- excel
- hdf5
- feather
- parquet
- orc
- stata
- pickle
- clipboard

SQL support coming soon

<br>

**Output:**

`-o or --output foo`

Simply type in the name of the format

`-o json`

or just use the extension for ease of use!

`-o xlsx`

<br>

**Export directly to clipboard!**

*Linux users may need to install xclip or xsel (with PyQt5, PyQt4 or qtpy) for use*

`-o clipboard`

### Browser

**Defaults to Firefox**

Supports Chrome, Chromium, Edge, Firefox, & Safari

`-b or --browser foo`


### Headless

**False by Default**

Supports Headless mode in all major browsers!

`--headless`

### Search

**No Default / Not Required**

Query a search or take every listing!

`-s foo`

`-s or --search 'foo bar'`

### Image

**False by Default**

Downloads images from the listings

`-i or --image`
