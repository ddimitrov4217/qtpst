# Екран с pyQt за разглеждане на Outlook pst и msg

## Възможности

За pst архив, екрана позволява:
1. Избор на Outlook pst файл;
2. Извеждане на йерархията на папките като дърво;
3. Извеждане на съобщенията --- тема, дата и час, подател, цветни категории;
4. Извеждане на съобщение --- като текст, като html със inline картинките, всички pst атрибути, приложени файлове;
За отделен msg файл с едно съобщение се извежда същото като посоченото в точка (4).

## Зависимости

Форматите за Outlook се обработват с модула
[ddimitrov4217/readms](https://github.com/ddimitrov4217/readms) който трябва да е свален в отделна папка така че да е достъпен локално.
Настройката на зависимостта може да се види във [pyproject.toml](pyproject.toml).

## Извикване от командна линия

```
Usage: pyqtpst [OPTIONS] COMMAND [ARGS]...

  Четене на изпозлваните от MS Outlook файлове

Options:
  --config PATH  конфигурационен файл
  --help         Show this message and exit.

Commands:
  message    Избор и разглеждане на msg файл
  navigator  Избор и разглеждане на pst файлове
```
където конфигурационния файл е нещо като примерния  [appconfig.ini](appconfig.ini).

Командата за четене на pst архив:
```
Usage: pyqtpst navigator [OPTIONS]

  Избор и разглеждане на pst файлове

Options:
  --file PATH  pst файл за разглеждане
  --help       Show this message and exit.
```

Командата за четене на msg съобщение:
```
Usage: pyqtpst message [OPTIONS] FILE

  Избор и разглеждане на msg файл

Options:
  --nid INTEGER  nid от pst файл
  --help         Show this message and exit.
```
