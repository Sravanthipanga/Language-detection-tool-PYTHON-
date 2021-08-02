# Language-detection-tool-PYTHON-
its all about the language detection that used to code 

!pip install langdetect
!pip3 install googletrans==3.1.0a0
from langdetect import detect
from googletrans import Translator, constants
from pprint import pprint
text = input("Enter any text in any language: ")
print(detect(text))
print(' ')
translator = Translator()
translation = translator.translate(text)
print(f"{translation.origin} ({translation.src}) --> {translation.text} ({translation.dest})")
