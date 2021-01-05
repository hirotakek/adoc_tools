#
# consume_sum_g
#
# import openpyxl
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import shutil
import os
import sys
from pathlib import Path
import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
# from time import sleep
import xlrd
# from xlrd import open_workbook
# from xlwt import Workbook
from xlutils.copy import copy
import datetime # added by HK
import chromedriver_binary  # Adds chromedriver binary to path
import numpy as np

#  Excelファイル選択ダイアログ表示、ファイルパス取得
def OpenFileDlg(tbox):
   ftype = [('','xls')] 
   dir = '.'
   # ファイルダイアログ表示
   filename = filedialog.askopenfilename(filetypes = ftype, initialdir = dir)
   # ファイルパスをテキストボックスに表示
   tbox.insert(0, filename)

#  Excelファイルディレクトリ選択ダイアログ表示、ファイルパス取得
def OpenDirectoryDlg(tbox):
   dir = '.'
   # ディレクトリダイアログ表示
   in_directory = filedialog.askdirectory(initialdir=dir)
   # ファイルディレクトリをテキストボックスに表示
   tbox.insert(0, in_directory)

# ディレクトリ配下の全ファイルをチェックする
def CheckExpense_all(dpath):
    get_file = glob.glob(dpath + "\*.xls")
    print(get_file)
    for fpath in get_file: # 指定ディレクトリ配下の全ファイル分繰り返し
        print(fpath)
        
        CheckExpense(fpath)

    # メッセージボックス（情報） ディレクトリ指定の場合のみメッセージボックスで終了通知
    messagebox.showinfo('確認', '指定フォルダ配下の全ファイルのチェックが終わりました。')



