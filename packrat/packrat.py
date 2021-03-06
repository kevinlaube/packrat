from configparser import ConfigParser
from io import BytesIO
from os import getenv
from sys import argv, exit

from flask import abort, Flask, render_template, request, send_file

from memorycache import MemoryCache

app = Flask(__name__)
cache = MemoryCache()

@app.route('/<key>', methods=['GET', 'POST'])
def set_or_get(key=None):
    """
    Route for uploading a file.  Expects a key parameter.
    """
    # TODO: What if a user uploads a file with a blank filename?
    if not key:
        abort(400)
    if request.method == 'POST':
        print(request.files['file'])
        return cache.store_file(key, request.files['file'])

    file = cache.get_file(key)
    if not file:
        abort(404)
    return send_file(BytesIO(file[1]), as_attachment=True, attachment_filename=file[0])


@app.route('/')
def status_screen():
    files, total_size, max_size = cache.status()
    return render_template(
        'packrat.html',
        files=files,
        total_size=total_size,
        max_size=max_size)


if __name__ == '__main__':
    if len(argv) != 2:
        exit("Usage: python packrat.py <config.ini>")
    config = ConfigParser()
    config.read(argv[1])
    try:
        host = config['packrat'].get('host', '0.0.0.0')
        port = config['packrat'].get('port', '5000')
        debug = config['packrat'].getboolean('debug', True)
    except KeyError:
        print("Invalid or non-existent config file: " + argv[1])
        raise
    app.run(host=host, port=int(port), debug=debug)
