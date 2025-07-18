from googletrans import Translator

translator = Translator()
result = translator.translate("سلام دنیا", src='fa', dest='en')
print(result.text)