# -*- coding: utf-8 -*-
"""
Created on Fri Feb 3 9:13:11 2023

@author: hirkatayama
"""

import streamlit as st
import openai
import os
os.environ["OPENAI_API_KEY"] = "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"
os.environ["SERPAPI_API_KEY"] = "8b89d4589d2c3393cdeedc98aaba032b50aefe6302331642181c72f47c702223"

from langchain import OpenAI, ConversationChain
from langchain.chains.conversation.memory import ConversationSummaryMemory
from langchain.agents import initialize_agent
from langchain.agents import load_tools
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain import SerpAPIWrapper, LLMChain
import sys
import pyttsx3
import time
import speech_recognition as sr
import datetime as dt

global endtime, endFlag, speech_in_end, result_text, s
# 対話モデルを設定（多分これがGPT-3）
engine = "text-davinci-003"


# def main():
# Streamlit が対応している任意のオブジェクトを可視化する (ここでは文字列)
st.header("Chat GPT用")
#st.text_input("質問を記入して下さい。")
st.write('入力欄に質問等を書いてGoボタンを押して下さい。GPT-3が回答します。:')
st.write('Googleの検索結果も欲しい場合は、Google検索ボタンを「ON」にして下さい。:  ')
google_clicked = st.radio("Google検索", ["On", "OFF"], horizontal=True)
read_clicked = st.radio("読み上げ", ["OFF", "日本語", "English"], horizontal=True)
in_text = st.text_area("入力欄")
st.write('入力に対する操作を指定して下さい。Go:チャット、Clear:消去、Exit:処理終了')

col1, col2, col3 = st.columns(3)

with col1:
    go_clicked = st.button("Go", key=1)
with col2:
    clear_clicked = st.button("Clear", key=2)
with col3:
    exit_clicked = st.button("Exit", key=3)
st.write('以下の出力欄に、GPT-3の結果、指定によりGoogleの結果と併せて表示内容が表示されます。')
out_text = st.text_area("出力欄")

col4, col5 = st.columns(2)

with col4:
    Rja_clicked = st.button("Read 日本語", key=4)
with col5:
    Ren_clicked = st.button("Read Eng", key=5)

# GPT-3 をアクセスする
def interact_gpt3_once(prompt):
    global result_text, s
    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        temperature=0.2, # 0〜1.0, 大きいほどクリエイティブで小さいほど明確な応答をする。
        max_tokens=2048, # 生成されるトークン（文字列をトークンに変換して処理しているらしく、英語ならword数の3/4程度の値になるそう）の最大数

        # ここの引数は様々(沢山)有るので、必要に応じて以下を参照。
        # https://beta.openai.com/docs/api-reference/completions/create で確認して下さい。
    )

    # 結果を取得
    result_text = response.choices[0]["text"]
    print("\n〜〜〜〜 ここからGPTの回答 〜〜〜〜\n")
    print(result_text)
    # window["-OUTPUT-"].update(values["-OUTPUT-"] + result_text)
    # read_text()
    
    # Google search
    prompt1 = prompt
    if google_clicked == "On":
        llm = OpenAI(temperature=0)
        tools = load_tools(["serpapi", "llm-math"], llm=llm)
        conversation = ConversationChain(llm=llm,memory=ConversationSummaryMemory(llm=OpenAI()),verbose=True)
        agent = initialize_agent(tools,llm,agent="zero-shot-react-description",verbose=True)
        search = SerpAPIWrapper()
        tools = [Tool(name = "Search",func=search.run,description="useful for when you need to answer questions about current events")]
        prefix = """Have a conversation with a human, answering the following questions as best you can. You have access to the following tools:"""
        suffix = """Begin!"
        {chat_history}
        Question: {input}
        {agent_scratchpad}"""
        prompt = ZeroShotAgent.create_prompt(tools,prefix=prefix,suffix=suffix,input_variables=["input", "chat_history", "agent_scratchpad"])
        memory = ConversationBufferMemory(memory_key="chat_history")
        llm_chain = LLMChain(llm=OpenAI(temperature=0), prompt=prompt)
        agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
        agent_chain = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, memory=memory)

    print("\n〜〜〜〜 ここまでがGPTの回答 〜〜〜〜\n")
    # print("\n〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜\n")
    
    if google_clicked == "On":
        s = agent_chain.run(input=prompt1)
        print("\n〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜\n")
        print("\n〜〜〜〜 以下GPT-3 + Google検索からの回答  〜〜〜〜\n")
        print("[%s]"%s)
    else:
        s = ""

