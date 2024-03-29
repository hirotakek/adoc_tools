# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 09:26:08 2022

@author: hirkatayama
"""

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
                                st.write(mid1, " = OK")
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
                                    st.write(mid1, " = OK")
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
                                        st.write(mid1, " = OK")
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
