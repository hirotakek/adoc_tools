# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 15:32:34 2020

@author: hirkatayama
"""

import streamlit as st
from selenium import webdriver #Selenium Webdriverをインポートして
import time
import chromedriver_binary  # Adds chromedriver binary to path

st.title("WEBコントロールのサンプルです。")

driver = webdriver.Chrome()

# driver = webdriver.Chrome(r"C:\Users\hirkatayama\Desktop\顧問関連\Python_proc\chromedriver.exe")
                          # chromeを動かすドライバを読み込み
# driver.get("https://google.co.jp") #googleを開く！
driver.get("https://www4.hp-ez.com/hp/semi-adoc/page2") # ADOC講習用サイトを開く！

# text = driver.find_element_by_id("lst-id") # ID属性から検索用テキストボックスの要素を取得し
text = driver.find_element_by_id("id") # ID属性から検索用テキストボックスの要素を取得し

text.send_keys("adocsemi") # 文字列"adocsemi" [id]をテキストボックスに入力

time.sleep(2)


text = driver.find_element_by_name("p") # NAME属性から検索用テキストボックスの要素を取得し

text.send_keys("selenium") # 文字列"selenium" [password]をテキストボックスに入力

time.sleep(2)

# btn = driver.find_element_by_name("btnK") # 検索用ボタンにはID属性がないのでname属性から取得し
# btn.click() # 対象をクリック！
btn = driver.find_element_by_name("logsubmit") # 「ログイン」ボタンをクリック
btn.click()

time.sleep(5)
driver.close()

st.mainloop()
