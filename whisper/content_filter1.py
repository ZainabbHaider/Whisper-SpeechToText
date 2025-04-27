# content_filter.py

import re

URDU_TOXIC_KEYWORDS = [
    # Vulgar/abusive
    "حرامی", "کتا", "حرامزاده", "لعنتی", "حرام", "بکواس", "گالی", "گند", "چپ", "مار", "کمینہ",
    "ناجائز", "خبیث", "کمینے", "مکار", "شیطان", "پاگل", "چوتیا", "بے غیرت", "فاحشہ", "بدمعاش", "نیچ",

    # Hate/religious hate
    "کافر", "دہشتگرد", "فساد", "نفرت", "ظالم", "تعصب", "قوم پرست", "توہین", "ملحد",

    # Harassment/threats
    "قتل", "مار ڈالوں گا", "زنا", "ریپ", "دھمکی", "چھیڑ"",

    # Mild inappropriate
    "اوئے", "بے ادب", "بے شرم", "بے حیا", "شرم کرو", "گدھا", "گھٹیا", "نکل جا", "چپ کر", "دفع ہو جا",

    # Slang/insults
   "لوفر", "چول", "بھڑو
]

def is_toxic_urdu(text):
    text = text.strip().lower()
    for word in URDU_TOXIC_KEYWORDS:
        if re.search(rf"\b{re.escape(word)}\b", text):
            return True
    return False
