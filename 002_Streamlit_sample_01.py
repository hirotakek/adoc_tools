# -*- coding: utf-8 -*-
"""
Created on Thu May 12 15:41:57 2022

@author: hirkatayama
"""

import streamlit as st

# 複数選択
# st.multiselect('ラベル', ['選択肢1', '選択肢2', '選択肢3'])

st.title("ADOC TOOL site")

tool_name_1 = st.selectbox('ツールのカテゴリを指定して下さい。',('終了', '標準ツール', "プロジェクト個別", '選択肢1', '選択肢3'))
if tool_name_1 == '標準ツール':
    tool_name = st.selectbox('どのツールを使いますか？選択して下さい。',('終了', 'QR Code作成', "バーコード作成", 'PDFをキャラクタに変換(日本語不可)', "webからテーブル抽出", "音楽再生"))
elif tool_name_1 == "プロジェクト個別":
    pass_code1 = st.text_input("パスコード", type="password")
    if pass_code1 == "qic":
        tool_name_2 = st.selectbox("ターゲットプロジェクト", ("終了", "SB駆け付け", "その他"))
        if tool_name_2 ==  "SB駆け付け":
            tool_name = st.selectbox("どのツールを使いますか？", ('駆け付け費用チェック', "終了"))
        else:
            tool_name = "終了"
    else:
        st.write("パスコードを入力して下さい。")
        tool_name = "終了"
else:
    tool_name = "終了"

