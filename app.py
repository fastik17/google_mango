import gspread

from flask import Flask, render_template, request
from google.oauth2 import service_account
import environs

env = environs.Env()

app = Flask(__name__)


def get_credentials():
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    GOOGLE_PRIVATE_KEY = env.str("GOOGLE_PRIVATE_KEY")
    # The environment variable has escaped newlines, so remove the extra backslash
    GOOGLE_PRIVATE_KEY = GOOGLE_PRIVATE_KEY.replace('\\n', '\n')

    account_info = {
        "private_key": GOOGLE_PRIVATE_KEY,
        "client_email": env.str("GOOGLE_CLIENT_EMAIL"),
        "token_uri": "https://accounts.google.com/o/oauth2/token",
    }

    credentials = service_account.Credentials.from_service_account_info(account_info, scopes=scopes)
    client = gspread.authorize(credentials)

    return client


@app.route('/')
def my_form():
    return render_template('form.html')


@app.route('/', methods=['POST'])
def my_form_post():
    try:
        client = get_credentials()
        gsheet_link = request.form['googleSheetLink']
        gsheet_data = client.open_by_url(gsheet_link).sheet1
        values = gsheet_data.get_all_records()
        print(values)
        headers = {}
        for row in values:
            for k, v in row.items():
                if v == '':
                    row[k] = {v: type(None)}
                else:
                    row[k] = {v: type(v)}
                headers.update({k: type(k)})
        return render_template('index.html', headers=headers, values=values)
    except gspread.exceptions.NoValidUrlKeyFound:
        return 'Please, provide GoogleSheet Link.'
    except gspread.exceptions.APIError as e:
        if 'PERMISSION_DENIED' in str(e):
            return 'Permission denied, this Google Sheet is not public.'
