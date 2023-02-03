# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 09:13:11 2023

@author: hirkatayama
"""

import streamlit as st

# def main():
# Streamlit が対応している任意のオブジェクトを可視化する (ここでは文字列)
st.header("Chat GPT用")
#st.text_input("質問を記入して下さい。")
st.caption('入力欄に質問等を書いてGoボタンを押して下さい。GPT-3が回答します。:')
st.write('Googleの検索結果も欲しい場合は、Google検索ボタンを「ON」にして下さい。:  ')

google_clicked = st.radio("Google検索", ["On", "OFF"], horizontal=True)
read_clicked = st.radio("読み上げ", ["OFF", "日本語", "English"], horizontal=True)
go_clicked = st.button("Go")
clear_clicked = st.button("Clear")
exit_clicked = st.button("Exit")
in_text = st.text_area("入力欄")
out_text = st.text_area("出力欄")


    


"""
if __name__ == '__main__':
    main()
"""