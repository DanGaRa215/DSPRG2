import sqlite3


# DBファイルを保存するファイルパス
# Google Colab
path = 'jma/'

# DBファイル名
db_name = 'dsprg2.db'
# db_name = 'dsprg2.sqlite'

# DBに接続する（DBファイルが存在しない場合は，新規に作成される）
con = sqlite3.connect(path + db_name)


# DBへの接続を閉じる
con.close()


# DBに接続
con = sqlite3.connect(path + db_name)

# SQL（RDBを操作するための言語）を実行するためのカーソルオブジェクトを取得
cur = con.cursor()

# 実行したいSQL
# 一旦
sql = """CREATE TABLE IF NOT EXISTS offices (
    id TEXT PRIMARY KEY,
    name TEXT,
    en_name TEXT,
    office_name TEXT,
    parent TEXT,
    children TEXT,
    weatherCodes TEXT,
    timeSeries TEXT,
    code TEXT

)"""

# SQLを実行
cur.execute(sql)

# DBへの接続を閉じる
con.close()