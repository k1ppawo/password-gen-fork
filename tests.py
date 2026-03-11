import unittest
from unittest.mock import patch, mock_open
import string
import tempfile
import os
import time
from datetime import datetime

# Импортируем тестируемые модули
from test_code import (
    PasswordManager, MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH, DEFAULT_PASSWORD_LENGTH,
    input_integer, input_yes_no, LOWERCASE, UPPERCASE, DIGITS, SPECIALS
)


class TestPasswordManager(unittest.TestCase):
    def setUp(self):
        """Создаёт менеджер перед каждым тестом."""
        self.manager = PasswordManager()

    def test_generate_only_lowercase(self):
        """Генерация пароля только из строчных букв."""
        length = 10
        pwd = self.manager.generate(length)
        self.assertEqual(len(pwd), length)
        # Все символы должны быть из string.ascii_lowercase
        self.assertTrue(all(c in string.ascii_lowercase for c in pwd))
        self.assertEqual(self.manager.last_password, pwd)

    def test_generate_with_uppercase(self):
        """Генерация пароля со строчными и заглавными буквами."""
        length = 15
        pwd = self.manager.generate(length, use_uppercase=True)
        self.assertEqual(len(pwd), length)
        # Допустимые символы: строчные + заглавные
        allowed = string.ascii_lowercase + string.ascii_uppercase
        self.assertTrue(all(c in allowed for c in pwd))

    def test_generate_with_digits(self):
        """Генерация пароля со строчными и цифрами."""
        length = 12
        pwd = self.manager.generate(length, use_digits=True)
        self.assertEqual(len(pwd), length)
        allowed = string.ascii_lowercase + string.digits
        self.assertTrue(all(c in allowed for c in pwd))

    def test_generate_with_specials(self):
        """Генерация пароля со строчными и спецсимволами."""
        length = 8
        pwd = self.manager.generate(length, use_specials=True)
        self.assertEqual(len(pwd), length)
        allowed = string.ascii_lowercase + SPECIALS
        self.assertTrue(all(c in allowed for c in pwd))

    def test_generate_all_options(self):
        """Генерация пароля со всеми типами символов."""
        length = 20
        pwd = self.manager.generate(length, use_uppercase=True, use_digits=True, use_specials=True)
        self.assertEqual(len(pwd), length)
        allowed = LOWERCASE + UPPERCASE + DIGITS + SPECIALS
        self.assertTrue(all(c in allowed for c in pwd))

    def test_generate_invalid_length(self):
        """Передача недопустимой длины (меньше MIN_PASSWORD_LENGTH)."""
        with self.assertRaises(ValueError):
            self.manager.generate(0)

    def test_format_settings(self):
        """Проверка формирования строки настроек."""
        # Только строчные
        self.assertEqual(PasswordManager._format_settings(False, False, False), "только строчные")
        # Строчные + заглавные
        self.assertEqual(PasswordManager._format_settings(True, False, False), "строчные + заглавные")
        # Строчные + цифры
        self.assertEqual(PasswordManager._format_settings(False, True, False), "строчные + цифры")
        # Строчные + спецсимволы
        self.assertEqual(PasswordManager._format_settings(False, False, True), "строчные + спецсимволы")
        # Все вместе
        self.assertEqual(PasswordManager._format_settings(True, True, True), "строчные + заглавные + цифры + спецсимволы")
        # Комбинации
        self.assertEqual(PasswordManager._format_settings(True, True, False), "строчные + заглавные + цифры")
        self.assertEqual(PasswordManager._format_settings(True, False, True), "строчные + заглавные + спецсимволы")

    def test_last_settings_after_generation(self):
        """Проверка, что last_settings обновляется после генерации."""
        self.manager.generate(5, use_uppercase=True, use_digits=False, use_specials=True)
        expected = PasswordManager._format_settings(True, False, True)
        self.assertEqual(self.manager.last_settings, expected)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_to_file_success(self, mock_file):
        """Сохранение пароля в файл (мок open)."""
        # Сначала сгенерируем пароль
        pwd = self.manager.generate(8)
        result = self.manager.save_to_file("test.txt")
        # Проверяем, что open вызван с правильными аргументами
        mock_file.assert_called_once_with("test.txt", "a")
        # Проверяем, что в файл что-то записано
        handle = mock_file()
        handle.write.assert_called_once()
        # Проверяем сообщение об успехе
        self.assertIn("Пароль сохранён", result)

    def test_save_to_file_without_generation(self):
        """Попытка сохранить, когда пароль ещё не сгенерирован."""
        result = self.manager.save_to_file()
        self.assertEqual(result, "Сначала сгенерируйте пароль!")

    @patch("builtins.open", side_effect=IOError("Disk full"))
    def test_save_to_file_io_error(self, mock_file):
        """Обработка ошибки ввода-вывода при сохранении."""
        self.manager.generate(8)
        result = self.manager.save_to_file()
        self.assertIn("Ошибка ввода-вывода: Disk full", result)

    # Опционально: тест с реальным временным файлом (для проверки записи)
    def test_save_to_file_real_file(self):
        """Тест с реальным временным файлом."""
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
            filename = tmp.name
        try:
            self.manager.generate(10)
            result = self.manager.save_to_file(filename)
            self.assertIn("Пароль сохранён", result)
            # Проверим, что файл не пустой
            with open(filename, "r") as f:
                content = f.read()
            self.assertIn(self.manager.last_password, content)
        finally:
            os.unlink(filename)


