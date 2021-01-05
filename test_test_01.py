# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 09:21:16 2021

@author: hirkatayama
"""

import streamlit as st
import platform

st.title("This is a test app.")

print(platform.platform())
st.write(platform.platform())

