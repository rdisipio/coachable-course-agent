# ESCO Skill Dataset Instructions

This folder is expected to contain a local export of the ESCO skills dataset.

To download the data:

1. Visit the official ESCO portal: https://esco.ec.europa.eu/en/download
2. Download the CSV version of the dataset (ESCO v1.2 or later).
3. Extract the archive. Make sure it contains a file called `skills_en.csv` file.

Only the relevant skill fields are needed: `conceptUri`, `preferredLabel`.

This file is used to normalize skills mentioned in user goals, preferences, and course metadata.
