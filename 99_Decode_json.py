import json

# ファイルを開いてJSONを読み込む
with open("metainfo.json", "r", encoding="utf-8-sig") as file:
    data = json.load(file)

# デコードされた内容を表示
""" print("アルバムタイトル:", data.get("albumtitle", "（未設定）"))
print("アルバムアーティスト:", data.get("albumartist", "（未設定）"))
print("アーティスト:", data.get("artist", "（未設定）")) """

# テキストファイルに出力
with open("output.txt", "w", encoding="utf-8") as out_file:
    out_file.write("アルバムタイトル: " + data.get("albumtitle", "（未設定）") + "\n")
    out_file.write("アルバムアーティスト: " + data.get("albumartist", "（未設定）") + "\n")
    out_file.write("アーティスト: " + data.get("artist", "（未設定）") + "\n")

print("output.txt に保存しました。")