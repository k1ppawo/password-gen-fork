import unittest
from unittest.mock import patch, mock_open
import string
import random
import time


import test_code as pwg


class TestGeneratePassword(unittest.TestCase):
    """Тесты для функции generate_password."""

    def test_only_lowercase(self):
        """Генерация только из строчных букв."""
        length = 10
        pwd = pwg.generate_password(length)
        self.assertEqual(len(pwd), length)
        self.assertTrue(all(c in pwg.LOWERCASE for c in pwd))

    def test_with_uppercase(self):
        """Добавление заглавных букв."""
        length = 15
        pwd = pwg.generate_password(length, use_uppercase=True)
        self.assertEqual(len(pwd), length)
        allowed = pwg.LOWERCASE + pwg.UPPERCASE
        self.assertTrue(all(c in allowed for c in pwd))

    def test_with_digits(self):
        """Добавление цифр."""
        length = 12
        pwd = pwg.generate_password(length, use_digits=True)
        self.assertEqual(len(pwd), length)
        allowed = pwg.LOWERCASE + pwg.DIGITS
        self.assertTrue(all(c in allowed for c in pwd))

    def test_with_specials(self):
        """Добавление спецсимволов."""
        length = 8
        pwd = pwg.generate_password(length, use_specials=True)
        self.assertEqual(len(pwd), length)
        allowed = pwg.LOWERCASE + pwg.SPECIALS
        self.assertTrue(all(c in allowed for c in pwd))

    def test_all_options(self):
        """Все типы символов."""
        length = 20
        pwd = pwg.generate_password(length, use_uppercase=True, use_digits=True, use_specials=True)
        self.assertEqual(len(pwd), length)
        allowed = pwg.LOWERCASE + pwg.UPPERCASE + pwg.DIGITS + pwg.SPECIALS
        self.assertTrue(all(c in allowed for c in pwd))

    def test_different_lengths(self):
        """Проверка для разных длин."""
        for length in [1, 5, 10, 50]:
            pwd = pwg.generate_password(length)
            self.assertEqual(len(pwd), length)

    def test_randomness(self):
        """Проверка, что при фиксированном seed результат предсказуем."""
        random.seed(42)
        pwd1 = pwg.generate_password(10, use_uppercase=True, use_digits=True)
        random.seed(42)
        pwd2 = pwg.generate_password(10, use_uppercase=True, use_digits=True)
        self.assertEqual(pwd1, pwd2)


class TestMenuGlobalState(unittest.TestCase):
    """Тесты для глобальных переменных last_password и last_settings через меню."""

    def setUp(self):
        pwg.last_password = ""
        pwg.last_settings = ""

    @patch('builtins.input')
    def test_generate_only_lowercase(self, mock_input):
        """Генерация только строчных (все ответы 'n')."""
        mock_input.side_effect = ["1", "", "n", "n", "n", "3"]
        with patch('builtins.print'):
            pwg.menu()
        self.assertNotEqual(pwg.last_password, "")
        self.assertEqual(pwg.last_settings, "только строчные")

    @patch('builtins.input')
    def test_generate_all_options(self, mock_input):
        """Генерация со всеми опциями."""
        mock_input.side_effect = ["1", "12", "y", "y", "y", "3"]
        with patch('builtins.print'):
            pwg.menu()
        self.assertEqual(len(pwg.last_password), 12)
        self.assertEqual(pwg.last_settings, "строчные + заглавные + цифры + спецсимволы")

    @patch('builtins.input')
    def test_generate_uppercase_and_digits(self, mock_input):
        """Генерация с заглавными и цифрами."""
        # Порядок: use_digits, use_specials, use_uppercase
        mock_input.side_effect = ["1", "8", "y", "n", "y", "3"]
        with patch('builtins.print'):
            pwg.menu()
        self.assertEqual(pwg.last_settings, "строчные + заглавные + цифры")

    @patch('builtins.input')
    def test_last_password_updated(self, mock_input):
        """Проверка, что last_password обновляется при генерации."""
        mock_input.side_effect = ["1", "5", "n", "n", "n", "3"]
        with patch('builtins.print'):
            pwg.menu()
        self.assertNotEqual(pwg.last_password, "")


class TestFileSaving(unittest.TestCase):
    """Тесты для сохранения в файл."""

    def setUp(self):
        # По умолчанию ставим непустой пароль, чтобы явно не мешал
        # Но в тестах, где нужен пустой, будем сбрасывать отдельно
        pwg.last_password = "testpass"
        pwg.last_settings = "тестовый пароль"

    @patch('builtins.input')
    @patch("builtins.open", new_callable=mock_open)
    def test_save_success(self, mock_file, mock_input):
        """Успешное сохранение после генерации."""
        pwg.last_password = ""  # начинаем с пустого, чтобы генерация точно произошла
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
    def test_save_io_error(self, mock_file, mock_input):
        """Ошибка ввода-вывода при сохранении."""
        pwg.last_password = ""  # сброс, чтобы генерация произошла
        mock_input.side_effect = ["1", "5", "n", "n", "n", "2", "3"]
        with patch('builtins.print') as mock_print:
            pwg.menu()
        mock_print.assert_any_call("Ошибка при сохранении в файл")

    @patch('builtins.input')
    def test_save_without_generation(self, mock_input):
        """Попытка сохранить без предварительной генерации."""
        pwg.last_password = ""  # явно обнуляем, чтобы условие сработало
        mock_input.side_effect = ["2", "3"]
        with patch('builtins.print') as mock_print:
            pwg.menu()
        mock_print.assert_any_call("Сначала сгенерируйте пароль!")


class TestInputHandling(unittest.TestCase):
    """Тесты для обработки некорректного ввода."""

    @patch('builtins.input')
    def test_invalid_menu_choice(self, mock_input):
        """Неверный пункт меню."""
        mock_input.side_effect = ["99", "3"]
        with patch('builtins.print') as mock_print:
            pwg.menu()
        mock_print.assert_any_call("Неверный выбор. Попробуйте снова.")

    @patch('builtins.input')
    def test_non_numeric_length(self, mock_input):
        """Ввод нечисловой длины (должен вызвать ValueError)."""
        mock_input.side_effect = ["1", "abc", "3"]
        with self.assertRaises(ValueError):
            pwg.menu()


if __name__ == "__main__":
    unittest.main()