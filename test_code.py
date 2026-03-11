import random
import time


last_password = ""
last_settings = ""

LOWERCASE = 'abcdefghijklmnopqrstuvwxyz'
UPPERCASE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
DIGITS = '0123456789'
SPECIALS = '!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

MIN_LEN = 1      
MAX_LEN = 50     

def menu():
    # реализует интерактивное консольное меню генератора паролей: 
    # позволяет пользователю генерировать пароли с заданными настройками, 
    # cохранять последний сгенерированный пароль в файл или выходить из программы

    global last_password, last_settings
    while True:
        print("\n___ Генератор паролей ___")
        print("1. Сгенерировать пароль")
        print("2. Сохранить последний пароль в файл")
        print("3. Выход")
        choice = input("\nВыберите пункт: ")

        if choice == "1":
            
            len_str = input(f"\nВведите длину пароля (по умолчанию {8}): ")
            if len_str.strip() == "":
                length = 8
            else:
                length = int(len_str)

            
            use_digits = input("Включить цифры? (y/n): ").lower() == 'y'
            use_specials = input("Включить спецсимволы? (y/n): ").lower() == 'y'
            use_uppercase = input("Включить заглавные буквы? (y/n): ").lower() == 'y'

            
            password = generate_password(length, use_uppercase, use_digits, use_specials)
            last_password = password

            
            settings_parts = []
            if use_uppercase:
                settings_parts.append("заглавные")
            if use_digits:
                settings_parts.append("цифры")
            if use_specials:
                settings_parts.append("спецсимволы")
            if not settings_parts:
                last_settings = "только строчные"
            else:
                last_settings = "строчные + " + " + ".join(settings_parts)

            print(f"\nСгенерированный пароль: {password}")
            print(f"Настройки: {last_settings}")

        elif choice == "2":
            
            if last_password == "":
                print("Сначала сгенерируйте пароль!")
            else:
                filename = "passwords.txt"
                try:
                    with open(filename, "a") as f:
                        f.write(f"{time.ctime()} - {last_password} ({last_settings})\n")
                    print(f"Пароль сохранён в файл {filename}")
                except:
                    print("Ошибка при сохранении в файл")
        elif choice == "3":
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


def generate_password(length, use_uppercase=False, use_digits=False, use_specials=False):
    
    # Генерирует пароль заданной длины из строчных букв (всегда) и,
    # при необходимости, из заглавных букв, цифр и спецсимволов.
    
    chars = LOWERCASE
    if use_uppercase:
        chars += UPPERCASE
    if use_digits:
        chars += DIGITS
    if use_specials:
        chars += SPECIALS

    password = ''.join(random.choice(chars) for _ in range(length))
    return password

if __name__ == "__main__":
    menu()