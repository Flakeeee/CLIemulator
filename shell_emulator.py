import os
import zipfile
import argparse

class VirtualFileSystem:
    def __init__(self, zip_path):
        self.zip_path = zip_path
        self.zip_file = zipfile.ZipFile(zip_path)
        self.current_dir = ""  # Начнем с корневого каталога

    def list_dir(self):
        # Список файлов и папок в текущем каталоге
        contents = [f for f in self.zip_file.namelist() if f.startswith(self.current_dir) and f != self.current_dir]
        for item in contents:
            print(item)

    def change_dir(self, path):
        # Переход в новую директорию
        if path == "..":
            self.current_dir = os.path.dirname(self.current_dir)
        else:
            potential_dir = os.path.join(self.current_dir, path)
            if any(f.startswith(potential_dir) for f in self.zip_file.namelist()):
                self.current_dir = potential_dir
            else:
                print(f"Папка '{path}' не найдена.")

    def get_file_content(self, file_path):
        try:
            with self.zip_file.open(file_path) as file:
                return file.read().decode('utf-8').splitlines()
        except KeyError:
            print(f"Файл '{file_path}' не найден в архиве.")
            return None

class ShellEmulator:
    def __init__(self, vfs):
        self.vfs = vfs

    def run_command(self, command):
        if command == "ls":
            self.vfs.list_dir()
        elif command.startswith("cd "):
            path = command.split(" ", 1)[1]
            self.vfs.change_dir(path)
        elif command == "exit":
            print("Выход из эмулятора.")
            return False
        elif command.startswith("uniq "):
            self.uniq_command(command.split(" ", 1)[1])
        elif command == "tree":
            self.tree_command()
        elif command == "du":
            self.du_command()
        else:
            print("Неизвестная команда")
        return True

    def uniq_command(self, file_path):
        # Команда uniq для вывода уникальных строк файла
        full_path = os.path.join(self.vfs.current_dir, file_path)
        content = self.vfs.get_file_content(full_path)
        if content:
            unique_lines = sorted(set(content))
            for line in unique_lines:
                print(line)

    def tree_command(self):
        # Команда tree для отображения структуры файлов и папок
        def display_tree(path, level=0):
            items = [f for f in self.vfs.zip_file.namelist() if f.startswith(path) and f != path]
            for item in items:
                item_name = os.path.basename(item.rstrip('/'))
                print(" " * (level * 2) + "|-- " + item_name)
                if item.endswith('/'):
                    display_tree(item, level + 1)

        display_tree(self.vfs.current_dir or "")

    def du_command(self):
        # Команда du для отображения размера файлов и папок
        contents = [f for f in self.vfs.zip_file.namelist() if f.startswith(self.vfs.current_dir) and f != self.vfs.current_dir]
        for item in contents:
            if not item.endswith('/'):
                info = self.vfs.zip_file.getinfo(item)
                print(f"{item} - {info.file_size} bytes")

def run_startup_script(emulator, script_path):
    with open(script_path, "r") as script_file:
        for line in script_file:
            line = line.strip()
            if line:
                print(f"Выполнение команды: {line}")
                if not emulator.run_command(line):
                    break

if __name__ == "__main__":
    # Настраиваем аргументы командной строки
    parser = argparse.ArgumentParser(description="Эмулятор shell для виртуальной файловой системы")
    parser.add_argument("zip_path", help="Путь к архиву виртуальной файловой системы")
    parser.add_argument("script_path", help="Путь к стартовому скрипту")
    args = parser.parse_args()

    # Инициализируем виртуальную файловую систему и эмулятор
    vfs = VirtualFileSystem(args.zip_path)
    emulator = ShellEmulator(vfs)

    # Запускаем команды из стартового скрипта
    run_startup_script(emulator, args.script_path)

    # Запускаем CLI для пользовательских команд
    while True:
        command = input("Эмулятор> ")
        if not emulator.run_command(command):
            break
