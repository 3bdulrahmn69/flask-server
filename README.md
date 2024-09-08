# License Management Server

## Description

A simple Flask-based server that provides functionality for managing license keys. This server supports checking the validity of license keys, adding new keys, and deleting existing keys. It uses SQLite for storage and supports endpoints to interact with the license data.

## Features

- **Check License**: Verify if a license key is valid or expired.
- **Add License**: Generate and add a new license key with an expiration date and name.
- **Delete License**: Remove an existing license key from the database.

## API Endpoints

### Check License

- **URL:** `/check-license`
- **Method:** `POST`
- **Request Body:**

  ```json
  {
    "key": "AAAA-1111-BBBB-2222"
  }
  ```

### Add License

- **URL:** `/add-license`
- **Method:** `POST`
- **Request Body:**

  ```json
  {
    "name": "John Doe",
    "expiration_date": "2022-12-31"
  }
  ```

### Delete License

- **URL:** `/delete-license`
- **Method:** `DELETE`
- **Request Body:**

  ```json
  {
    "key": "AAAA-1111-BBBB-2222"
  }
  ```
