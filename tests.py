import unittest
from unittest.mock import patch, mock_open
import random
import string
import tempfile
import os


import test_code as pwg


class TestGeneratorFunctions(unittest.TestCase):
    """Тесты для отдельных функций генерации паролей."""

    def test_generate_lower(self):
        """Только строчные буквы."""
        length = 10
        pwd = pwg.generate_lower(length)
        self.assertEqual(len(pwd), length)
        for ch in pwd:
            self.assertIn(ch, string.ascii_lowercase)

    def test_generate_lower_digits(self):
        """Строчные + цифры."""
        length = 15
        pwd = pwg.generate_lower_digits(length)
        self.assertEqual(len(pwd), length)
        allowed = string.ascii_lowercase + string.digits
        for ch in pwd:
            self.assertIn(ch, allowed)

    def test_generate_lower_specials(self):
        """Строчные + спецсимволы."""
        length = 12
        pwd = pwg.generate_lower_specials(length)
        self.assertEqual(len(pwd), length)
        allowed = string.ascii_lowercase + ''.join(chr(i) for i in range(33, 48)) \
                  + ''.join(chr(i) for i in range(58, 65)) \
                  + ''.join(chr(i) for i in range(91, 97)) \
                  + ''.join(chr(i) for i in range(123, 127))
        for ch in pwd:
            self.assertIn(ch, allowed)

    def test_generate_lower_upper(self):
        """Строчные + заглавные."""
        length = 20
        pwd = pwg.generate_lower_upper(length)
        self.assertEqual(len(pwd), length)
        allowed = string.ascii_letters
        for ch in pwd:
            self.assertIn(ch, allowed)

    def test_generate_lower_digits_specials(self):
        """Строчные + цифры + спецсимволы."""
        length = 8
        pwd = pwg.generate_lower_digits_specials(length)
        self.assertEqual(len(pwd), length)
        allowed = string.ascii_lowercase + string.digits + \
                  ''.join(chr(i) for i in range(33, 48)) + \
                  ''.join(chr(i) for i in range(58, 65)) + \
                  ''.join(chr(i) for i in range(91, 97)) + \
                  ''.join(chr(i) for i in range(123, 127))
        for ch in pwd:
            self.assertIn(ch, allowed)

    def test_generate_lower_digits_upper(self):
        """Строчные + цифры + заглавные."""
        length = 10
        pwd = pwg.generate_lower_digits_upper(length)
        self.assertEqual(len(pwd), length)
        allowed = string.ascii_letters + string.digits
        for ch in pwd:
            self.assertIn(ch, allowed)

    def test_generate_lower_specials_upper(self):
        """Строчные + спецсимволы + заглавные."""
        length = 10
        pwd = pwg.generate_lower_specials_upper(length)
        self.assertEqual(len(pwd), length)
        allowed = string.ascii_letters + \
                  ''.join(chr(i) for i in range(33, 48)) + \
                  ''.join(chr(i) for i in range(58, 65)) + \
                  ''.join(chr(i) for i in range(91, 97)) + \
                  ''.join(chr(i) for i in range(123, 127))
        for ch in pwd:
            self.assertIn(ch, allowed)

    def test_generate_all(self):
        """Все типы символов."""
        length = 15
        pwd = pwg.generate_all(length)
        self.assertEqual(len(pwd), length)
        allowed = string.ascii_letters + string.digits + \
                  ''.join(chr(i) for i in range(33, 48)) + \
                  ''.join(chr(i) for i in range(58, 65)) + \
                  ''.join(chr(i) for i in range(91, 97)) + \
                  ''.join(chr(i) for i in range(123, 127))
        for ch in pwd:
            self.assertIn(ch, allowed)

    def test_all_functions_different_outputs(self):
        """Проверка, что при одном seed функции дают разные результаты."""
        random.seed(42)
        pwd1 = pwg.generate_lower(10)
        random.seed(42)
        pwd2 = pwg.generate_lower_digits(10)
        self.assertNotEqual(pwd1, pwd2)


class TestGlobalState(unittest.TestCase):
    """Тесты для глобальных переменных last_password и last_settings."""

    def setUp(self):
        pwg.last_password = ""
        pwg.last_settings = ""

    @patch('builtins.input')
    def test_menu_generate_lower_only(self, mock_input):
        """Выбор только строчных (все ответы 'n')."""
        mock_input.side_effect = ["1", "", "n", "n", "n", "3"]
        with patch('builtins.print'):
            pwg.menu()
        self.assertNotEqual(pwg.last_password, "")
        self.assertEqual(pwg.last_settings, "только строчные")

    @patch('builtins.input')
    def test_menu_generate_all(self, mock_input):
        """Все опции включены (все ответы 'y')."""
        mock_input.side_effect = ["1", "12", "y", "y", "y", "3"]
        with patch('builtins.print'):
            pwg.menu()
        self.assertEqual(len(pwg.last_password), 12)
        self.assertEqual(pwg.last_settings, "все символы")

    @patch('builtins.input')
    def test_menu_generate_digits_specials(self, mock_input):
        """Только цифры и спецсимволы (без заглавных)."""
        mock_input.side_effect = ["1", "8", "y", "y", "n", "3"]
        with patch('builtins.print'):
            pwg.menu()
        self.assertEqual(pwg.last_settings, "строчные + цифры + спецсимволы")


class TestFileSaving(unittest.TestCase):
    """Тесты для сохранения в файл."""

    def setUp(self):
        pwg.last_password = "testpass"
        pwg.last_settings = "тестовый пароль"

    @patch('builtins.input')
    @patch("builtins.open", new_callable=mock_open)
    def test_menu_save_after_generation(self, mock_file, mock_input):
        """Генерация, затем сохранение."""
        pwg.last_password = ""  # сброс
        mock_input.side_effect = ["1", "5", "n", "n", "n", "2", "3"]
        with patch('builtins.print'):
            pwg.menu()
        mock_file.assert_called_once_with("passwords.txt", "a")
        handle = mock_file()
        handle.write.assert_called_once()
        written_text = handle.write.call_args[0][0]
        self.assertIn(pwg.last_password, written_text)

    @patch('builtins.input')
    @patch("builtins.open", side_effect=IOError("Disk error"))
    def test_menu_save_io_error(self, mock_file, mock_input):
        """Ошибка ввода-вывода при сохранении."""
        pwg.last_password = ""  # сброс
        mock_input.side_effect = ["1", "5", "n", "n", "n", "2", "3"]
        with patch('builtins.print') as mock_print:
            pwg.menu()
        mock_print.assert_any_call("Ошибка при сохранении в файл")


class TestInputHandling(unittest.TestCase):
    """Тесты для ввода данных (без меню)."""

    @patch('builtins.input')
    def test_menu_invalid_choice(self, mock_input):
        """Неверный пункт меню."""
        mock_input.side_effect = ["99", "3"]
        with patch('builtins.print') as mock_print:
            pwg.menu()
        mock_print.assert_any_call("Неверный выбор. Попробуйте снова.")

    @patch('builtins.input')
    def test_menu_length_non_numeric(self, mock_input):
        """Ввод нечисловой длины (должно вызвать ValueError)."""
        mock_input.side_effect = ["1", "abc", "3"]
        with self.assertRaises(ValueError):
            pwg.menu()


if __name__ == "__main__":
    unittest.main()