from flask import Flask, request, jsonify, render_template, send_file, session, Response
from werkzeug.utils import secure_filename
import os
import uuid
import json
import time
import threading
from tar_converter import TarConverter
import tempfile
import shutil

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'tar_converter_uploads')
CONVERTED_FOLDER = os.path.join(tempfile.gettempdir(), 'tar_converter_results')
ALLOWED_EXTENSIONS = {'tar', 'tar.gz', 'tgz', 'tar.bz2', 'tbz2'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

# In-memory progress storage
progress_store = {}

def allowed_file(filename):
    return '.' in filename and (filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS or 
                               filename.endswith('.tar.gz') or filename.endswith('.tar.bz2'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        # Generate unique filename
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id

        filename = secure_filename(file.filename)
        session['original_filename'] = filename

        filepath = os.path.join(UPLOAD_FOLDER, f"{session_id}_{filename}")
        file.save(filepath)
        session['filepath'] = filepath

        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'session_id': session_id,
            'filename': filename
        })

    return jsonify({'error': 'Invalid file format'}), 400

@app.route('/list_contents', methods=['GET'])
def list_contents():
    filepath = session.get('filepath')

    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'No file found'}), 404

    try:
        converter = TarConverter(filepath)
        contents = converter.list_contents()
        return jsonify({'contents': contents})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def do_conversion(filepath, target_format, output_path, session_id):
    """Background task to convert file with progress updates"""
    try:
        # Initialize progress
        progress_store[session_id] = {
            'status': 'starting',
            'progress': 0,
            'message': 'Starting conversion...',
            'error': None
        }

        def progress_callback(status, progress_percent, message=''):
            progress_store[session_id] = {
                'status': status,
                'progress': progress_percent,
                'message': message,
                'error': None
            }

        converter = TarConverter(filepath, output_path, verbose=True, progress_callback=progress_callback)

        if target_format == 'zip':
            result_path = converter.convert_to_zip()
        elif target_format == '7z':
            result_path = converter.convert_to_7z()
        elif target_format == 'rar':
            result_path = converter.convert_to_rar()

        # Mark as complete
        progress_store[session_id] = {
            'status': 'complete',
            'progress': 100,
            'message': f'Successfully converted to {target_format}',
            'error': None
        }
    except Exception as e:
        # Mark as failed
        progress_store[session_id] = {
            'status': 'failed',
            'progress': 0,
            'message': f'Conversion failed: {str(e)}',
            'error': str(e)
        }

@app.route('/convert', methods=['POST'])
def convert_file():
    filepath = session.get('filepath')
    original_filename = session.get('original_filename')
    session_id = session.get('session_id')

    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'No file found'}), 404

    target_format = request.json.get('format', 'zip')
    if target_format not in ['zip', '7z', 'rar']:
        return jsonify({'error': 'Invalid format specified'}), 400

    # Generate output filename
    base_name = os.path.splitext(original_filename)[0]
    if base_name.endswith('.tar'):
        base_name = base_name[:-4]

    output_filename = f"{base_name}.{target_format}"
    output_path = os.path.join(CONVERTED_FOLDER, f"{session_id}_{output_filename}")

    # Store path for later download
    session['converted_path'] = output_path
    session['converted_filename'] = output_filename

    # Start conversion in background thread
    thread = threading.Thread(target=do_conversion, args=(filepath, target_format, output_path, session_id))
    thread.daemon = True
    thread.start()

    return jsonify({
        'success': True,
        'message': f'Conversion started',
        'session_id': session_id
    })

@app.route('/progress')
def progress():
    """Server-Sent Events endpoint for progress updates"""
    session_id = session.get('session_id')

    if not session_id:
        return jsonify({'error': 'No active session'}), 404

    def generate():
        last_progress = None

        while True:
            current_progress = progress_store.get(session_id, {})

            # Send update if progress changed or it's complete/failed
            if current_progress != last_progress:
                data = json.dumps(current_progress)
                yield f"data: {data}\n\n"
                last_progress = current_progress.copy()

                # Exit loop when conversion is done
                if current_progress.get('status') in ['complete', 'failed']:
                    break

            time.sleep(0.5)

    return Response(generate(), mimetype='text/event-stream')

@app.route('/download', methods=['GET'])
def download_file():
    converted_path = session.get('converted_path')
    converted_filename = session.get('converted_filename')

    if not converted_path or not os.path.exists(converted_path):
        return jsonify({'error': 'Converted file not found'}), 404

    return send_file(converted_path, as_attachment=True, download_name=converted_filename)

@app.route('/cleanup', methods=['POST'])
def cleanup():
    # Clean up session files
    filepath = session.get('filepath')
    converted_path = session.get('converted_path')
    session_id = session.get('session_id')

    if filepath and os.path.exists(filepath):
        os.remove(filepath)

    if converted_path and os.path.exists(converted_path):
        os.remove(converted_path)

    if session_id and session_id in progress_store:
        del progress_store[session_id]

    session.clear()

    return jsonify({'success': True, 'message': 'Cleanup completed'})

if __name__ == '__main__':
    app.run(debug=True)