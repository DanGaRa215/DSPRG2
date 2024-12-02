import flet as ft
import json

# 地域リストを読み込む関数
def load_all_regions():
    try:
        with open("jma/weather_info.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("地域リストファイルが見つかりません。")
        return {}
    except json.JSONDecodeError as e:
        print(f"JSONデータの読み込み中にエラーが発生しました: {e}")
        return {}

# Fletアプリケーション
def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.scroll = ft.ScrollMode.AUTO

    # 地域リストを読み込む
    all_regions = load_all_regions()
    if not all_regions:
        page.add(ft.Text("地域リストが読み込めませんでした。"))
        return

    # class10 と class15 のデータを取得
    class10s = all_regions.get("class10s", {})
    class15s = all_regions.get("class15s", {})

    # ナビゲーションバーに表示する class10 のリスト
    navigation_items = [
        ft.NavigationRailDestination(
            icon=ft.icons.PUBLIC,
            selected_icon=ft.icons.PUBLIC_OFF,
            label=details.get("name", "不明な地域"),
        )
        for code, details in class10s.items()
    ]

    # 選択された class15 を表示するエリア
    class15_display = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO)

    # 天気情報を表示するエリア
    weather_display = ft.Text("天気情報はここに表示されます。")

    # 選択された地域の情報を表示するための関数
    def on_destination_change(e):
        selected_index = e.control.selected_index
        selected_code = list(class10s.keys())[selected_index]
        selected_name = class10s[selected_code]["name"]

        # 選択された class10 に関連する class15 を取得
        related_class15 = [
            f"{details['name']} (コード: {code})"
            for code, details in class15s.items()
            if details["parent"] == selected_code
        ]

        # class15 の情報を更新（下に表示）
        if related_class15:
            class15_display.controls = [ft.Text(f"- {item}") for item in related_class15]
        else:
            class15_display.controls = [ft.Text("関連する地域 (class15) はありません。")]

        # 天気情報エリアの初期状態をリセット（天気情報はここで更新予定）
        weather_display.value = f"{selected_name} の天気情報を表示する予定です。"

        # ページを更新
        page.update()

    # 左側の NavigationRail を固定サイズの Container でラップ
    navigation_rail = ft.NavigationRail(
        destinations=navigation_items,
        selected_index=0,
        on_change=on_destination_change,
    )

    # ページのレイアウト
    page.add(
        ft.Row(
            controls=[
                ft.Container(
                    content=navigation_rail,
                    width=250,
                    height=page.height,  # 高さを固定
                    bgcolor=ft.colors.BLUE_GREY_50,
                ),
                ft.Column(
                    controls=[
                        ft.Text("選択された地域:"),
                        ft.Container(content=class15_display, expand=True),  # class15 を表示するエリア
                    ],
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,  # スクロールを有効にする
                    width=300,
                ),
                ft.Container(
                    content=weather_display,  # 天気情報を表示するエリア
                    expand=True,
                    bgcolor=ft.colors.LIGHT_BLUE_50,
                ),
            ],
            expand=True,  # Row の高さを親に合わせる
        )
    )

# Fletアプリケーションを実行
ft.app(target=main)