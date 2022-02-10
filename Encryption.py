

def encrypt(text):
    result = ""
    for i in range(len(text)):
        char = text[i]
        if char.isupper():
            result += chr((ord(char) + 2 - 65) % 26 + 65)
        else:
            result += chr((ord(char) + 2 - 97) % 26 + 97)
    return result


def decrypt(text):
    result = ""
    for i in range(len(text)):
        char = text[i]
        if char.isupper():
            result += chr((ord(char) - 2 - 65) % 26 + 65)
        else:
            result += chr((ord(char) - 2 - 97) % 26 + 97)
    return result
