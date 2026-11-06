# Phone Number Inspector

A Persian-friendly desktop application for checking phone-number formats and public numbering-plan metadata. Numbers are processed locally with the `phonenumbers` library and are never sent to a service or server.

## Features

- Checks number validity and whether its length is possible
- Accepts Persian, Arabic, and Western digits, as well as common phone-number punctuation
- Lets you select a default region for numbers without a country code (Iran is selected by default)
- Displays the country calling code, likely region, line type, possible time zones, and carrier metadata when available
- Shows national, international, and E.164 formats, with an option to copy the E.164 number
- Supports Enter to analyze and Ctrl+L to clear the form
- Works offline after its dependency has been installed

## Requirements

- Python 3.10 or later
- Tkinter (included with the standard Python installer on Windows in most cases)

## Install and run

Create a virtual environment in the project directory:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Then install the dependency and start the app:

```bash
python -m pip install -r requirements.txt
python app.py
```

## Usage

Enter a phone number and choose a default region for national-format numbers. The default region is Iran. Numbers prefixed with `+` and a country calling code are parsed independently of the selected default region.

Examples:

- Iranian national format: `09121234567`
- International format: `+989121234567`

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## Project structure

```text
app.py                         Tkinter desktop interface
phone_inspector.py             Number parsing and metadata
tests/test_phone_inspector.py  Focused unit tests
requirements.txt               Python dependencies
```

## Limitations and privacy

- A valid result means that the number matches a recognized numbering plan. It does not confirm that the number is active or belongs to a particular person.
- Region, line type, time zone, and carrier (when available) are numbering-plan metadata. They may be incomplete or out of date; number portability can also make carrier information inaccurate.
- The displayed region is not the subscriber's live or precise location. A phone number cannot reveal a street address, current location, or subscriber identity.
- The app does not perform live lookups, send messages, access contacts, or keep a search history. A number is held in the local process while you use the app and is not transmitted over the network.
- Once the library is installed, parsing and validation are performed locally. Internet access is needed to download or update the dependency during installation.
