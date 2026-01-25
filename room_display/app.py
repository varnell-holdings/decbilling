from flask import Flask, render_template, jsonify, send_from_directory
import boto3
import csv
from io import StringIO
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)

# S3 bucket name
BUCKET_NAME = 'dec601'

# Store last modified times for change detection
last_modified_cache = {}


def get_s3_client():
    """Create and return an S3 client using environment credentials."""
    return boto3.client('s3')


def get_csv_from_s3(room_name):
    """
    Read CSV file from S3 and return rows as list of dictionaries.
    Also updates the last_modified cache.
    """
    s3 = get_s3_client()
    file_key = f"{room_name}.csv"

    try:
        # Get the object from S3
        response = s3.get_object(Bucket=BUCKET_NAME, Key=file_key)

        # Update last modified cache
        last_modified_cache[room_name] = response['LastModified'].isoformat()

        # Read CSV content
        csv_content = response['Body'].read().decode('utf-8')

        # Parse CSV
        reader = csv.DictReader(StringIO(csv_content))
        rows = list(reader)

        return rows

    except Exception as e:
        print(f"Error reading {file_key} from S3: {e}")
        return []


def get_last_modified(room_name):
    """Get the last modified timestamp for a room's CSV file."""
    s3 = get_s3_client()
    file_key = f"{room_name}.csv"

    try:
        response = s3.head_object(Bucket=BUCKET_NAME, Key=file_key)
        return response['LastModified'].isoformat()
    except Exception as e:
        print(f"Error getting last modified for {file_key}: {e}")
        return None


def get_current_date():
    """Return today's date formatted nicely (e.g., 'Saturday, January 25, 2026')."""
    aus_tz = ZoneInfo('Australia/Sydney')
    return datetime.now(aus_tz).strftime('%A, %B %d, %Y')


@app.route('/room1')
def room1():
    """Display procedures for Room 1."""
    rows = get_csv_from_s3('room1')
    current_date = get_current_date()
    return render_template('room.html', room_name='Room 1', rows=rows, current_date=current_date)


@app.route('/room2')
def room2():
    """Display procedures for Room 2."""
    rows = get_csv_from_s3('room2')
    current_date = get_current_date()
    return render_template('room.html', room_name='Room 2', rows=rows, current_date=current_date)


@app.route('/deccal.html')
def deccal():
    """Serve the deccal.html static file."""
    return send_from_directory('static', 'deccal.html')


@app.route('/check_updates/<room>')
def check_updates(room):
    """
    Return JSON with last modified timestamp for polling.
    Frontend uses this to detect when to reload.
    """
    # Only allow room1 or room2
    if room not in ['room1', 'room2']:
        return jsonify({'error': 'Invalid room'}), 400

    last_modified = get_last_modified(room)
    return jsonify({'last_modified': last_modified})


if __name__ == '__main__':
    # Run in debug mode for local development
    app.run(debug=True, host='0.0.0.0', port=5000)
