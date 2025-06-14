# Программа для скачивания видео с YouTube

## Описание

Программа на Python предназначена для скачивания видео с YouTube по предоставленной ссылке. Она использует библиотеку `pytubefix` для удобной загрузки видео и аудио с платформы YouTube. Пользователь вводит URL видео, а программа сохраняет его в указанную папку в выбранном формате (например, MP4). Для интерфейса используется библиотека `flet`, а для обработки медиа — `ffmpeg`.

## Основные функции

- **Скачивание видео**: Поддержка загрузки видео в различных разрешениях (например, 720p, 1080p, в зависимости от доступных форматов).
- **Выбор формата**: Возможность выбора между видео с аудио или только аудио (MP3).
- **Интерфейс**: Графический интерфейс на основе `flet` для ввода URL и управления загрузкой.
- **Обработка ошибок**: Обрабатывает некорректные ссылки и недоступные видео.
- **Многопоточность**: Использует `threading` для выполнения загрузки в фоновом режиме.

## Требования

- Python 3.6+
- Установленные библиотеки:
  - `flet` (`pip install flet`)
  - `pytubefix` (`pip install pytubefix`)
  - `ffmpeg-python` (`pip install ffmpeg-python`)
- Установленный `ffmpeg` на компьютере (для обработки медиафайлов).

## Пример использования

1. Запустите программу.
2. Введите URL видео с YouTube (например, `https://www.youtube.com/watch?v=video_id`) в графическом интерфейсе.
3. Выберите разрешение или формат (если реализовано).
4. Нажмите кнопку для начала загрузки.
5. Видео будет сохранено в указанную директорию (по умолчанию — текущая папка).

## Ограничения

- Требуется стабильное интернет-соединение.
- Некоторые видео могут быть недоступны для скачивания из-за ограничений YouTube.
- Программа не поддерживает скачивание плейлистов (требуется доработка).
- Необходима установка `ffmpeg` для корректной работы с медиа.

## Установка

1. Установите Python с официального сайта: [python.org](https://www.python.org/).
2. Установите необходимые библиотеки:
   ```bash
   pip install flet pytubefix ffmpeg-python
   ```
3. Установите `ffmpeg`:
   - На Windows: Скачайте с [официального сайта](https://ffmpeg.org/download.html) и добавьте в PATH.
   - На macOS: `brew install ffmpeg`.
   - На Linux: `sudo apt-get install ffmpeg` (для Ubuntu/Debian).
4. Скопируйте и запустите код программы.

## Примечания

- Убедитесь, что вы соблюдаете авторские права и условия использования YouTube при скачивании видео.
- Для улучшения функциональности можно добавить:
  - Поддержку скачивания плейлистов через `Playlist` из `pytubefix`.
  - Выбор директории сохранения через интерфейс `flet`.
  - Индикатор прогресса загрузки.
- Код использует `threading` для асинхронной загрузки и `time` для управления таймингами.
