from flask import Flask
from flask import render_template, flash, request, redirect, url_for
from flask import send_from_directory
from werkzeug.utils import secure_filename
import os

# create bib directory under tmp
if not os.path.exists("/tmp/bib"):
  os.mkdir("/tmp/bib")


UPLOAD_DIR = "/tmp/bib"

app = Flask(__name__)
app.config['UPLOAD_DIR'] = UPLOAD_DIR
app.secret_key = "59c957bc540b7b2d530fc46b9874633479488721d283f8582d54d961f107"

def allowed_file(filename):
  return "." in filename and \
      filename.rsplit(".", 1)[1].lower() == "bib"

@app.get("/")
def index_get():
  return render_template("index.html")

@app.post("/")
def index_post():
  # check if the post request has the file part.
  if "file" not in request.files:
    print("in 1.")
    flash("Request does not contain a file part.")
    return render_template("index.html")

  bibfile = request.files['file']
  # if the user does not select a file, the browser submits an empty file
  # without a filename.
  if bibfile.filename == "":
    print("in 2.")
    flash('Please select a file.')
    return render_template("index.html")
  if bibfile and allowed_file(bibfile.filename):
    print("in 3.")
    filename = secure_filename(bibfile.filename)
    bibfile.save(os.path.join(app.config["UPLOAD_DIR"], filename))
    print(type(bibfile))
    bibfile.seek(0)
    bibcontent = bibfile.read().decode("utf8")
    flash("Upload successful.")
    flash(bibcontent)
    return render_template("index.html")
  flash("Please select a .bib file.")
  return render_template("index.html")

@app.get("/entry")
def entry_get():
  return render_template("entry.html")

@app.post("/entry")
def entry_post():
  formlist = ["name", "author", "title", "journal", "volume", "number", "pages",
              "year", "doi"]
  fields = [[i, request.form[i]] for i in formlist]
  if all([i[1] for i in fields]):
    with open("/tmp/bib/main.bib", "a") as bibfile:
      # TODO: replace hardcoded main.bib with the fileaname.
      bibfile.write("\n")
      bibfile.write("@article{{{},".format(fields[0][1]))
      bibfile.write("\n")
      for i in fields:
        if i[0] != "name":
          bibfile.write("{} = \"{}\",".format(i[0], i[1]))
          bibfile.write("\n")
      bibfile.write("}")
      bibfile.write("\n")
    flash("Entry \"{}\" added.".format(fields[0][1]))
    return render_template("entry.html")
  else:
    flash("Please fill all fields!")
    return render_template("entry.html")

@app.route("/download")
def download():
  return send_from_directory(UPLOAD_DIR, "main.bib")
