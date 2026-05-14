#projeto para acessar ssw
import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv

load_dotenv()

time.sleep(1)
print("Iniciando navegador")
driver = webdriver.Chrome()
driver.get("https://sistema.ssw.inf.br/bin/ssw0422")

driver.find_element(By.NAME, "f1").send_keys(os.environ.get("SSW_EMPRESA"))
driver.find_element(By.NAME, "f2").send_keys(os.environ.get("SSW_CPF"))
driver.find_element(By.NAME, "f3").send_keys(os.environ.get("SSW_USUARIO"))
driver.find_element(By.NAME, "f4").send_keys(os.environ.get("SSW_SENHA"))