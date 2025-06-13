
import requests
import time
import smtplib
from email.message import EmailMessage
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")


send_mail = ""
pw = ""
with open("sender.txt", "r") as file:
    lines = file.readlines()
    send_mail = lines[0].strip()
    print(send_mail)
    pw = lines[1].strip()
    print(pw)

print("Suche nach freigewordenen Basslinern von Hamburg-ZOB und Hamburg-Veddel (Mittwoch 25.06.2025)")

print("Frühester gewünschte Abfahrtszeit (Nur in ganzen Stunden andgeben z.B. 7:00 = 7 )")
min_hour = int(input())
print("Spätester gewünschte Abfahrtszeit (Nur in ganzen Stunden andgeben z.B. 15:00 = 15 )")
max_hour = int(input())

print("E-Mail Adresse:")
email = input()

stations = ["Hamburg Veddel", "Hamburg ZOB"]

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://bassliner.org/fahrten/fusion-festival-2025")

def find(driver, station, max_hour, min_hour):
    city_dropdown = driver.find_element(By.CLASS_NAME, "vs__search")
    city_dropdown.click()

    city_dropdown.send_keys(station)

    time.sleep(1)

    city_dropdown.send_keys(Keys.RETURN)

    time.sleep(2)
    found, t = exists("bsl-tour__wrapper")
    hour = int(t.split(":")[0])
    if found and hour <= max_hour and hour >= min_hour: # notification is only going out if the bus is in the correct time slot
        print(f"Bus verfügbar um {t}. {email} wird benachrichtigt")
        msg = EmailMessage()
        msg['Subject'] = f'BUS GEFUNDEN ({t})'
        msg['From'] = send_mail
        msg['To'] = email
        msg.set_content(f'Ein Bus von {station} um {t} wurde gefunden!\n https://bassliner.org/fahrten/fusion-festival-2025')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(send_mail, pw)
            smtp.send_message(msg)
        return found
    else:
        print(f"Bus gefunden aber zur falschen Zeit ({t})")
        return False

def exists(class_name):
    try:
        elem = driver.find_element(By.CLASS_NAME, class_name)
        time_div = elem.find_element(By.CLASS_NAME, "bsl-tour__col-time")
        t_span = time_div.find_element(By.TAG_NAME, "span")
        t = t_span.text
        return True, t
    except NoSuchElementException:
        return False, 0

    

while True:
    countdown = 6
    found_stations = {"Hamburg ZOB": False,
                      "Hamburg Veddel": False}
    for station in stations:
        found_stations.update({station : find(driver, station, max_hour, min_hour)})
    if True in found_stations.values():
        exit()
    print(f"\rGesucht um: {time.strftime('%H:%M:%S')}")
    while countdown > 0:
        mins, secs = divmod(countdown, 60)
        timer = f"{mins:02d}:{secs:02d}"
        print(f"\r{timer}", end="")
        time.sleep(1)
        countdown -= 1


