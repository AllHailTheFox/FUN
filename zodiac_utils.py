from datetime import datetime

def get_western_zodiac(month, day):
    zodiacs = [
        ("Capricorn", 1, 19), ("Aquarius", 2, 18), ("Pisces", 3, 20),
        ("Aries", 4, 19), ("Taurus", 5, 20), ("Gemini", 6, 20),
        ("Cancer", 7, 22), ("Leo", 8, 22), ("Virgo", 9, 22),
        ("Libra", 10, 22), ("Scorpio", 11, 21), ("Sagittarius", 12, 21),
        ("Capricorn", 12, 31)
    ]
    zodiac_facts = {
        "Aries": "Aries are known for their fiery energy and leadership qualities. They're natural go-getters!",
        "Taurus": "Taurus individuals are grounded and love comfort — think good food, cozy spaces, and loyal vibes.",
        "Gemini": "Geminis are curious and adaptable — they love variety and have a way with words.",
        "Cancer": "Cancers are deeply intuitive and emotional. They’re the caregivers of the zodiac.",
        "Leo": "Leos love to shine. They're confident, charismatic, and often take center stage.",
        "Virgo": "Virgos are analytical and detail-oriented. They thrive on order and practicality.",
        "Libra": "Libras seek harmony and beauty. They value fairness and often make great diplomats.",
        "Scorpio": "Scorpios are intense and passionate. They’re often mysterious but fiercely loyal.",
        "Sagittarius": "Sagittarians are adventurous free spirits. They love exploring new ideas and places.",
        "Capricorn": "Capricorns are disciplined and ambitious. They climb steadily toward their goals.",
        "Aquarius": "Aquarians are forward-thinking and quirky. They often think outside the box.",
        "Pisces": "Pisces are dreamy and empathetic. They're deeply artistic and emotionally intelligent."
    }
    for sign, m, d in zodiacs:
        if (month == m and day <= d) or (month == m - 1 and day > d):
            return sign, zodiac_facts[sign]
    return "Capricorn", zodiac_facts["Capricorn"]

def get_chinese_zodiac(year):
    animals = [
        "Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
        "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"
    ]
    chinese_zodiac_facts = {
        "Rat": "Rats are clever and quick-witted. They’re resourceful and often good with money.",
        "Ox": "Oxen are hardworking, reliable, and determined — slow and steady wins the race.",
        "Tiger": "Tigers are brave, competitive, and confident. They’re natural-born leaders.",
        "Rabbit": "Rabbits are gentle, elegant, and kind-hearted. They value peace and harmony.",
        "Dragon": "Dragons are powerful, energetic, and charismatic. The only mythical animal in the zodiac!",
        "Snake": "Snakes are wise, graceful, and mysterious. They often have deep intuition.",
        "Horse": "Horses are active, energetic, and love freedom. They’re social and full of life.",
        "Goat": "Goats are calm, creative, and compassionate. They prefer a peaceful, artistic life.",
        "Monkey": "Monkeys are playful, curious, and intelligent. They love solving problems.",
        "Rooster": "Roosters are observant, confident, and hardworking. They’re known for being punctual.",
        "Dog": "Dogs are loyal, honest, and kind. They are trustworthy and protective of loved ones.",
        "Pig": "Pigs are generous, sincere, and enjoy life’s pleasures. They have a big heart."
    }
    index = (year - 1900) % 12
    animal = animals[index]
    return animal, chinese_zodiac_facts[animal]