def kaketsuke():
    import streamlit as st
    import pandas as pd
    
    
    st.subheader("駆けつけ費用チェックツール")
    st.write("ファイルをアップロードして下さい")
    
    uploaded_file_s = st.file_uploader("SBファイルを指定", type="xlsx")
    uploaded_file_m = st.file_uploader("案件ファイルを指定", type="xlsx")
    uploaded_file_a = st.file_uploader("Airファイルを指定", type="xlsx")
    uploaded_file_g = st.file_uploader("提出用ファイルを指定", type="xlsx")
    
    
    
    # もし、データが揃ったら処理開始ボタン押下
    if st.checkbox("処理開始"):
        if uploaded_file_s is not None and uploaded_file_a is not None and uploaded_file_g is not None:
            st.write("start")
    
    # チェック処理開始
    
            # 定数
            # sheet_name = "" # 処理対象シート名
            # title_row = 0
            title_row_pt1 = 2
            title_row_pt2 = 3
            
            # SBファイルロード
            df_customer1 = pd.read_excel(uploaded_file_s, header=title_row_pt1, usecols=['案件管理No.','かけつけ費金額\n(往復)','宿泊費金額', 'かけつけ費合計'])
            df_customer1 = df_customer1.fillna(0.0) # 何も入力が無いNaNを比較出来るように数値に置換え
            
            # 案件ファイルロード
            df_customer2 = pd.read_excel(uploaded_file_m, header=title_row_pt2, usecols=['案件管理No.','かけつけ費金額\n(往復)','宿泊費金額', 'かけつけ費合計'])
            df_customer2 = df_customer2.fillna(0.0) # 何も入力が無いNaNを比較出来るように数値に置換え
            
            # Airファイルロード
            df_customer3 = pd.read_excel(uploaded_file_a, header=title_row_pt1, usecols=['案件管理No.','かけつけ費金額\n(往復)','宿泊費金額', 'かけつけ費合計'])
            df_customer3 = df_customer3.fillna(0.0) # 何も入力が無いNaNを比較出来るように数値に置換え
            
            # 顧客提出用ファイル
            df = pd.read_excel(uploaded_file_g, index_col=0, usecols=["NO","管理ID","対応日","カテゴリ","交通費(往復)"], skiprows=[1])
            df = df.fillna(0.0) # 何も入力が無いNaNを比較出来るように数値に置換え
    
    
    
            # 管理IDの重複確認、一つ目以外の重複は True となる
            df_mod = df.duplicated(subset="管理ID",keep="first")
            df_tail = df.tail(1).index # 最終行のインデックス値
            
            # compare
            for pindex in df.index: # Primary file top to bottom
            
                # 初期値
                usage = 0.0 # 交通費＋タクシー代
                accomodation_fee = 0.0 # 宿泊費
                claim_total = 0.0 # 合計金額
                pindex_count = pindex # 現在行から下の行のためのカウンタ
            
                # 管理ID読み出し
                mid1 = df.loc[pindex, "管理ID"]
                mid1_result = 1 # このまま抜けると一致するID無し
                
                # 管理IDが文字列でなければ対象外とする
                if type(mid1) != str and mid1 != 0.0:
                    st.write(mid1," = 対象外")
                    continue
                elif mid1 == 0.0:
                    continue
                
                # 管理IDが物品等
                if "-" or "_" in mid1:
                    pass
                else:
                    st.write(mid1," = 対象外")
                    continue
                
                # 管理IDが同一かをチェックする
                if df_mod[pindex] == True:
                    st.write(df.loc[pindex, "管理ID"], " = 同一ID")
                    continue
        
                
                # visit_date = df.loc[pindex, "対応日"]
                category = df.loc[pindex, "カテゴリ"]
                
                if category == "公共機関" or category == "タクシー":
                    usage = df.loc[pindex, "交通費(往復)"]
                    accomodation_fee = 0.0
                elif category == "宿泊費":
                    usage = 0.0
                    accomodation_fee = df.loc[pindex, "交通費(往復)"]
                
                
                while pindex_count < df_tail: # 現在行の後ろに同一管理番号があればマージする
                   
                    if mid1 == df.loc[pindex_count+1, "管理ID"]:
                        category1 = df.loc[pindex_count+1, "カテゴリ"]
                        if category1 == "公共機関" or category1 == "タクシー":
                            usage = usage + df.loc[pindex_count+1, "交通費(往復)"]
                        elif category1 == "宿泊費":
                            accomodation_fee = accomodation_fee + df.loc[pindex+1, "交通費(往復)"]
                    
                    pindex_count = pindex_count + 1
                # ここまでがWhileで、同一管理番号をマージする
                    
                claim_total = usage + accomodation_fee
        
                    
                for sb_count1 in df_customer1.index:
                    if mid1 == df_customer1.loc[sb_count1,"案件管理No."]:
        #                st.write("mid1",df_customer1.loc[sb_count1,"案件管理No."])
                        if df_customer1.loc[sb_count1,'かけつけ費金額\n(往復)'] == usage:
        #                    st.write(df_customer1.loc[sb_count1,'かけつけ費金額\n(往復)'],"  ,  ",usage)
                            if df_customer1.loc[sb_count1,'宿泊費金額'] == accomodation_fee:
        #                        st.write(df_customer1.loc[sb_count1,'宿泊費金額'],"  ,  ",accomodation_fee)
                                if df_customer1.loc[sb_count1,'かけつけ費合計'] == claim_total:
        #                            st.write(df_customer1.loc[sb_count1,'かけつけ費合計'],"  ,  ",claim_total)
                                    # st.write(mid1, " = OK")
                                    mid1_result = 0
                                    continue
                                else:
                                    mid1_result = 12 # "かけつけ費合計"不一致
                            else:
                                mid1_result = 11 # "宿泊費金額"不一致
                                st.write(accomodation_fee,"  ",df_customer1.loc[sb_count1,'宿泊費金額'])
    #
                                if df_customer1.loc[sb_count1,'かけつけ費合計'] == claim_total:
                                    mid1_result = mid1_result + 0
                                else:
                                    mid1_result = mid1_result + 12 # "かけつけ費合計"不一致
    #
                        else:
                            mid1_result = 10 # "かけつけ費金額\n(往復)"不一致
    #
                            if df_customer1.loc[sb_count1,'宿泊費金額'] == accomodation_fee:
                                if df_customer1.loc[sb_count1,'かけつけ費合計'] == claim_total:
                                    mid1_result = mid1_result + 0
                                else:
                                    mid1_result = mid1_result + 12 # "かけつけ費合計"不一致
                            else:
                                mid1_result = mid1_result + 11 # "宿泊費金額"不一致
                                st.write(accomodation_fee,"  ",df_customer1.loc[sb_count1,'宿泊費金額'])
    #
                                if df_customer1.loc[sb_count1,'かけつけ費合計'] == claim_total:
                                    mid1_result = mid1_result + 0
                                else:
                                    mid1_result = mid1_result + 12 # "かけつけ費合計"不一致
    #
                else:
                    for sb_count2 in df_customer2.index:
                        mod_mid = df_customer2.loc[sb_count2,"案件管理No."]   # .replace("_","-")
                        if mid1 == mod_mid:
                   #     if mid1 == df_customer2.loc[sb_count2,"案件管理No."]:
                            if df_customer2.loc[sb_count2,'かけつけ費金額\n(往復)'] == usage:
                                if df_customer2.loc[sb_count2,'宿泊費金額'] == accomodation_fee:
                                    if df_customer2.loc[sb_count2,'かけつけ費合計'] == claim_total:
                                        # st.write(mid1, " = OK")
                                        mid1_result = 0
                                        continue
                                    else:
                                        mid1_result = 12 # "かけつけ費合計"不一致
                                else:
                                    mid1_result = 11 # "宿泊費金額"不一致
                                    st.write(accomodation_fee,"  ",df_customer2.loc[sb_count2,'宿泊費金額'])
    #
                                    if df_customer1.loc[sb_count1,'かけつけ費合計'] == claim_total:
                                        mid1_result = mid1_result + 0
                                    else:
                                        mid1_result = mid1_result + 12 # "かけつけ費合計"不一致
    # 
                            else:
                                mid1_result = 10 # "かけつけ費金額\n(往復)"不一致
    #
                                if df_customer1.loc[sb_count1,'宿泊費金額'] == accomodation_fee:
                                    if df_customer1.loc[sb_count1,'かけつけ費合計'] == claim_total:
                                        mid1_result = mid1_result + 0
                                    else:
                                        mid1_result = mid1_result + 12 # "かけつけ費合計"不一致
                                else:
                                    mid1_result = mid1_result + 11 # "宿泊費金額"不一致
                                    st.write(accomodation_fee,"  ",df_customer1.loc[sb_count1,'宿泊費金額'])
        #
                                    if df_customer1.loc[sb_count1,'かけつけ費合計'] == claim_total:
                                        mid1_result = mid1_result + 0
                                    else:
                                        mid1_result = mid1_result + 12 # "かけつけ費合計"不一致
    #
    
                    else:
                        for sb_count3 in df_customer3.index:
                            mod_mid = df_customer3.loc[sb_count3,"案件管理No."]   # .replace("_","-")
                            if mid1 == mod_mid:
                       #     if mid1 == df_customer2.loc[sb_count2,"案件管理No."]:
                                if df_customer3.loc[sb_count3,'かけつけ費金額\n(往復)'] == usage:
                                    if df_customer3.loc[sb_count3,'宿泊費金額'] == accomodation_fee:
                                        if df_customer3.loc[sb_count3,'かけつけ費合計'] == claim_total:
                                            # st.write(mid1, " = OK")
                                            mid1_result = 0
                                            continue
                                        else:
                                            mid1_result = 12 # "かけつけ費合計"不一致
                                    else:
                                        mid1_result = 11 # "宿泊費金額"不一致
                                        st.write(accomodation_fee,"  ",df_customer3.loc[sb_count3,'宿泊費金額'])
    #
                                        if df_customer1.loc[sb_count1,'かけつけ費合計'] == claim_total:
                                            mid1_result = mid1_result + 0
                                        else:
                                            mid1_result = mid1_result + 12 # "かけつけ費合計"不一致
    #
                                else:
                                    mid1_result = 10 # "かけつけ費金額\n(往復)"不一致
    #
                                    if df_customer1.loc[sb_count1,'宿泊費金額'] == accomodation_fee:
                                        if df_customer1.loc[sb_count1,'かけつけ費合計'] == claim_total:
                                            mid1_result = mid1_result + 0
                                        else:
                                            mid1_result = mid1_result + 12 # "かけつけ費合計"不一致
                                    else:
                                        mid1_result = mid1_result + 11 # "宿泊費金額"不一致
                                        st.write(accomodation_fee,"  ",df_customer1.loc[sb_count1,'宿泊費金額'])
    #
                                        if df_customer1.loc[sb_count1,'かけつけ費合計'] == claim_total:
                                            mid1_result = mid1_result + 0
                                        else:
                                            mid1_result = mid1_result + 12 # "かけつけ費合計"不一致
    #
        
        #            else:
        #                mid1_result = 0 # 案件管理No一致無し
                    
                if mid1_result == 0:
                    st.write()
                    st.write(mid1," = OK")
                elif mid1_result == 1:
                    st.write()
                    st.write(mid1," = NG(顧客側リストに存在しない")
                elif mid1_result == 2:
                    st.write()
                elif mid1_result == 12:
                    st.write(mid1, " = かけつけ費合計不一致")
                elif mid1_result == 11:
                    st.write(mid1, " = 宿泊費金額不一致")
                elif mid1_result == 10:
                    st.write(mid1, " = かけつけ費金額/(往復)不一致")
                elif mid1_result == 21:
                    st.write(mid1, " = 宿泊費金額 / かけつけ費金額/(往復)不一致")
                elif mid1_result == 22:
                    st.write(mid1, " = かけつけ費金額/(往復) / かけつけ費合計 不一致")
                elif mid1_result == 23:
                    st.write(mid1, " = 宿泊費金額 / かけつけ費合計 不一致")
                elif mid1_result == 33:
                    st.write(mid1, " = 宿泊費金額 / かけつけ費金額/(往復) / かけつけ費合計 不一致")
                else:
                    st.write(mid1, "error = ", mid1_result)
                    
            st.subheader("処理が終わりました")
    
        else:
            st.subheader("チェック用ファイルが揃っていません")

