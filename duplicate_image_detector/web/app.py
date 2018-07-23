import os
import sys
from flask import Flask, render_template, send_from_directory, redirect
from flask_sqlalchemy import SQLAlchemy

from models import Images

view = "gallery"

if len(sys.argv) > 1:
	view = sys.argv[1]
	if view not in ["gallery","table"]:
		sys.exit("please view in gallery or table mode only..")


x = open('config.txt', 'r')
r = x.read()
x.close

img_dir = r.split('\n')[0].split(':')[1].strip()
images_per_page = int(r.split('\n')[1].split(':')[1].strip())


project_abs_path = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

db_url = 'sqlite:///' + os.path.join(project_abs_path, "..") + '/images_info.db'

app.config['SQLALCHEMY_DATABASE_URI'] = db_url

db = SQLAlchemy(app)


@app.route('/page/<int:page_num>')
def main(page_num):
    elements = Images.query.paginate(
        per_page=images_per_page, page=page_num, error_out=True)
    return render_template(view+".html", pages=elements)


@app.route('/')
def hello():
    return redirect("/page/1", code=302)


@app.route('/image/<filename>')
def send_file(filename):
    return send_from_directory(img_dir, filename)


if __name__ == '__main__':
    app.run(port=1111)
