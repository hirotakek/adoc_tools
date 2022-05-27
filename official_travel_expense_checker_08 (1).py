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
from chromedriver_py import binary_path # this will get you the path variable
from time import sleep
import xlrd
from xlutils.copy import copy
import datetime # added by HK
import pandas as pd
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
   
   #webサイトの動作をwebを開かずに実行
   options = Options()
   options.add_argument("--headless") # WEBを開かずに処理
   
   original_file = fpath # 指定された被処理ファイルパス
   original_file_name = Path(original_file).stem # パスから拡張子を削除
   check_file_name = original_file_name + add_file_name # 結果ファイル名
   shutil.copyfile(original_file, check_file_name)
   
   
   read_wb = xlrd.open_workbook(check_file_name, formatting_info=True) # 書式保持
   read_sheet = read_wb.sheet_by_name(sheet_name)
   write_wb = copy(read_wb)
   write_sheet = write_wb.get_sheet(0)
   print("input:  ", original_file) # added HK for debug
   
   
   pan_data = read_sheet.col(item_Column) # 費目欄を読み込み（費目=交通費記載分をチェック）
   current_row = start_row # 0行目よりチェックカウント開始
   
   
   for item_obj in pan_data:

    row_values = read_sheet.row_values(current_row)
    
    if item_obj.value == "": # 費目がブランクなら処理スキップ
        result_text = ""
    elif item_obj.value == "交通費" or item_obj.value== "出張交通費": # 交通費又は出張交通費なら以下のチェック処理を実行
    # if row_values[item_Column] == '交通費': # 交通費なら以下の処理を実行
    # row_values = read_sheet.row_values(start_row) 後ろに移動
        
     if row_values[trans_Column] == 'タクシー': # タクシーならチェックスキップ
        
    # if row_values[trans_Column] not in trans_facility: # modified by HK
        
         result_text = 'タクシー'


     elif row_values[from_Column] == '': # 出発地不明
         result_text = '区間(出発地)不明'
         
        

     elif row_values[arrow_Column] == '': # 片道・往復の判別不可
         result_text = '1-2 Way不良'

     elif row_values[to_Column] == '': # 目的地不明
         result_text = '区間(目的地)不明'

     elif row_values[price_Column] == '': # 金額不明
         result_text = '金額未記入'

     else: # 交通費で判定可能なら以下の処理を実行（WEBで料金チェック）
     
      price_num = 0
      if row_values[arrow_Column] == '⇒':
          price_num = 1

      elif row_values[arrow_Column] == '⇔':
          price_num = 2

      if price_num == 0:
          result_text = '往復例外'

      else:
         
        # driver = webdriver.Chrome(options=options) # Headless（画面表示なし）でチェックを実行
        # driver = webdriver.Chrome() # Headless（画面表示なし）でチェックを実行
        # driver = webdriver.Chrome(r"C:\Users\hirkatayama\Desktop\顧問関連\Python_proc\chromedriver.exe",options=options)
         
        #display_orders = [1]　for文を一回回すため
        result_text = "例外発生"

        display_orders = ["IC","Ticket"]
        for display_order in display_orders:
         if result_text == "OK":
             break
         else:
             driver = webdriver.Chrome(executable_path=binary_path, options=options)
            # driver = webdriver.Chrome(options=options)
             cur_url = "https://www.jorudan.co.jp/"
             #jorudan のURLを指定
             driver.get(cur_url)
             
             sleep(2)
            
             text = driver.find_element_by_id("eki1_in") 
             text.send_keys(row_values[from_Column]) # 出発地
             sleep(1)
             
             try:
                 text = driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[3]/div[1]/form[1]/fieldset/div[2]/div[2]/table/tbody/tr[1]/td[1]/div/div/ul/li[1]")
                 text.click()
             except:
                 print(row_values[from_Column], "出発地駅名が有りません。")
                 result_text = "出発地不明"
                 break

             text = driver.find_element_by_id("eki2_in")
             text.send_keys(row_values[to_Column]) # 目的地
             sleep(1)
             
             try:
                 text = driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[3]/div[1]/form[1]/fieldset/div[2]/div[2]/table/tbody/tr[2]/td/div/div/ul/li[1]")
                 text.click()
                 sleep(1)
             except:
                 print(row_values[to_Column], "目的地駅名が有りません。")
                 result_text = "目的地不明"
                 break
             
             if display_order == "IC":
                 ticket_kind = driver.find_element_by_id("Cfp1")#ICの場合の処理
                 ticket_kind.click() #ICを選択
                 sleep(1)
             elif display_order == "Ticket":
                 ticket_kind = driver.find_element_by_id("Cfp2")#切符利用の場合
                 ticket_kind.click() #切符を選択
                 sleep(1)
            
             btn = driver.find_element_by_name("S")
             btn.click() # 検索ボタンをクリック
            
        
             cur_url2=driver.current_url
             kekka = pd.read_html(cur_url2)[0] # テーブルの０番目を抽出
             #print(kekka) テーブルが取得出来てるか確認する
             #type(kekka) # DataFrame typeを確認する
             #numpyを使ってDataFrameを二次元配列に置き換える
             #print(type(kekka))
             array_kekka = np.array(kekka) # DataFrame を配列に変換
             #print(array_kekka)
             array_kekka1 = array_kekka[0:,4:5] # 全行（0～終わり）の4欄（4:5）取り出し（スライス）
             #print(array_kekka1)
             
             driver.close()
             sleep(2)
            
             for i in array_kekka1:
                 #print(i)
                 #print(type(i))
                 price_int_1 = i[0].rstrip("円") # 要素１つの配列の０番目要素から"円"を削除
                 #print(type(price_int_1))
                 price_text1 =  price_int_1.replace(',',"") # 値段の[,]を削除
                 price_int_2 = int(price_text1)
                 #print(type(price_int_2))
                 #print("end")
             # driver.close()
             # sleep(2)
                 result_int1 = price_int_2 * price_num
                 if row_values[price_Column] == result_int1:
                    result_text = "OK"
                    break
            
                 else:
                  # result_int = "{:,}".format(result_int1)
                  # result_text = str(result_int)+'円'
                      result_text = str(result_int1) + '円'

    else:
        if item_obj.value == "費目":
            result_text = ""
        else:
            result_text = "対象外"
    


    write_sheet.write(current_row,result_Column,result_text)
    write_wb.save(check_file_name)

    current_row = current_row + 1 # HK 順序変更
    # row_values = read_sheet.row_values(start_row) # HK 順序変更
        
    # dt_now = datetime.datetime.now() # added by HK
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
root.geometry("370x150")

# 出力用ディレクトリ
#os.chdir(r"出力用ディレクトリを記入")

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