def qr_code():
    import qrcode
    from PIL import Image
    # import cv2
    import streamlit as st
    import time

    input_text = st.text_input("QR変換したい文字列を入力して下さい：　", placeholder="ここにQRコードに変換したい文字を入力")

    img = qrcode.make(input_text)

    if st.checkbox("変換"):
        img.save('qrcode_test.jpg')
    
        image = Image.open('qrcode_test.jpg')
    
        st.image(image, caption='QR code')
        time.sleep(30)

def pdf_char():
    # import PyPDF2
    # from PyPDF2 import PdfFileReader
    # import streamlit as st
    
    # from pdfminer.pdfinterp import PDFResourceManager
    # rmgr = PDFResourceManager()
    
    # PDF本体情報を扱うための機能や属性を提供するクラス
    from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
    # 構文解析を実行するクラス
    from pdfminer.pdfparser import PDFParser
    import PyPDF2
    
    uploaded_file_conv1 = st.file_uploader("変換するファイル", type="pdf")
    st.write(uploaded_file_conv1)
    
    if st.checkbox("変換実施"):
        # file_conv1 = open(uploaded_file_conv1,"rb")
        # pdfparser = PDFParser()
        reader = PyPDF2.PdfFileReader(uploaded_file_conv1)
        st.write(reader)
        pageNo = reader.numPages
        st.write(pageNo)
        
        for i in range(pageNo):
            page = reader.getPage(i)
            st.write(page.extractText())

