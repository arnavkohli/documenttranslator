import os, time
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def g_translate_pdf(path, input_lang_code, output_lang_code):
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--disable-gpu')
	chrome_options.add_argument('--no-sandbox')
	chrome_options.binary_location = os.getenv('GOOGLE_CHROME_PATH')
	driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=os.getenv('CHROMEDRIVER_PATH'))
	driver.get(f"https://translate.google.com/?sl={input_lang_code}&tl={output_lang_code}&op=docs")
	time.sleep(1)

	ele = driver.find_element_by_xpath("/html/body/c-wiz/div/div[2]/c-wiz/div[3]/c-wiz/div[2]/c-wiz/div/form/div[1]/div[3]/input")

	ele.send_keys(os.path.join(os.getcwd(), path))


	translate_btn = driver.find_element_by_xpath("/html/body/c-wiz/div/div[2]/c-wiz/div[3]/c-wiz/div[2]/c-wiz/div/form/div[2]/div[2]/button")

	translate_btn.click()

	time.sleep(2)

	return driver.page_source

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file_and_translate():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return g_translate_pdf(f"./uploads/{filename}", "hi", "en")
            # return redirect(url_for('upload_file',
            #                         filename=filename))
    return render_template('index.html')




if __name__ == '__main__':
	app.run("0.0.0.0", port=5000)