import unittest
from unittest.mock import patch, mock_open
import random
import string
import time


import test_code as pg


class TestPasswordManager(unittest.TestCase):
    """Тесты для класса PasswordManager."""

    def setUp(self):
        self.manager = pg.PasswordManager()

    def test_generate_only_lowercase(self):
        pwd = self.manager.generate(10)
        self.assertEqual(len(pwd), 10)
        self.assertTrue(all(c in pg.LOWERCASE for c in pwd))
        self.assertEqual(self.manager.last_password, pwd)
        self.assertEqual(self.manager.last_settings, "только строчные")

    def test_generate_with_uppercase(self):
        pwd = self.manager.generate(15, use_uppercase=True)
        allowed = pg.LOWERCASE + pg.UPPERCASE
        self.assertTrue(all(c in allowed for c in pwd))
        self.assertEqual(self.manager.last_settings, "строчные + заглавные")

    def test_generate_with_digits(self):
        pwd = self.manager.generate(12, use_digits=True)
        allowed = pg.LOWERCASE + pg.DIGITS
        self.assertTrue(all(c in allowed for c in pwd))
        self.assertEqual(self.manager.last_settings, "строчные + цифры")

    def test_generate_with_specials(self):
        pwd = self.manager.generate(8, use_specials=True)
        allowed = pg.LOWERCASE + pg.SPECIALS
        self.assertTrue(all(c in allowed for c in pwd))
        self.assertEqual(self.manager.last_settings, "строчные + спецсимволы")

    def test_generate_all_options(self):
        pwd = self.manager.generate(20, use_uppercase=True, use_digits=True, use_specials=True)
        allowed = pg.LOWERCASE + pg.UPPERCASE + pg.DIGITS + pg.SPECIALS
        self.assertTrue(all(c in allowed for c in pwd))
        self.assertEqual(self.manager.last_settings, "строчные + заглавные + цифры + спецсимволы")

    def test_generate_uppercase_and_digits(self):
        pwd = self.manager.generate(8, use_uppercase=True, use_digits=True)
        allowed = pg.LOWERCASE + pg.UPPERCASE + pg.DIGITS
        self.assertTrue(all(c in allowed for c in pwd))
        self.assertEqual(self.manager.last_settings, "строчные + заглавные + цифры")

    def test_generate_invalid_length(self):
        with self.assertRaises(ValueError):
            self.manager.generate(0)

    def test_format_settings(self):
        self.assertEqual(pg.PasswordManager._format_settings(False, False, False), "только строчные")
        self.assertEqual(pg.PasswordManager._format_settings(True, False, False), "строчные + заглавные")
        self.assertEqual(pg.PasswordManager._format_settings(False, True, False), "строчные + цифры")
        self.assertEqual(pg.PasswordManager._format_settings(False, False, True), "строчные + спецсимволы")
        self.assertEqual(pg.PasswordManager._format_settings(True, True, False), "строчные + заглавные + цифры")
        self.assertEqual(pg.PasswordManager._format_settings(True, False, True), "строчные + заглавные + спецсимволы")
        self.assertEqual(pg.PasswordManager._format_settings(False, True, True), "строчные + цифры + спецсимволы")
        self.assertEqual(pg.PasswordManager._format_settings(True, True, True), "строчные + заглавные + цифры + спецсимволы")

    def test_save_to_file_no_password(self):
        success, message = self.manager.save_to_file()
        self.assertFalse(success)
        self.assertEqual(message, "Сначала сгенерируйте пароль!")

    @patch("builtins.open", new_callable=mock_open)
    def test_save_to_file_success(self, mock_file):
        self.manager.generate(8)
        success, message = self.manager.save_to_file("test.txt")
        self.assertTrue(success)
        self.assertIn("Пароль сохранён", message)
        mock_file.assert_called_once_with("test.txt", "a")
        handle = mock_file()
        handle.write.assert_called_once()
        written = handle.write.call_args[0][0]
        self.assertIn(self.manager.last_password, written)
        self.assertIn(self.manager.last_settings, written)

    @patch("builtins.open", side_effect=IOError("Disk error"))
    def test_save_to_file_io_error(self, mock_file):
        self.manager.generate(8)
        success, message = self.manager.save_to_file()
        self.assertFalse(success)
        self.assertEqual(message, "Ошибка: Disk error")

    @patch("builtins.open", side_effect=Exception("Unexpected"))
    def test_save_to_file_unexpected_error(self, mock_file):
        self.manager.generate(8)
        success, message = self.manager.save_to_file()
        self.assertFalse(success)
        self.assertEqual(message, "Неожиданная ошибка: Unexpected")


