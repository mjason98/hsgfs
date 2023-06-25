from flask import Flask, send_file, jsonify, request
from flask import make_response
import os


app = Flask(__name__)
CHUNCK_STORAGE_PATH = os.environ.get('STORAGE_PATH')
# CHUNCK_STORAGE_PATH = ''


@app.route('/get_chunk/<chunk_handler>', methods=['GET'])
def get_chunck(chunk_handler: str):
    file_path = os.path.join(CHUNCK_STORAGE_PATH, chunk_handler + '.part')
    print(file_path)
    return send_file(file_path, as_attachment=True)


@app.route('/delete_chunk/<chunk_handler>', methods=['DELETE'])
def delete_chunck(chunk_handler: str):
    file_path = os.path.join(CHUNCK_STORAGE_PATH, chunk_handler + '.part')

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'status': 200, 'message': 'deleted'})
        else:
            return jsonify({'status': 404, 'message': 'not found'})
    except Exception as ex:
        return jsonify({'status': 500, 'message': str(ex)})


@app.route('/update_chunk/<chunk_handler>', methods=['POST', 'PUT'])
def update_chunck(chunk_handler: str):
    file_path = os.path.join(CHUNCK_STORAGE_PATH, chunk_handler + '.part')

    if 'file' not in request.files:
        jsonify({'status': 400, 'message': 'not file recieved'})

    file = request.files['file']

    file.save(file_path)

    return jsonify({'status': 200, 'message': 'chunk saved'})


@app.route('/health', methods=['GET'])
def get_health():
    response_data = {"message": "Success"}
    response = make_response(jsonify(response_data), 200)
    return response


if __name__ == '__main__':
    app.run(port=8080)
