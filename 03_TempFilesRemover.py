import json
import shutil
from pathlib import Path


TEMP_FOLDER_NAME = "00_tempfiles"
EXTRA_FOLDERS = {"繁體中文", "简体中文"}


def move_without_overwrite(source: Path, destination: Path) -> None:
    """同名の移動先がないことを確認して、ファイルまたはフォルダを移動する。"""
    if destination.exists():
        raise FileExistsError(f"移動先に同名の項目があります: {destination}")
    shutil.move(str(source), str(destination))


def move_japanese_contents(japanese_path: Path, folder_path: Path) -> None:
    """「日本語」フォルダ内の項目を親フォルダへ移動する。"""
    contents = list(japanese_path.iterdir())
    conflicts = [item.name for item in contents if (folder_path / item.name).exists()]
    if conflicts:
        raise FileExistsError(
            f"日本語フォルダ内の項目と同名の項目が移動先にあります: {', '.join(conflicts)}"
        )

    for item in contents:
        move_without_overwrite(item, folder_path / item.name)
        print(f"移動: 日本語\\{item.name} -> {folder_path.name}")


def should_move_file(path: Path) -> bool:
    """00_tempfilesへ移動する対象のファイルか判定する。"""
    return (
        path.is_file()
        and (
            path.name.endswith(".txt")
            or (path.name.endswith(".jpg") and not path.name.endswith("_img_main.jpg"))
            or path.name.endswith(".png")
            or path.name.endswith("dlsite_info.json")
        )
    )


def process_folder(folder_path: Path) -> None:
    """作業フォルダ内を確認し、対象項目を00_tempfilesへ移動する。"""
    print("=====作業中=====")
    print(f"処理中: {folder_path.name}")

    # 移動先フォルダを準備する
    temp_path = folder_path / TEMP_FOLDER_NAME
    temp_path.mkdir(exist_ok=True)

    # フォルダ内の各項目を種類に応じて処理する
    for source in list(folder_path.iterdir()):
        try:
            # 「日本語」内の項目を親へ移し、空になったフォルダを退避する
            if source.name == "日本語" and source.is_dir():
                destination = temp_path / source.name
                if destination.exists():
                    raise FileExistsError(f"移動先に同名の項目があります: {destination}")
                move_japanese_contents(source, folder_path)
                move_without_overwrite(source, destination)
                print(f"移動: 日本語 -> {TEMP_FOLDER_NAME}")
                continue

            # 他言語フォルダは内容を変更せず、そのまま退避する
            if source.name in EXTRA_FOLDERS and source.is_dir():
                move_without_overwrite(source, temp_path / source.name)
                print(f"移動: {source.name} -> {TEMP_FOLDER_NAME}")
                continue

            # 対象ファイルを退避する
            if should_move_file(source):
                destination = temp_path / source.name
                move_without_overwrite(source, destination)
                print(f"移動: {source.name} -> {TEMP_FOLDER_NAME}")
        except OSError as error:
            print(f"移動失敗: {source.name} ({error})")

    print("==============")


def main() -> None:
    """設定から作業場所を読み込み、直下の各フォルダを処理する。"""
    # JSON設定ファイルから作業フォルダの場所を取得する
    config_path = Path.cwd() / "json" / "paths.json"
    with config_path.open("r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    # 作業フォルダ直下のサブフォルダを順番に処理する
    work_path = Path(config["work"]["path"])
    for folder_path in list(work_path.iterdir()):
        if folder_path.is_dir():
            process_folder(folder_path)


if __name__ == "__main__":
    main()
