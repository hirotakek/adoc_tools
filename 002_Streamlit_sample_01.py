# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 13:56:00 2020

@author: hirkatayama
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
# import os
# import openpyxl as opx
from PIL import Image
# import mapboxgl

# progress
st.title("プログレスバーの表示")
"start"
latest_iteration = st.empty()
bar = st.progress(0)
for i in range(100):
    latest_iteration.text(f"Iteration {i+1}")
    bar.progress(i+1)
    time.sleep(0.01)
"Done!!!"

# 2x3表、画像選択表示
st.title('Streamlit 使い方サンプル')
uploaded_file = st.file_uploader("choose an image", type="jpg")
# uploaded_excel_file = st.file_uploader("choose an image", type="xlsx")

if st.checkbox("data presence"):
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption="uploaded image", use_column_width=True)
st.write("data frame")
df = pd.DataFrame({"First column": [1, 2, 3, 4], "Second column": [10, 20, 30, 40]})
st.dataframe(df, 400, 400)
print('OK')

# マジックコマンド　：　Pythonコード表示
"""
```python

import streamlit as st
import pandas as pd
import numpy as np

```
"""

# Graph 描画
dg = pd.DataFrame(
    np.random.rand(20,3),
    columns=["a", "b", "c"]
)

# ２カラム表示
left_column, right_column = st.beta_columns(2)
button = left_column.button("右側にグラフを表示")
with right_column:
    if button:
        st.line_chart(dg)

# st.area_chart(dg)
# st.bar_chart(dg)

# Map
dm = pd.DataFrame({"lat":[35.702202], "lon":[139.414096]})
# map.token("pk.eyJ1IjoiaGlyb3Rha2VrMDYiLCJhIjoiY2tpbzI2NGgwMTh5dTJyanpxczBtNGZsdyJ9.8WcugSD91Zq4M5KFqPzwvg")
st.map(dm)

# Interactive Wedgets
# input box

st.title("interactive wedgets")

text = st.text_input("あなたの趣味を教えて下さい。")
# text = st.sidebar.text_input("あなたの趣味を教えて下さい。") # sidbar表示の場合
"あなたの趣味:",text
condition = st.slider("あなたの調子は？", 0, 100, 50)
# condition = st..sidebar.slider("あなたの調子は？", 0, 100, 50) # sidbar表示の場合
"あなたの調子:", condition

# expander
expander1 = st.beta_expander("質問")
expander1.write("回答")

