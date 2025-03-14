# README.md

# Flask Domain Checker

This project is a Flask application that allows users to check the MX records of domain names. Users can input a single domain name or upload a CSV file containing multiple domain names. The application checks if the domain names are using Google MX records and provides feedback accordingly.

## Features

- Input a single domain name or upload a CSV file for bulk domain names.
- Limit of 20 domain names for bulk upload; an error message will be displayed if the limit is exceeded.
- Check MX records for the entered domain names.
- Feedback on whether Google Workspace is found for the domain names.

## Project Structure

```
flask-domain-checker
├── static
│   └── css
│       └── style.css
├── templates
│   └── index.html
├── app.py
├── requirements.txt
└── README.md
```

## Requirements

To run this application, you need to have Python and Flask installed. You can install the required packages using the following command:

```
pip install -r requirements.txt
```

## Running the Application

1. Clone the repository:
   ```
   git clone <repository-url>
   cd flask-domain-checker
   ```

2. Run the application:
   ```
   python app.py
   ```

3. Open your web browser and go to `http://127.0.0.1:5000`.

## License

This project is licensed under the MIT License.#   M X 2  
 