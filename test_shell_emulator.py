import unittest
import os
from shell_emulator import VirtualFileSystem, ShellEmulator


class TestShellEmulator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Подготовка виртуальной файловой системы для тестов
        cls.vfs = VirtualFileSystem("test_fs.zip")  # Путь к тестовому zip-файлу
        cls.shell = ShellEmulator(cls.vfs)

    def test_ls_root(self):
        # Тестируем команду ls в корневой директории
        self.vfs.current_dir = ""
        expected_files = ["documents/", "photos/", "file1.txt"]
        output = self.vfs.list_dir()
        for item in expected_files:
            self.assertIn(item, output, f"{item} должно быть в корне")

    def test_cd_and_ls(self):
        # Тестируем команду cd и ls в поддиректории
        self.shell.run_command("cd documents")
        output = self.vfs.list_dir()
        expected_files = ["doc1.txt", "doc2.txt"]
        for item in expected_files:
            self.assertIn(item, output, f"{item} должно быть в папке documents")

    def test_cd_back(self):
        # Тестируем команду cd для перехода на уровень выше
        self.shell.run_command("cd documents")
        self.shell.run_command("cd ..")
        self.assertEqual(self.vfs.current_dir, "", "Мы должны быть в корневой директории после cd ..")

    def test_exit(self):
        # Тестируем команду exit
        result = self.shell.run_command("exit")
        self.assertFalse(result, "Команда exit должна завершить эмулятор")

    def test_uniq(self):
        # Тестируем команду uniq
        self.shell.vfs.zip_file.extract("documents/duplicates.txt")  # Предположим, что в test_fs.zip есть этот файл
        self.shell.run_command("uniq documents/duplicates.txt")

    def test_tree(self):
        # Тестируем команду tree
        output = self.shell.run_command("tree")
        self.assertIn("documents/", output)
        self.assertIn("photos/", output)

    def test_du(self):
        # Тестируем команду du
        output = self.shell.run_command("du")
        self.assertIn("file1.txt", output)


if __name__ == "__main__":
    unittest.main()
