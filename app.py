import os, time
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.binary_location = os.getenv('GOOGLE_CHROME_PATH')
driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=os.getenv('CHROMEDRIVER_PATH'))#executable_path="./chromedriver") #executable_path=os.getenv('CHROMEDRIVER_PATH'))


def html_to_pdf(driver, fp):
    driver.get("https://pdfcrowd.com/#convert_by_upload")

    time.sleep(1)

    file_input = driver.find_element_by_xpath("/html/body/div/div[3]/div/div[1]/div[3]/form/div[1]/div[2]/div/div/input")

    file_input.send_keys(os.path.join(os.getcwd(), fp))

    convert_btn = driver.find_element_by_xpath("/html/body/div/div[3]/div/div[1]/div[3]/form/div[2]/div[1]/div/button")

    convert_btn.click()

    while True:
        time.sleep(1)
        try:
            ele = driver.find_element_by_xpath("/html/body/div/div[3]/div/div[1]/div[1]/div/div/div[2]/p[2]/a[1]")
            href = ele.get_attribute("href")
            if href.strip() == "":
                continue

            return href
        except:
            pass


def g_translate_pdf(driver, path, input_lang_code, output_lang_code, filename):

    driver.get(f"https://translate.google.com/?sl={input_lang_code}&tl={output_lang_code}&op=docs")
    time.sleep(1)

    ele = driver.find_element_by_xpath("/html/body/c-wiz/div/div[2]/c-wiz/div[3]/c-wiz/div[2]/c-wiz/div/form/div[1]/div[3]/input")

    ele.send_keys(os.path.join(os.getcwd(), path))


    translate_btn = driver.find_element_by_xpath("/html/body/c-wiz/div/div[2]/c-wiz/div[3]/c-wiz/div[2]/c-wiz/div/form/div[2]/div[2]/button")

    translate_btn.click()

    time.sleep(2)

    with open(f"{filename}_translated.html", "w") as f:
        f.write(driver.page_source)
        # f.write(driver.find_element_by_tag_name("body").get_attribute('innerHTML'))

    # return driver.page_source
    return html_to_pdf(driver, f"{filename}_translated.html")


UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = "secret!"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file_and_translate():
    if request.method == 'POST':
        # check if the post request has the file part
        input_lang = request.form.get("inputLang", "hi").lower()
        output_lang = request.form.get("outputLang", "en").lower()

        print (request.form)
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

            return redirect(g_translate_pdf(driver, f"./uploads/{filename}", input_lang, output_lang, filename.split(".")[0]))

            # return redirect(pdf_url)
            # return redirect(url_for('upload_file',
            #                         filename=filename))
    return render_template('index.html')




if __name__ == '__main__':
    app.run("0.0.0.0", port=5000)
    # html = open("test.html").read()
    # html_to_pdf(html)

