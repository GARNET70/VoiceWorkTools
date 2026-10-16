import json
import os 
import subprocess


def get_windows_filename_error(filename):
    invalid_chars = '<>:"/\\|?*'
    if any(char in invalid_chars or ord(char) < 32 for char in filename):
        return "使用できない文字（または制御文字）が含まれています"
    if filename.endswith((" ", ".")):
        return "末尾に空白またはピリオドは使用できません"

    device_name = filename.split(".", 1)[0].rstrip(" .").upper()
    reserved_names = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
    numbered_device = (
        len(device_name) == 4
        and device_name[:3] in {"COM", "LPT"}
        and device_name[3] in "123456789¹²³"
    )
    if device_name in reserved_names or numbered_device:
        return f"予約されたデバイス名「{device_name}」は使用できません"

    return None


#jsonファイルの読み込み
f = open(f"{os.getcwd()}\\json\\paths.json", 'r')
dict_json = json.load(f)
f.close()

#作業フォルダを取得
rename_path = dict_json['rename']['path']
work_path = dict_json['work']['path']
rar_path = dict_json['rar']['path']
winrar_exe = r"C:\Program Files\WinRAR\WinRAR.exe"

#フォルダの一覧を取得
files_and_folders = os.listdir(rename_path)
folders = [f for f in files_and_folders if os.path.isdir(os.path.join(rename_path, f))]

#rarファイルへ他のファイルを追加
for folder in folders:
    rar_filename = f"{folder}.rar"
    filename_error = get_windows_filename_error(rar_filename)
    if filename_error:
        print(
            f"RARファイル名がWindowsの規則に反しているため"
            f"スキップします: {rar_filename} ({filename_error})"
        )
        continue

    print("=====作成中=====")
    print(f"処理中: {folder}")
    #RARファイルを作成
    try:
        subprocess.run(
            [
                winrar_exe,
                "a",
                "-r",
                "-ep1",
                rar_filename,
                os.path.join(folder, "*"),
            ],
            cwd=rename_path,
            check=True,
        )
        print("RARファイル作成完了")

        #追加後にrarを移動
        try:
            os.replace(
                os.path.join(rename_path, rar_filename),
                os.path.join(rar_path, rar_filename),
            )
            print("RARファイルの移動完了")

            try:
                os.replace(
                    os.path.join(rename_path, f"{folder}"),
                    os.path.join(work_path, f"{folder}"),
                )
                print("フォルダの移動完了")
            except OSError as e:
                print(f"フォルダの移動失敗: {e}")
        except OSError as e:
            print(f"RARファイルの移動失敗: {e}")
    except subprocess.CalledProcessError as e:
        print(f"作成失敗（終了コード: {e.returncode}）")

    print("================")