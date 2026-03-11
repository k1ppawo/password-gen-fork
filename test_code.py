import random
import time


last_password = ""
last_settings = ""



MIN_LEN = 1      
MAX_LEN = 50     

def menu():
    global last_password, last_settings
    while True:
        print("\n___ Генератор паролей ___")
        print("1. Сгенерировать пароль")
        print("2. Сохранить последний пароль в файл")
        print("3. Выход")
        choice = input("Выберите пункт: ")
        
        if choice == "1":
            
            len_str = input(f"Введите длину пароля (по умолчанию {8}): ")
            if len_str.strip() == "":
                length = 8
            else:
                length = int(len_str)  
            
            
            use_digits = input("Включить цифры? (y/n): ").lower() == 'y'
            use_specials = input("Включить спецсимволы? (y/n): ").lower() == 'y'
            use_uppercase = input("Включить заглавные буквы? (y/n): ").lower() == 'y'
            
            
            if not use_digits and not use_specials and not use_uppercase: 
                password = generate_lower(length)
                last_settings = "только строчные"
            elif use_digits and not use_specials and not use_uppercase:
                password = generate_lower_digits(length)
                last_settings = "строчные + цифры"
            elif not use_digits and use_specials and not use_uppercase:
                password = generate_lower_specials(length)
                last_settings = "строчные + спецсимволы"
            elif not use_digits and not use_specials and use_uppercase:
                password = generate_lower_upper(length)
                last_settings = "строчные + заглавные"
            elif use_digits and use_specials and not use_uppercase:
                password = generate_lower_digits_specials(length)
                last_settings = "строчные + цифры + спецсимволы"
            elif use_digits and not use_specials and use_uppercase:
                password = generate_lower_digits_upper(length)
                last_settings = "строчные + цифры + заглавные"
            elif not use_digits and use_specials and use_uppercase:
                password = generate_lower_specials_upper(length)
                last_settings = "строчные + спецсимволы + заглавные"
            elif use_digits and use_specials and use_uppercase:
                password = generate_all(length)
                last_settings = "все символы"
            else:
                password = generate_lower(length)
                last_settings = "только строчные (по умолчанию)"
            
            last_password = password
            print(f"Сгенерированный пароль: {password}")
            print(f"Настройки: {last_settings}")
        
        elif choice == "2":
            if last_password == "":
                print("Сначала сгенерируйте пароль!")
            else:
                filename = "passwords.txt"  
                try:
                    f = open(filename, "a")  
                    f.write(f"{time.ctime()} - {last_password} ({last_settings})\n")
                    f.close()
                    print(f"Пароль сохранён в файл {filename}")
                except:
                    print("Ошибка при сохранении в файл") 
        elif choice == "3":
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


def generate_lower(length):
    result = ""
    for i in range(length):
        char_code = random.randint(97, 122)
        result += chr(char_code)
    return result

def generate_lower_digits(length):
    result = ""
    for i in range(length):
        if random.randint(0, 1) == 0:
            char_code = random.randint(97, 122)
            result += chr(char_code)
        else:
            char_code = random.randint(48, 57) 
            result += chr(char_code)
    return result

def generate_lower_specials(length):
    result = ""
    for i in range(length):
        if random.randint(0, 1) == 0:
            char_code = random.randint(97, 122)
            result += chr(char_code)
        else:
            choice = random.randint(0, 3)
            if choice == 0:
                char_code = random.randint(33, 47)
            elif choice == 1:
                char_code = random.randint(58, 64)
            elif choice == 2:
                char_code = random.randint(91, 96)
            else:
                char_code = random.randint(123, 126)
            result += chr(char_code)
    return result

def generate_lower_upper(length):
    result = ""
    for i in range(length):
        if random.randint(0, 1) == 0:
            char_code = random.randint(97, 122)
            result += chr(char_code)
        else:
            char_code = random.randint(65, 90)  
            result += chr(char_code)
    return result

def generate_lower_digits_specials(length):
    result = ""
    for i in range(length):
        r = random.randint(0, 2) 
        if r == 0:
            char_code = random.randint(97, 122)
            result += chr(char_code)
        elif r == 1:
            char_code = random.randint(48, 57)
            result += chr(char_code)
        else:
            s = random.randint(0, 3)
            if s == 0:
                char_code = random.randint(33, 47)
            elif s == 1:
                char_code = random.randint(58, 64)
            elif s == 2:
                char_code = random.randint(91, 96)
            else:
                char_code = random.randint(123, 126)
            result += chr(char_code)
    return result

def generate_lower_digits_upper(length):
    result = ""
    for i in range(length):
        r = random.randint(0, 2)
        if r == 0:
            char_code = random.randint(97, 122)
            result += chr(char_code)
        elif r == 1:
            char_code = random.randint(48, 57)
            result += chr(char_code)
        else:
            char_code = random.randint(65, 90)
            result += chr(char_code)
    return result

def generate_lower_specials_upper(length):
    result = ""
    for i in range(length):
        r = random.randint(0, 2)
        if r == 0:
            char_code = random.randint(97, 122)
            result += chr(char_code)
        elif r == 1:
            s = random.randint(0, 3)
            if s == 0:
                char_code = random.randint(33, 47)
            elif s == 1:
                char_code = random.randint(58, 64)
            elif s == 2:
                char_code = random.randint(91, 96)
            else:
                char_code = random.randint(123, 126)
            result += chr(char_code)
        else:
            char_code = random.randint(65, 90)
            result += chr(char_code)
    return result

def generate_all(length):
    result = ""
    for i in range(length):
        r = random.randint(0, 3)  
        if r == 0:
            char_code = random.randint(97, 122)
            result += chr(char_code)
        elif r == 1:
            char_code = random.randint(48, 57)
            result += chr(char_code)
        elif r == 2:
            char_code = random.randint(65, 90)
            result += chr(char_code)
        else:
            s = random.randint(0, 3)
            if s == 0:
                char_code = random.randint(33, 47)
            elif s == 1:
                char_code = random.randint(58, 64)
            elif s == 2:
                char_code = random.randint(91, 96)
            else:
                char_code = random.randint(123, 126)
            result += chr(char_code)
    return result

if __name__ == "__main__":
    menu()