class TestInputFunctions(unittest.TestCase):
    """Тесты для функций ввода с клавиатуры."""

    @patch('builtins.input')
    def test_input_integer_default(self, mock_input):
        """Ввод целого числа с использованием значения по умолчанию."""
        mock_input.return_value = ""
        result = input_integer("Введите число: ", default=5, min_val=1, max_val=10)
        self.assertEqual(result, 5)

    @patch('builtins.input')
    def test_input_integer_valid(self, mock_input):
        """Ввод корректного целого числа в диапазоне."""
        mock_input.return_value = "7"
        result = input_integer("Введите число: ", default=5, min_val=1, max_val=10)
        self.assertEqual(result, 7)

    @patch('builtins.input')
    def test_input_integer_invalid_then_valid(self, mock_input):
        """Ввод некорректного значения, затем корректного."""
        mock_input.side_effect = ["abc", "15", "8"]
        result = input_integer("Введите число: ", default=5, min_val=1, max_val=10)
        self.assertEqual(result, 8)

    @patch('builtins.input')
    def test_input_yes_no_yes(self, mock_input):
        """Ввод 'y' (True)."""
        mock_input.return_value = "y"
        result = input_yes_no("Продолжить? (y/n): ")
        self.assertTrue(result)

    @patch('builtins.input')
    def test_input_yes_no_no(self, mock_input):
        """Ввод 'n' (False)."""
        mock_input.return_value = "n"
        result = input_yes_no("Продолжить? (y/n): ")
        self.assertFalse(result)

    @patch('builtins.input')
    def test_input_yes_no_invalid_then_valid(self, mock_input):
        """Ввод некорректного ответа, затем корректного."""
        mock_input.side_effect = ["maybe", "yes"]
        result = input_yes_no("Продолжить? (y/n): ")
        self.assertTrue(result)


class TestMenuIntegration(unittest.TestCase):
    """Интеграционные тесты для меню (с подменой ввода)."""

    @patch('test_code.input_integer')
    @patch('test_code.input_yes_no')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_menu_generate_and_save(self, mock_print, mock_input, mock_yes_no, mock_integer):
        """Тест сценария: генерация пароля и сохранение."""
        # Имитация выбора пунктов меню
        mock_input.side_effect = ["1", "2", "3"]  # 1 - генерация, 2 - сохранение, 3 - выход
        # Настройка возвращаемых значений для функций ввода параметров
        mock_integer.return_value = 10  # длина пароля
        mock_yes_no.side_effect = [True, False, True]  # цифры: да, спецсимволы: нет, заглавные: да

        manager = PasswordManager()
        with patch.object(manager, 'generate', return_value="Abcd1234") as mock_generate:
            with patch.object(manager, 'save_to_file', return_value="Пароль сохранён") as mock_save:
                # Запускаем меню (оно будет работать, пока не дойдёт до выхода)
                from test_code import menu
                try:
                    menu(manager)
                except SystemExit:
                    pass  # menu не вызывает exit, просто break

                # Проверяем, что generate был вызван с правильными параметрами
                mock_generate.assert_called_once_with(10, True, True, False)  # use_uppercase, use_digits, use_specials
                # Проверяем, что save_to_file был вызван
                mock_save.assert_called_once()
                # Проверяем, что было напечатано сообщение о сохранении
                mock_print.assert_any_call("Пароль сохранён")

    @patch('builtins.input')
    @patch('builtins.print')
    def test_menu_invalid_choice(self, mock_print, mock_input):
        """Тест выбора несуществующего пункта меню."""
        mock_input.side_effect = ["4", "3"]  # неверный выбор, затем выход

        manager = PasswordManager()
        from test_code import menu
        try:
            menu(manager)
        except SystemExit:
            pass

        # Проверяем, что было напечатано сообщение об ошибке
        mock_print.assert_any_call("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    unittest.main()