# Excelデータ確認
def CheckExpense(fpath):
   # 定数
   dt_now = datetime.datetime.now() # debug
   print(dt_now) # debug

   sheet_name = "支払伝票フォーマット" # 処理対象シート名
   add_file_name = "_チェック結果.xls" # チェック結果ファイル名として付加
   # month_for_Judge = 0 # data presence を判断するため
   start_row = 0
   item_Column = 12
   trans_Column = 13
   from_Column = 21
   arrow_Column = 27
   to_Column = 28
   price_Column = 34
   result_Column = 47 # 結果表示欄 （AV欄）
   
   
   # last_row_no = 59
   # trans_facility = {"JR","私鉄","バス","SkyMark","JAL"}
   
   options = Options()
   options.add_argument("--headless") # WEBを開かずに処理
   
   original_file = fpath # 指定された被処理ファイルパス
   original_file_name = Path(original_file).stem
   check_file_name = original_file_name + add_file_name # 結果ファイル名
   shutil.copyfile(original_file, check_file_name)
   
   
   read_wb = xlrd.open_workbook(check_file_name, formatting_info=True) # 書式保持
   read_sheet = read_wb.sheet_by_name(sheet_name)
   write_wb = copy(read_wb)
   write_sheet = write_wb.get_sheet(0)
   print("input:  ", original_file) # added HK for debug
   
   # trans_index = read_sheet.col(trans_Column)
   pan_data = read_sheet.col(item_Column) # 費目欄を読み込み（費目=交通費記載分をチェック）
   current_row = start_row # 0行目よりチェックカウント開始
   
   for item_obj in pan_data:
    row_values = read_sheet.row_values(current_row)
    
    if item_obj.value == "": # 費目がブランクなら処理スキップ
        result_text = ""
    elif item_obj.value == "交通費": # 交通費なら以下のチェック処理を実行
    # if row_values[item_Column] == '交通費': # 交通費なら以下の処理を実行
    # row_values = read_sheet.row_values(start_row) 後ろに移動
        
     if row_values[trans_Column] == 'タクシー': # タクシーならチェックスキップ
        
    # if row_values[trans_Column] not in trans_facility: # modified by HK
        
         result_text = 'タクシー'

     elif row_values[from_Column] == '': # 出発地不明
         result_text = '区間(出発地)不明'
         
        # break

     elif row_values[arrow_Column] == '': # 片道・往復の判別不可
         result_text = '1-2 Way不良'

     elif row_values[to_Column] == '': # 目的地不明
         result_text = '区間(目的地)不明'

     elif row_values[price_Column] == '': # 金額不明
         result_text = '金額未記入'

     else: # 交通費で判定可能なら以下の処理を実行（WEBで料金チェック）
         driver = webdriver.Chrome(options=options) # Headless（画面表示なし）でチェックを実行
         # driver = webdriver.Chrome(r"C:\Users\hirkatayama\Desktop\顧問関連\Python_proc\chromedriver.exe",options=options)
         driver.get("https://transit.yahoo.co.jp/")

         text = driver.find_element_by_id("sfrom") 
         text.send_keys(row_values[from_Column]) # 出発地
        # sleep(1)
         text.click()
        # sleep(1)

         text = driver.find_element_by_id("sto")
         text.send_keys(row_values[to_Column]) # 目的地
        # sleep(1)
         text.click()
        # sleep(1)

         ticket_kind = driver.find_element_by_name('ticket')
         ticket_kind_element = Select(ticket_kind)
         ticket_kind_element.select_by_value('normal') # 現金価格　ICなら 'normal'->'ic'に変更
         
         fare_cheap = driver.find_element_by_name("s")
         fare_cheap_element = Select(fare_cheap)
         fare_cheap_element.select_by_value("1") # 料金が安い順に表示

         btn = driver.find_element_by_id("searchModuleSubmit")
         btn.click() # 検索ボタンをクリック

         price = driver.find_elements_by_class_name("fare")
         price_text = price[0].text # 料金欄の最初(0番目)が料金
         price_text = price_text.replace(',',"")
         price_int = int(price_text.rstrip("円")) # 円を削除し、整数値に変換
         driver.close # WEBサイトを閉じる（つもり）

         price_num = 0
         if row_values[arrow_Column] == '⇒':
             price_num = 1

         elif row_values[arrow_Column] == '⇔':
             price_num = 2

         if price_num == 0:
             result_text = '往復例外'

         else:
             result_int = price_int * price_num

             if row_values[price_Column] == result_int:
                 result_text = 'OK'

             else:
                 result_int = "{:,}".format(result_int)
                 result_text = str(result_int)+'円'

    else:
        if item_obj.value == "費目":
            result_text = ""
        else:
            result_text = "対象外"
        
    write_sheet.write(current_row,result_Column,result_text)
    write_wb.save(check_file_name)

    current_row = current_row + 1 # HK 順序変更
    row_values = read_sheet.row_values(start_row) # HK 順序変更
        
    dt_now = datetime.datetime.now() # added by HK
    # print(dt_now) # added by HK
   
   
   print("output folder:  ", os.getcwd()) # added HK for debug
   print("output file name:  ", check_file_name) # added HK for debug
   print("指定ファイルのチェックが終わりました。") # 追加
   
   dt_now = datetime.datetime.now() # debug
   print(dt_now) # debug

   # メッセージボックス（情報） 
   # messagebox.showinfo('確認', '指定ファイルのチェックが終わりました。')
   
   return


# 閉じるコールバック
def DoExit():
    # exit this program
    root.destroy()
    sys.exit(0)

#
# メイン
#
root = tk.Tk()
root.title('交通費チェック　xlsファイル用')
root.geometry("370x170")

# Excelファイルダイアログ
label = tk.Label(root, text='Excelファイル')
label.place(x=30, y=10)
direct_text = tk.Entry(root, width=40)
direct_text.place(x=30, y=30)
file_text = tk.Entry(root, width=40)
file_text.place(x=30, y=60)

fdlg_button = tk.Button(root, text='ディレクトリ選択', command = lambda: OpenDirectoryDlg(direct_text) )
fdlg_button.place(x=280, y=30)

fdlg_button = tk.Button(root, text='ファイル選択', command = lambda: OpenFileDlg(file_text) )
fdlg_button.place(x=280, y=60)

# 処理実施ボタン
all_check_button = tk.Button(root, text='allチェック', command = lambda: CheckExpense_all(direct_text.get()))
all_check_button.place(x=60, y=100)

# 処理実施ボタン
calc_button = tk.Button(root, text='チェック', command = lambda: CheckExpense(file_text.get()))
calc_button.place(x=140, y=100)

# 閉じるボタン
close_button = tk.Button(root, text='閉じる', command = lambda: DoExit())
close_button.place(x=200, y=100)
root.mainloop()