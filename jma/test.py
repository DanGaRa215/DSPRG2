import flet as ft
import requests
import json

# ローカルJSONデータのファイルパス
DATA_FILE = "jma/weather_info.json"

def main(page: ft.Page):
    page.title = "地域と県名の表示"
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = ft.colors.WHITE  # 背景色を白に設定

    # JSONデータをファイルから読み込む
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
    # ExpansionTileリストを作成
    center_tiles = []

    for center_key, center_info in centers.items():
        # そのセンターに関連するオフィスを取得
        related_offices = [
            offices[office_key]
            for office_key in center_info.get("children", [])
            if office_key in offices
        ]

        # 関連するオフィス情報をサブリストとして表示
        office_tiles = [
            ft.ListTile(title=ft.Text(f"{office['name']} ({office['enName']})"),bgcolor=ft.colors.WHITE38)
            for office in related_offices
        ]

        # ExpansionTileにセンターとオフィス情報を追加
        center_tiles.append(
            ft.ExpansionTile(
                title=ft.Text(center_info["name"], color=ft.colors.BLACK),
                controls=office_tiles,
                initially_expanded=False,
                text_color=ft.colors.BLACK,
                collapsed_text_color=ft.colors.GREY,
            )
        )

    # 左側の地域リストを表示
    region_list = ft.Container(
        content=ft.Column(
            controls=center_tiles,
            scroll=ft.ScrollMode.AUTO,
        ),
        width=200,  # 左側の幅を設定
        bgcolor=ft.colors.BLUE_GREY_50,
        padding=10,
    )

    # 右側の空白部分（後で追加する内容のスペース）
    right_placeholder = ft.Container(
        content=ft.Text("ここに詳細情報が表示されます。", color=ft.colors.GREY),
        expand=True,
        bgcolor=ft.colors.LIGHT_BLUE_50,
        padding=10,
    )

    # ページ全体のレイアウトを構築
    page.add(
        ft.Row(
            controls=[
                region_list,
                right_placeholder,
            ],
            expand=True,
        )
    )

# 実行
ft.app(target=main)