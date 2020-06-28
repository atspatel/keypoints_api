import re
lang_unicode = {
    "Devanagari": {"length": 128, "offset": "0x0900"},
    # "Bengali":{"length":128 , "offset":"0x0980"},
    # "Oriya":{"length":   128 , "offset":"0x0B00"},
    # "Gurmukhi":{"length":128 , "offset":"0x0A00"},
    # "Gujarati":{"length": 128 , "offset":"0x0A80"},
    # "Tamil":{"length": 128 , "offset":"0x0B80"},
    # "Telugu":{"length": 128 , "offset":"0x0C00"},
    # "Kannada":{"length": 128 , "offset":"0x0C80"},
    # "Malayalam":{"length":128 , "offset":"0x0D00"}
}

regex_string = "0-9a-zA-Z"
for lang in lang_unicode:
    start = int(lang_unicode[lang]['offset'], 0)
    end = start + lang_unicode[lang]['length'] - 1
    regex_string += "%s-%s" % (chr(start), chr(end))


def text_to_query(text):
    return re.sub("[^%s]+" % (regex_string), "", text.lower())
