import random
import time


last_password = ""
last_settings = ""

LOWERCASE = 'abcdefghijklmnopqrstuvwxyz'
UPPERCASE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
DIGITS = '0123456789'
SPECIALS = '!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

MIN_PASSWORD_LENGTH = 1
MAX_PASSWORD_LENGTH = 50    
DEFAULT_PASSWORD_LENGTH = 8

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
            length = input_integer(
                f"Введите длину пароля (от {MIN_PASSWORD_LENGTH} до {MAX_PASSWORD_LENGTH}, по умолчанию {DEFAULT_PASSWORD_LENGTH}): ",
                default=DEFAULT_PASSWORD_LENGTH,
                min_val=MIN_PASSWORD_LENGTH,
                max_val=MAX_PASSWORD_LENGTH
            )
            use_digits = input_yes_no("Включить цифры? (y/n): ")
            use_specials = input_yes_no("Включить спецсимволы? (y/n): ")
            use_uppercase = input_yes_no("Включить заглавные буквы? (y/n): ")
        
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
        
            print(f"Сгенерированный пароль: {password}")
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

def input_integer(prompt, default, min_val, max_val):
    # Запрашивает у пользователя целое число в диапазоне [min_val, max_val].
    # При пустом вводе возвращает значение по умолчанию.
    # При неверном вводе выводит сообщение и повторяет запрос.
    while True:
        user_input = input(prompt).strip()
        if user_input == "":
            return default
        try:
            value = int(user_input)
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Ошибка: число должно быть от {min_val} до {max_val}.")
        except ValueError:
            print("Ошибка: введите целое число.")

def input_yes_no(prompt): 
    # Запрашивает у пользователя ответ 'y' или 'n'.
    # Повторяет запрос до получения корректного ответа.
    # Возвращает True для 'y', False для 'n'.
    
    while True:
        answer = input(prompt).strip().lower()
        if answer in ('y', 'yes', 'да'):
            return True
        elif answer in ('n', 'no', 'нет'):
            return False
        else:
            print("Пожалуйста, введите 'y' или 'n'.")

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