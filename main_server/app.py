from flask import Flask, render_template, request


app = Flask(__name__)


@app.route('/get_chunk_distro/<filename>')
def get_chunk_distro(filename):
    return f'Hello, Flask! {filename}'


@app.route('/gen_chunk_distro/<filename>')
def gen_chunk_distro(filename):
    return f'Hello, Flask! {filename}'


@app.route('/delete/<filename>')
def delete_by_filename(filename):
    return f'Hello, Flask! {filename}'

# def mark_soft_delete():
# def validate_file():


if __name__ == '__main__':
    app.run(port=8020)
