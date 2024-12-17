import sqlite3
import json
import requests
from datetime import datetime
import flet as ft

# ローカルJSONデータのファイルパス
DATA_FILE = "test.py"
WEATHER_API_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/{office_code}.json"
DB_FILE = "weather.db"

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
        "400": "❄️",  # 雪
    }
    return weather_icons.get(weather_code, "❓")

def get_weather_text(code: str) -> str:
    weather_codes = {
        "100": "晴れ",
        "101": "晴れ時々曇り",
        "102": "晴れ時々雨",
        "200": "曇り",
        "300": "雨",
        "400": "雪",
    }
    return weather_codes.get(code, f"不明な天気 (コード: {code})")


def save_weather_data_to_db(office_code: str, weather_data: list):
    """天気データをSQLiteのweather_dataテーブルに保存する"""
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        
        # weather_data テーブルを作成
        sql ="""
CREATE TABLE IF NOT EXISTS offices (
    id TEXT PRIMARY KEY,
    name TEXT,
    en_name TEXT,
    office_name TEXT,
    parent TEXT,
    children TEXT
)"""
        cur.execute(sql)

        # データを挿入するためのリストを作成
        data_to_insert = []
        for i, day in enumerate(weather_data[0]["timeSeries"][0]["timeDefines"]):
            date = format_date(day)
            weather_code = weather_data[0]["timeSeries"][0]["areas"][0]["weatherCodes"][i]
            weather_icon = get_weather_icon(weather_code)
            weather_text = get_weather_text(weather_code)

            data_to_insert.append((office_code, date, weather_code, weather_icon, weather_text))

        # データを一括挿入
        cur.executemany("""
        INSERT INTO weather_data (office_code, date, weather_code, weather_icon, weather_text) 
        VALUES (?, ?, ?, ?, ?)
        """, data_to_insert)

        print(f"{len(data_to_insert)} 件の天気データがDBに格納されました。")

def display_weather_ui(weather_display, weather_data):
    """UI表示用の関数"""
    for i, day in enumerate(weather_data[0]["timeSeries"][0]["timeDefines"]):
        date = format_date(day)
        weather_code = weather_data[0]["timeSeries"][0]["areas"][0]["weatherCodes"][i]
        weather_display.controls.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(date, size=16, weight="bold"),
                            ft.Text(get_weather_icon(weather_code), size=60),
                            ft.Text(get_weather_text(weather_code), size=16),
                            ft.Text(f"天気コード: {weather_code}"),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=10,
                )
            )
        )


def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = ft.colors.WHITE

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        page.add(ft.Text(f"JSONの読み込みエラー: {e}", color=ft.colors.RED))
        return

    centers = data.get("centers", {})
    offices = data.get("offices", {})

    weather_display = ft.Row(wrap=True, expand=True, spacing=20)

    def display_weather(office_code: str):
        weather_display.controls.clear()
        try:
            response = requests.get(WEATHER_API_URL.format(office_code=office_code))
            response.raise_for_status()
            weather_data = response.json()

            save_weather_data_to_db(office_code, weather_data)
            display_weather_ui(weather_display, weather_data)

        except Exception as e:
            weather_display.controls.append(ft.Text(f"天気情報の取得に失敗しました: {e}", color=ft.colors.RED))
        
        page.update()

    center_tiles = []
    for center_key, center_info in centers.items():
        office_tiles = [
            ft.ListTile(
                title=ft.Text(f"{offices[office_key]['name']} ({offices[office_key]['enName']})"),
                on_click=lambda e, office_code=office_key: display_weather(office_code),
            )
            for office_key in center_info.get("children", [])
            if office_key in offices
        ]

        center_tiles.append(
            ft.ExpansionTile(
                title=ft.Text(center_info["name"]),
                controls=office_tiles,
                initially_expanded=False,
                text_color=ft.colors.BLACK,
                collapsed_text_color=ft.colors.GREY,
            )
        )

    region_list = ft.Container(
        content=ft.Column(
            controls=center_tiles,
            scroll=ft.ScrollMode.AUTO,
        ),
        width=250,
        bgcolor=ft.colors.LIGHT_BLUE_50,
        padding=10,
    )

    page.add(
        ft.Row(
            controls=[
                region_list,
                ft.Container(content=weather_display, padding=5),
            ],
            expand=True,
        )
    )

ft.app(target=main)