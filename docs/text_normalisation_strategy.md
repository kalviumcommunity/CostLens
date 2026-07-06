# Text Normalisation Strategy

## Overview
This document outlines the standardisation and cleaning rules applied to string fields in the Cloud Cost Intelligence dataset. Consistent text formatting is crucial for accurate aggregation, category mapping, and reporting.

## 1. Whitespace Rules
All string columns undergo whitespace trimming to remove invisible characters that often lead to duplicate categories.
- **Rule**: Strip leading and trailing whitespace.
- **Function**: `.str.strip()`
- **Example**: `" AWS "` becomes `"AWS"`

## 2. Case Standardisation Rules
To ensure consistent categorisation regardless of how the data was entered, all text fields are normalised to a standard casing format.
- **Rule**: Apply Title Case to all string values.
- **Function**: `.str.title()`
- **Example**: `"aws"`, `"AWS"`, `"aWs"` all become `"Aws"`

## 3. Regex Transformations (Special Character Removal)
Unwanted special characters can corrupt labels and cause issues in downstream processing or visualisations.
- **Rule**: Remove specific special characters (`@`, `#`, `$`, `%`, `&`, `*`, `!`).
- **Function**: `.str.replace(r'[@#\$%&\*!]', '', regex=True)`
- **Example**: `"AWS#Prod"` becomes `"AWSProd"`

## 4. Mapping Dictionary Logic (Label Standardisation)
After basic cleaning, specific business terms and categories are mapped to their official, standardised names.
- **Rule**: Replace known variants with standard category names using a predefined dictionary.
- **Mapping Logic**:
  ```python
  {
      "Aws": "Amazon Web Services",
      "Amazon Aws": "Amazon Web Services",
      "Amazon Web Srvices": "Amazon Web Services",
      "Gcp": "Google Cloud Platform",
      "Google Cloud": "Google Cloud Platform"
  }
  ```
- **Execution**: Apply the mapping after whitespace, regex, and casing normalisation to ensure maximal matching.
