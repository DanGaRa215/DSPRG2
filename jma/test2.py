import flet as ft
import json
import requests
from datetime import datetime

# ローカルJSONデータのファイルパス
DATA_FILE = "jma/weather_info.json"
WEATHER_API_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/{office_code}.json"

# 日付フォーマット関数
def format_date(date_str: str) -> str:
    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    return date.strftime("%Y年%m月%d日")

# 天気アイコンを取得する関数
def get_weather_icon(weather_code: str) -> str:
    weather_icons = {
        "100": "☀️",  # 晴れ
        "101": "🌤️",  # 晴れ時々曇り
        "102": "🌦️",  # 晴れ時々雨
        "200": "☁️",  # 曇り
        "300": "🌧️",  # 雨
        "317": "🌧️❄️☁️",  # 雨か雪のち曇り
        "400": "❄️",  # 雪
        "402": "❄️☁️",  # 雪時々曇り
        "500": "⛈️",  # 雷雨
        "413": "❄️→🌧️",  # 雪のち雨
        "314": "🌧️→❄️",  # 雨のち雪
        "201": "🌤️",
        "202": "☁️🌧️",
        "218": "☁️❄️",
        "270": "❄️☁️",
        "206": "🌧️☁️",
        "111": "🌧️☀️",
        "112": "🌧️❄️",
        "211": "❄️☀️",
        "212": "❄️☁️",
        "313": "❄️🌧️",
        "203": "☁️❄️",
        "302": "❄️",
        "114": "❄️☀️",
        "214":"☁️🌧️",
        "204":"☁️❄️⚡️",
        "207":"☁️🌧️❄️",
        "110":"☀️☁️",
    }
    # 該当する天気コードがない場合は ❓ を表示
    return weather_icons.get(weather_code, "❓")

def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = ft.colors.WHITE

    # JSONデータを読み込む
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        page.add(ft.Text("JSONファイルが見つかりません。", color=ft.colors.RED))
        return
    except json.JSONDecodeError as e:
        page.add(ft.Text(f"JSONデータの読み込みに失敗しました: {e}", color=ft.colors.RED))
        return

    centers = data.get("centers", {})
    offices = data.get("offices", {})

    # 天気情報を表示する領域
    weather_display = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    # 天気情報を取得して表示する関数
    def display_weather(office_code: str):
        weather_display.controls.clear()
        try:
            # 天気情報を取得
            response = requests.get(WEATHER_API_URL.format(office_code=office_code))
            response.raise_for_status()
            weather_data = response.json()

            # 天気情報を表示
            for day in weather_data[0]["timeSeries"][0]["timeDefines"]:
                date = format_date(day)
                weather_code = weather_data[0]["timeSeries"][0]["areas"][0]["weatherCodes"][0]
                weather_display.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(date, size=16, weight="bold"),
                                    ft.Text(get_weather_icon(weather_code)),
                                    ft.Text(f"天気コード: {weather_code}"),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            padding=10,
                        )
                    )
                )
        except Exception as e:
            weather_display.controls.append(ft.Text(f"天気情報の取得に失敗しました: {e}", color=ft.colors.RED))

        page.update()

    # 左側のリスト
    center_tiles = []
    for center_key, center_info in centers.items():
        # そのセンターに関連するオフィスを取得
        related_offices = [
            offices[office_key]
            for office_key in center_info.get("children", [])
            if office_key in offices
        ]

        # オフィスリスト
        # オフィスリスト
        office_tiles = [
            ft.ListTile(
                title=ft.Text(f"{offices[office_key]['name']} ({offices[office_key]['enName']})"),
                on_click=lambda e, office_code=office_key: display_weather(office_code),
            )
            for office_key in center_info.get("children", [])
            if office_key in offices
        ]


        # ExpansionTile
        center_tiles.append(
            ft.ExpansionTile(
                title=ft.Text(center_info["name"], color=ft.colors.BLACK),
                controls=office_tiles,
                initially_expanded=False,
                text_color=ft.colors.BLACK,
                collapsed_text_color=ft.colors.GREY,
            )
        )

    # 左側のリスト
    region_list = ft.Container(
        content=ft.Column(
            controls=center_tiles,
            scroll=ft.ScrollMode.AUTO,
        ),
        width=250,
        bgcolor=ft.colors.LIGHT_BLUE_50,
        padding=10,
    )

    # レイアウト
    page.add(
        ft.Row(
            controls=[
                region_list,
                ft.Container(content=weather_display, expand=True, padding=10),
            ],
            expand=True,
        )
    )

# 実行
ft.app(target=main)