class TestInputFunctions(unittest.TestCase):
    """Тесты для функций ввода input_integer и input_yes_no."""

    @patch('builtins.input')
    def test_input_integer_default(self, mock_input):
        mock_input.return_value = ""
        result = pg.input_integer("prompt", default=5, min_val=1, max_val=10)
        self.assertEqual(result, 5)

    @patch('builtins.input')
    def test_input_integer_valid(self, mock_input):
        mock_input.return_value = "7"
        result = pg.input_integer("prompt", default=5, min_val=1, max_val=10)
        self.assertEqual(result, 7)

    @patch('builtins.input')
    def test_input_integer_invalid_then_valid(self, mock_input):
        mock_input.side_effect = ["abc", "15", "8"]
        result = pg.input_integer("prompt", default=5, min_val=1, max_val=10)
        self.assertEqual(result, 8)

    @patch('builtins.input')
    def test_input_integer_out_of_range(self, mock_input):
        mock_input.side_effect = ["0", "11", "5"]
        result = pg.input_integer("prompt", default=5, min_val=1, max_val=10)
        self.assertEqual(result, 5)

    @patch('builtins.input')
    def test_input_yes_no_yes(self, mock_input):
        mock_input.return_value = "y"
        result = pg.input_yes_no("prompt")
        self.assertTrue(result)

    @patch('builtins.input')
    def test_input_yes_no_no(self, mock_input):
        mock_input.return_value = "n"
        result = pg.input_yes_no("prompt")
        self.assertFalse(result)

    @patch('builtins.input')
    def test_input_yes_no_invalid_then_valid(self, mock_input):
        mock_input.side_effect = ["maybe", "yes"]
        result = pg.input_yes_no("prompt")
        self.assertTrue(result)


class TestMenuIntegration(unittest.TestCase):
    """Тесты для меню с использованием моков."""

    def setUp(self):
        self.manager = pg.PasswordManager()

    @patch('builtins.input')
    def test_menu_generate_only_lowercase(self, mock_input):
        # Последовательность: 1 (генерация), пустая строка (длина по умолчанию), n, n, n, 3 (выход)
        mock_input.side_effect = ["1", "", "n", "n", "n", "3"]
        with patch('builtins.print'):
            pg.menu(self.manager)
        self.assertEqual(self.manager.last_settings, "только строчные")
        self.assertEqual(len(self.manager.last_password), pg.DEFAULT_PASSWORD_LENGTH)

    @patch('builtins.input')
    def test_menu_generate_all_options(self, mock_input):
        mock_input.side_effect = ["1", "12", "y", "y", "y", "3"]
        with patch('builtins.print'):
            pg.menu(self.manager)
        self.assertEqual(self.manager.last_settings, "строчные + заглавные + цифры + спецсимволы")
        self.assertEqual(len(self.manager.last_password), 12)

    @patch('builtins.input')
    def test_menu_generate_uppercase_and_digits(self, mock_input):
        mock_input.side_effect = ["1", "8", "y", "n", "y", "3"]
        with patch('builtins.print'):
            pg.menu(self.manager)
        self.assertEqual(self.manager.last_settings, "строчные + заглавные + цифры")
        self.assertEqual(len(self.manager.last_password), 8)

    @patch('builtins.input')
    def test_menu_generate_digits_and_specials(self, mock_input):
        mock_input.side_effect = ["1", "10", "y", "y", "n", "3"]
        with patch('builtins.print'):
            pg.menu(self.manager)
        self.assertEqual(self.manager.last_settings, "строчные + цифры + спецсимволы")
        self.assertEqual(len(self.manager.last_password), 10)

    @patch('builtins.input')
    def test_menu_save_without_generation(self, mock_input):
        mock_input.side_effect = ["2", "3"]
        with patch('builtins.print') as mock_print:
            pg.menu(self.manager)
        mock_print.assert_any_call("❌ Сначала сгенерируйте пароль!")

    @patch('builtins.input')
    @patch("builtins.open", new_callable=mock_open)
    def test_menu_save_after_generation(self, mock_file, mock_input):
        # Генерация, затем сохранение, затем выход
        mock_input.side_effect = ["1", "8", "n", "n", "n", "2", "3"]
        with patch('builtins.print') as mock_print:
            pg.menu(self.manager)
        mock_file.assert_called_once_with("passwords.txt", "a")
        mock_print.assert_any_call("✅ Пароль сохранён в файл passwords.txt")

    @patch('builtins.input')
    def test_menu_invalid_choice(self, mock_input):
        mock_input.side_effect = ["99", "3"]
        with patch('builtins.print') as mock_print:
            pg.menu(self.manager)
        mock_print.assert_any_call("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    unittest.main()