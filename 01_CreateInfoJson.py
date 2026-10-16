import json
from pathlib import Path
from lib.DLsite_scraping import DLsiteDownloader
import os 

#jsonファイルの読み込み
f = open(f"{os.getcwd()}\\json\\paths.json", 'r')
dict_json = json.load(f)
f.close()

def split_string(text: str, separator: str) -> list[str]:
    """指定した区切り文字で文字列を分割する。"""
    return text.split(separator)


def get_folder_names(target_dir_path: str) -> list[str]:
    """指定フォルダ直下にあるサブフォルダ名を取得する。"""
    target_dir = Path(target_dir_path)
    if not target_dir.exists() or not target_dir.is_dir():
        raise ValueError(f"指定されたパスが存在しないか、フォルダではありません: {target_dir_path}")

    return sorted(
        (entry.name for entry in target_dir.iterdir() if entry.is_dir()),
        key=str.casefold,
    )


def write_folder_names_json(
    folder_names: list[str],
    output_json_path: str = "folder_names.json",
) -> None:
    """フォルダ名のリストをJSONファイルに保存する。"""
    output_path = Path(output_json_path)
    output_path.write_text(
        json.dumps(folder_names, ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8",
    )
    print(f"サブフォルダ名 {len(folder_names)} 件を保存しました: {output_path.resolve()}")


def create_folder_names_json(target_dir_path: str, output_json_path: str = "folder_names.json") -> list[str]:
    """指定フォルダ直下のサブフォルダ名を取得してJSONファイルに保存する。"""
    folder_names = get_folder_names(target_dir_path)
    write_folder_names_json(folder_names, output_json_path)
    return folder_names


def crearte_metainfo_json(target_dir_path: str):
    """指定フォルダ直下のサブフォルダ名を取得して設定用jsonファイルの作成とジャケット画像を保存する。"""
    folder_names = get_folder_names(target_dir_path)
    for fn in folder_names:
        if "_" not in fn:
            if fn.startswith("RJ"):
                rj_id = fn  # RJ番号を取得
            else:
                print(f"フォルダ名にRJ番号が含まれていません: {fn}")
                continue
        else:
            split_names = split_string(fn, "_")
            rj_id = split_names[0]  # RJ番号を取得

        try:
            downloader = DLsiteDownloader(rj_id, f"{target_dir_path}\\{fn}")
            downloader.run()
        except Exception as e:
            print(f"RJ番号 {rj_id} の処理中にエラーが発生しました: {e}")
            continue

if __name__ == "__main__":
    # target_path = input("一覧を作成するフォルダのパスを入力してください: ").strip()
    # create_folder_names_json(target_path)

    #作業フォルダを取得
    #target_path = "D:\\work\\voice\\04_rename"
    target_path = dict_json['rename']['path']
    crearte_metainfo_json(target_path)

    """
    target_path = input("一覧を作成するフォルダのパスを入力してください: ").strip()
    create_folder_names_json(target_path)

    rj_id = input("取得するRJ番号を入力してください: ").strip()
    downloader = DLsiteDownloader(rj_id, target_path)
    downloader.run()
    """