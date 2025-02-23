import flet as ft
from pytubefix import YouTube, Playlist
import os
import threading
import ffmpeg
import time


def main(page: ft.Page):
    page.title = "YouTube Downloader"
    page.window_width = 600
    page.window_height = 580  # Увеличил высоту для нового элемента
    page.window_resizable = False
    page.padding = 20
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.colors.BLACK

    # Элементы интерфейса
    url_input = ft.TextField(
        label="URL видео или плейлиста",
        width=500,
        bgcolor=ft.colors.GREY_900,
        color=ft.colors.WHITE,
        border_color=ft.colors.GREY_700
    )
    output_path = ft.Text(
        value=os.path.join(os.getcwd(), "downloads"),
        width=500,
        color=ft.colors.WHITE
    )
    resolution_dropdown = ft.Dropdown(
        label="Качество",
        options=[
            ft.dropdown.Option("360p"),
            ft.dropdown.Option("480p"),
            ft.dropdown.Option("720p"),
            ft.dropdown.Option("1080p")
        ],
        value="480p",
        width=150,
        bgcolor=ft.colors.GREY_900,
        color=ft.colors.WHITE,
        border_color=ft.colors.GREY_700
    )
    size_label = ft.Text("Размер: Неизвестно", color=ft.colors.WHITE)
    total_size_label = ft.Text("Общий объём плейлиста: Неизвестно", color=ft.colors.WHITE, visible=False)
    speed_label = ft.Text("Скорость: 0.00 MB/s", color=ft.colors.WHITE)
    status_text = ft.Text("Введите URL и выберите параметры", color=ft.colors.WHITE)
    progress_bar = ft.ProgressBar(width=500, value=0, color=ft.colors.BLUE, bgcolor=ft.colors.GREY_800)
    total_progress_bar = ft.ProgressBar(width=500, value=0, color=ft.colors.GREEN, bgcolor=ft.colors.GREY_800,
                                        visible=False)
    download_button = ft.ElevatedButton(
        "Скачать",
        on_click=lambda e: start_download(),
        bgcolor=ft.colors.BLUE_700,
        color=ft.colors.WHITE
    )

    # Функция для выбора папки
    def choose_folder(e):
        folder_picker = ft.FilePicker(on_result=lambda e: update_output_path(e))
        page.overlay.append(folder_picker)
        page.update()
        folder_picker.get_directory_path(dialog_title="Выберите папку")

    def update_output_path(e):
        if e.path:
            output_path.value = e.path
            page.update()

    # Функция для оценки размера и общего объёма
    def update_size(e):
        url = url_input.value
        resolution = resolution_dropdown.value
        if not url:
            size_label.value = "Размер: Введите URL"
            total_size_label.value = "Общий объём плейлиста: Неизвестно"
            total_size_label.visible = False
            page.update()
            return

        try:
            if "playlist" in url.lower():
                pl = Playlist(url)
                if pl.videos:
                    total_size_mb = 0
                    for yt in pl.videos:
                        stream = yt.streams.filter(resolution=resolution, file_extension="mp4",
                                                   progressive=True).first() or \
                                 yt.streams.filter(resolution=resolution, file_extension="mp4").first()
                        total_size_mb += stream.filesize / (1024 * 1024) if stream else 0
                    size_label.value = f"Размер одного видео: ~{total_size_mb / len(pl.videos):.2f} MB (оценка)"
                    total_size_label.value = f"Общий объём плейлиста: ~{total_size_mb:.2f} MB"
                    total_size_label.visible = True
                    total_progress_bar.visible = True
            else:
                yt = YouTube(url)
                stream = yt.streams.filter(resolution=resolution, file_extension="mp4", progressive=True).first() or \
                         yt.streams.filter(resolution=resolution, file_extension="mp4").first()
                size_mb = stream.filesize / (1024 * 1024) if stream else 0
                size_label.value = f"Размер: ~{size_mb:.2f} MB"
                total_size_label.visible = False
                total_progress_bar.visible = False
        except Exception as e:
            size_label.value = f"Размер: Не удалось оценить ({e})"
            total_size_label.value = f"Общий объём: Не удалось оценить ({e})"
            total_size_label.visible = "playlist" in url.lower()
        page.update()

    url_input.on_change = update_size
    resolution_dropdown.on_change = update_size

    # Функция скачивания
    def download_content(url, output_path_value, resolution):
        try:
            if "playlist" in url.lower():
                playlist = Playlist(url)
                status_text.value = f"Скачивание плейлиста: {playlist.title}"
                page.update()

                total_videos = len(playlist.video_urls)
                for i, video_url in enumerate(playlist.video_urls, 1):
                    yt = YouTube(video_url)
                    download_single_video(yt, output_path_value, resolution, i, total_videos)
                    total_progress_bar.value = i / total_videos
                    page.update()
            else:
                yt = YouTube(url)
                download_single_video(yt, output_path_value, resolution, 1, 1)

            status_text.value = "Скачивание завершено!"
            speed_label.value = "Скорость: 0.00 MB/s"
            page.dialog = ft.AlertDialog(title=ft.Text("Успех"), content=ft.Text("Все файлы скачаны!"), open=True)

        except Exception as e:
            status_text.value = f"Ошибка: {e}"
            speed_label.value = "Скорость: 0.00 MB/s"
            page.dialog = ft.AlertDialog(title=ft.Text("Ошибка"), content=ft.Text(f"Не удалось скачать: {e}"),
                                         open=True)

        download_button.disabled = False
        page.update()

    def download_single_video(yt, output_path_value, resolution, current, total):
        status_text.value = f"Скачивание {current}/{total}: {yt.title or 'Unknown Title'}"
        page.update()

        video_stream = yt.streams.filter(
            resolution=resolution,
            file_extension="mp4",
            progressive=True
        ).first()

        if not video_stream and resolution in ["720p", "1080p"]:
            status_text.value = f"{resolution} прогрессивный недоступен, скачиваем с аудио отдельно..."
            page.update()
            video_stream = yt.streams.filter(
                resolution=resolution,
                file_extension="mp4"
            ).first()
            audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()

            if video_stream and audio_stream:
                if not os.path.exists(output_path_value):
                    os.makedirs(output_path_value)

                video_file = video_stream.download(output_path=output_path_value, filename="video_temp.mp4")
                audio_file = audio_stream.download(output_path=output_path_value, filename="audio_temp.mp4")

                output_file = os.path.join(output_path_value, f"{yt.title or 'video'}.mp4")
                try:
                    ffmpeg.input(video_file).output(output_file, audio=audio_file, codec="copy").run(
                        overwrite_output=True)
                except ffmpeg.Error as e:
                    raise Exception(f"Ошибка объединения потоков: {e}")

                os.remove(video_file)
                os.remove(audio_file)
            else:
                raise Exception(f"Не удалось найти подходящие потоки для {resolution}")
        else:
            if not video_stream:
                status_text.value = f"Качество {resolution} недоступно, ищу альтернативу..."
                page.update()
                video_stream = yt.streams.filter(file_extension="mp4", progressive=True).order_by(
                    "resolution").desc().first()

            if not video_stream:
                raise Exception(f"Нет доступных потоков для {yt.title}")

            if not os.path.exists(output_path_value):
                os.makedirs(output_path_value)

            last_time = time.time()
            last_bytes = 0

            def progress_callback(stream, chunk, bytes_remaining):
                nonlocal last_time, last_bytes
                total_size = stream.filesize
                bytes_downloaded = total_size - bytes_remaining
                percentage = (bytes_downloaded / total_size) * 100
                progress_bar.value = percentage / 100

                # Расчёт скорости
                current_time = time.time()
                time_diff = current_time - last_time
                if time_diff > 0.5:  # Обновляем каждые 0.5 секунды
                    bytes_diff = bytes_downloaded - last_bytes
                    speed_mb_s = (bytes_diff / (1024 * 1024)) / time_diff
                    speed_label.value = f"Скорость: {speed_mb_s:.2f} MB/s"
                    last_time = current_time
                    last_bytes = bytes_downloaded
                page.update()

            yt.register_on_progress_callback(progress_callback)
            video_stream.download(output_path_value)

    # Функция запуска скачивания
    def start_download():
        url = url_input.value
        output = output_path.value
        resolution = resolution_dropdown.value

        if not url:
            page.dialog = ft.AlertDialog(title=ft.Text("Внимание"), content=ft.Text("Введите URL!"), open=True)
            page.update()
            return
        if not output:
            page.dialog = ft.AlertDialog(title=ft.Text("Внимание"), content=ft.Text("Выберите папку!"), open=True)
            page.update()
            return

        status_text.value = "Начинаем скачивание..."
        progress_bar.value = 0
        total_progress_bar.value = 0
        speed_label.value = "Скорость: 0.00 MB/s"
        download_button.disabled = True
        page.update()
        threading.Thread(target=download_content, args=(url, output, resolution), daemon=True).start()

    # Сборка интерфейса
    page.add(
        ft.Column(
            [
                url_input,
                ft.Row([ft.Text("Папка:", color=ft.colors.WHITE),
                        ft.ElevatedButton("Выбрать", on_click=choose_folder, bgcolor=ft.colors.GREY_700,
                                          color=ft.colors.WHITE)], alignment=ft.MainAxisAlignment.CENTER),
                output_path,
                ft.Row([resolution_dropdown, size_label], alignment=ft.MainAxisAlignment.CENTER),
                total_size_label,
                ft.Text("Прогресс текущего видео:", color=ft.colors.WHITE),
                progress_bar,
                speed_label,
                ft.Text("Общий прогресс плейлиста:", color=ft.colors.WHITE, visible=False,
                        ref=total_progress_label_ref),
                total_progress_bar,
                status_text,
                download_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        )
    )


# Ссылка для видимости общего прогресса
total_progress_label_ref = ft.Ref[ft.Text]()

ft.app(target=main)