def read_text(read_flag):
    global result_text, s
    # 読み上げONの場合
    engine2 = pyttsx3.init()
    voices = engine2.getProperty('voices')

    if read_flag == 'on':
        if Ren_clicked == True:
            #声の選択
            engine2.setProperty('voice',voices[3].id)
            engine2.say(result_text)
            time.sleep(0.5)
            engine2.say("considering with google search," + s)

        else:
            #声の選択
            engine2.setProperty('voice',voices[0].id)
            engine2.say(result_text)
            time.sleep(0.5)
            engine2.say("グーグル検索と合わせた回答は、" + s)

        engine2.runAndWait()
        
    elif read_clicked == "日本語" or read_clicked == "English":
        engine2 = pyttsx3.init()
        voices = engine2.getProperty('voices')
        
        """
        # PC端末によって、搭載されているvoiceが異なるので、使用するvoiceを確認・変更する
        print(len(voices))
        for voice in voices:
            print(f'voice: {voice.name}')
            print(f'id: {voice.id}')
            print('')
        """
        
        if read_clicked == "English":
            #声の選択
            engine2.setProperty('voice',voices[3].id)
        else:
            #声の選択
            engine2.setProperty('voice',voices[0].id)
    
        # GPT 回答
        engine2.say(result_text)
        engine2.runAndWait()
        
        # GPT + Google の回答
        if s != "":
            time.sleep(0.5)
            engine2.say("ジーピィーティとグーグル検索結果からの回答は、" + s)
            engine2.runAndWait()
    
    else:
        return

"""
if __name__ == '__main__':
    main()
"""

try:
    speech_in_end = False # 音声認識終了フラグを初期設定(オフ)
    while True:
        #　ユーザからの入力を待ちます。入力があると、次の処理に進みます。
        #event, values = window.read()
        """
        if event == " SR  ":
            endtime = dt.datetime.now() + dt.timedelta( seconds = 30 )
            speech_in_end = False # 音声での入力必要
            endFlag = False # 音声入力終了フラグをクリア
            speechToText()
            # speech_in_end = True   # 音声入力済
         """
         
        if go_clicked == " Go  ":
            
            
            s = in_text # 入力欄の文字列読込
            # print("INPUT= " + s)
            if s == "":
                out_text = "入力欄エラー" + "\n" + "入力欄に何も見つかりません。もう一度設定してからやり直して下さい。"
                
            else:
                prompt = s # GPT-3に渡す文字列
            
                # GPT-3実行
                interact_gpt3_once(prompt) # 結果欄に出力
                print("\n〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜〜\n")
                
                """
                loop_time = 0
                number_of_loop = 300
                while loop_time < number_of_loop:
                    if "\n〜〜〜〜〜〜〜〜\n" in values["-OUTPUT-"]:
                        read_text()
                        break
                    else:
                        loop_time +=1
                        time.sleep(1)
                """
                read_flag = 'off'
                read_text(read_flag)

        """
        engine1 = pyttsx3.init()
        engine1.say(prompt)
        engine1.runAndWait()
        """
        
        #　ウィンドウの右上の×を押したときの処理、「Exit」・[Clear]ボタンを押したときの処理
        #if go_click == "Go":
        #    break
        if exit_clicked == 'Exit ':
            break
        #　「Clear」ボタンを押したときの処理
        if clear_clicked == 'Clear':
            #　「-IN-」領域を、空白で更新します。
            input_text = ""
            #　「-OUTPUT-」領域を、空白で更新します。
            out_text = ''
            # 音声入力を再度可能とする
            speech_in_end = False
            endFlag = False
        
        # 結果欄の読み上げ
        if Rja_clicked == True or Ren_clicked == True:
            # result_text = values['-OUTPUT-']
            read_flag = 'on' # 最後の出力後に最後の結果のみを読み上げ
            read_text(read_flag)
            
except:
    out_text = "エラー発生のため、処理を終了します。"