def web_check():
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    import time

    browser = webdriver.Chrome(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    browser.get('https://www.google.com/?hl=ja', options=options)
    time.sleep(5)
    browser.quit()

def web_table_get():
    import streamlit as st
    import pandas as pd

    st.subheader("Web頁内のテーブルを抽出")
    url = st.text_input("URL")
    table_no = st.text_input("何番目のテーブル？")

    if url != None:
        if st.checkbox("Table = " + table_no):
            table_no_int = int(table_no)
            # url = 'https://db.netkeiba.com/race/202005030211/'
            try:
                kekka = pd.read_html(url)[table_no_int]
                st.write(kekka)
            except:
                st.write('<span style="color:red">該当のURLには、指定のテーブルが見つかりませんでした。</span>', unsafe_allow_html=True)

def b_code():
    import streamlit as st
    from pybarcodes import JAN

    st.title("JAN/EAN/UPC バーコード作成")
    b_code = st.number_input(label="JANコード：45または49から始まる数字12桁", min_value=0, max_value=1000000000000, step=1)
    if b_code != 0:
        barcode = JAN(b_code)
        barcode.show()


if tool_name == "駆け付け費用チェック":
    st.write("駆け付け費用チェックが選択されました。")
    if st.checkbox("実行"):
        kaketsuke()
        
elif tool_name == "QR Code作成":
    if st.checkbox("実行"):
        qr_code()

elif tool_name == "バーコード作成":
    if st.checkbox("実行"):
        b_code()

elif tool_name == "PDFをキャラクタに変換(日本語不可)":
    if st.checkbox("実行"):
        pdf_char()
        
elif tool_name == "webからテーブル抽出":
    if st.checkbox("実行"):
        web_table_get()

elif tool_name == "選択肢3":
    if st.checkbox("実行"):
        web_check()
        
elif tool_name == '終了':
    if st.checkbox("終了？"):
        st.subheader("ブラウザを「x」等で閉じて下さい。")
        st.stop()
        exit()
        
elif tool_name == "音楽再生":
    if st.checkbox("音楽再生"):
        play_music = st.file_uploader("再生したいファイル(mp3 または wav)", type=("wav", "mp3"))
        st.write(play_music)

        if play_music != None:
            st.audio(play_music)

        
else:
    st.write("他のツールを選択して下さい。")

