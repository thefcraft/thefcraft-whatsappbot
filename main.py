from flask import Flask, request, jsonify, make_response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from qrcode import QRCode
import base64
import os
import io
from time import sleep
import threading


app = Flask(__name__)

@app.route("/qrcode")
def qrcode():
    def img_to_base64(img):
        buffer = io.BytesIO()
        img.save(buffer, "PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def get_qrcode_from_website():
        for i in range(10):
            try:
                reload_element = browser.find_element(By.CLASS_NAME, '_1EP1P') # reload button
                reload_element.click()
            except: pass

            try:
                qr_element = browser.find_element(By.CLASS_NAME, '_19vUU')
                qr_data = qr_element.get_attribute('data-ref')
                return qr_data
            except: pass

            try:
                browser.find_element(By.CLASS_NAME, '_2vDPL')
                return None
            except: pass

            sleep(.5)
        print(browser.page_source)
        return False
        
    text = get_qrcode_from_website()
    if text is None: return jsonify({"Status": 'already logged in'})
    elif text is False: return jsonify({"Error": 'somting went wrong'})

    qr = QRCode(version=1, box_size=10, border=5)
    qr.add_data(text)
    qr.make(fit=True)
 
    img = qr.make_image(fill_color="black", back_color="white")
    img = img_to_base64(img)

    # return jsonify({"qr_code_image_as_base64": img})
    response = make_response(base64.b64decode(img))
    response.headers.set("Content-Type", "image/png")
    return response

@app.route("/")
def home():
    return jsonify({"qrcode": '/qrcode', 'reset':'/reset'})

@app.route("/reset")
def reset():
    return jsonify({"Status": 'under development'})

# @app.route("/api/otp")
# def otp(): 
    # country_code = 91
    # mobile_number = 8005960667
    # url = f'https://web.whatsapp.com/send/?phone=%2B{country_code}{mobile_number}'
    # return jsonify({"Status": 'under development'})



def send_message(message):  
    try:
        message_box_element = browser.find_element(By.CLASS_NAME, '_3Uu1_')
        message_box_element.click()
        message_box_element.send_keys(message)
        message_box_element.send_keys(Keys.ENTER)
        return True
    except: return False

def log_user(username='Log.txt'):
    try:
        serch_box_element = browser.find_element(By.CLASS_NAME, 'Er7QU')
        serch_box_element.send_keys(username)
        serch_box_element.send_keys(Keys.ENTER)
        return True
    except: return False

def last_message():
    try:
        last_message_element = browser.find_elements(By.CLASS_NAME, 'message-in')[-1]
        message = last_message_element.text
        return message
    except: return False

def new_message_click():
    def parent_element(element, n=1): 
        for _ in range(n):  
            element = element.find_element(By.XPATH, "..")
        return element

    while True:
        try: 
            green_dot_element = browser.find_element(By.CLASS_NAME, '_1pJ9J') #rx9719la
            break
        except: pass
        sleep(.5)
    try:
        user_element = parent_element(green_dot_element, n=8)
        user_element.click()
        try:
            username_parent =  parent_element(green_dot_element, n=4)
            username_element = username_parent.find_element(By.CLASS_NAME, '_7T_0D')
            return username_element.text
        except: return None
    except: return False

def log_sender(message, reply, message_time, username):
    if log_user():
        log = f"Time: {message_time} | User: {username} | Message: {message} | Reply: {reply}".replace("\n", " ")
        send_message(log)

    
# @app.route("/main")
def main():
    while True:
        username = new_message_click()
        if username != False:
            if username == None: username = 'unknown'
            message = last_message()
            if message.find('\n') == -1: 
                message_time = message
                message = None # image or audio or video etc.
                message_out = None
                reply = f'Hey {username}! i am unavailable right now.'
                send_message(reply)
                log_sender(message, reply, message_time, username)
                continue

            message_time = message.split('\n')[-1]
            message = '\n'.join(message.split('\n')[:-1])
            reply = f'Hey {username}! you just send {message} but i am unavailable right now.'
            send_message(reply)
            log_sender(message, reply, message_time, username)
            
        sleep(.2)
    

    # return jsonify({"Message": message, "Time": message_time})
    


if __name__ == "__main__":
    # dir_path = os.getcwd()
    # profile = os.path.join(dir_path, "profile", "wpp")

    options = webdriver.ChromeOptions()
    # options.add_argument(r"user-data-dir={}".format(profile))
    options.headless=True

    browser = webdriver.Chrome(chrome_options=options)
    browser.maximize_window()

    browser.get("https://web.whatsapp.com")
    
    threading.Thread(target=main, daemon=True).start()

    app.run()
