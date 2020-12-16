# FlaskProject
University flask project

Розгортання проекту на віндовс.

Для установки потрібних програм можна використовувати Chocolatey.

Установка Chocolatey:
@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"

Установка pyenv:
choco install pyenv-win

Установка пайтон:
pyenv install 3.6.8

Клонувати проект на пк.
У папці з проектом:
pyenv local 3.6.8

Інсталювати poetry (наприклад за допомогою pip).
choco install pip
pip install poetry

Виконати у папці з проектом:
where python
Копіювати шлях до пайтона потрібної версії(C:\Users\Roman\.pyenv\pyenv-win\shims\python.bat).

Створити віртуальне середовище:
poetry env use C:\Users\Roman\.pyenv\pyenv-win\shims\python.bat

Встановити залежності:
poetry install