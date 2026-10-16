import os
import re
import json


def count_audio_files(base_path, folder_names):
    """指定フォルダ直下にあるMP3・FLACファイル数を集計する。"""
    mp3_count = 0
    flac_count = 0

    for folder in folder_names:
        folder_path = os.path.join(base_path, folder)
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if not os.path.isfile(file_path):
                continue
            if file.lower().endswith(".mp3"):
                mp3_count += 1
            elif file.lower().endswith(".flac"):
                flac_count += 1

    return mp3_count, flac_count


#jsonファイルの読み込み
f = open(f"{os.getcwd()}\\json\\paths.json", 'r')
dict_json = json.load(f)
f.close()

#作業フォルダを取得
comp_path = dict_json['comp']['path']
esc_path = dict_json['esc']['path']
addfiles_path = dict_json['addfiles']['path']

#フォルダの一覧を取得
files_and_folders = os.listdir(comp_path)
folders = [f for f in files_and_folders if os.path.isdir(os.path.join(comp_path, f))]

#全フォルダ直下にあるmp3およびflacファイルの数を取得（サブディレクトリは対象外）
mp3_count, flac_count = count_audio_files(comp_path, folders)

#対象外フォルダの設定
NotTarget = {"スタジオりふれぼ", "じゅじゅっとウェルダン", "青春×フェティシズム"}
moved_mp3_count = 0
moved_flac_count = 0
excluded_folder_count = 0

for folder in folders:
    target_folder = re.sub(r"\\ ", " ", f"{comp_path}{folder}")
    moved_files = []

    try :
        #対象外のフォルダをescへ移動 if folder.lower() not in NotTarget:
        if folder.lower() in NotTarget:
        #if NotTarget in folder.lower():
            os.rename(os.path.join(comp_path, folder), os.path.join(esc_path, folder))
            excluded_folder_count += 1
            print("対象外です")

        else :
            all_files = os.listdir(target_folder)
            moved_files = os.listdir(addfiles_path)
            
            #フォルダ内のmp3またはflacファイルを取得
            target_files = [file for file in all_files if file.lower().endswith(".mp3")]
            
            if target_files == []:
                target_files = [file for file in all_files if file.lower().endswith(".flac")]
            
            #移動先フォルダに同名ファイルがあるか確認
            and_list = set(target_files) & set(moved_files)
            if len(and_list) > 0 :
                #ファイル移動は行わず、フォルダをescへ
                os.rename(os.path.join(comp_path, folder), os.path.join(esc_path, folder))
                excluded_folder_count += 1
                print("対象外です")

            else :
                #ファイルをaddfilesフォルダへ移動
                for target_file in target_files :
                    os.rename(re.sub(r"\\ ", " ", f"{target_folder}\\{target_file}"), re.sub(r"\\ ", " ", f"{addfiles_path}{target_file}"))
                    if target_file.lower().endswith(".mp3"):
                        moved_mp3_count += 1
                    elif target_file.lower().endswith(".flac"):
                        moved_flac_count += 1
                
                #終わったら02_okフォルダへ移動
                #os.rename(os.path.join(comp_path, folder), os.path.join(comp_path, folder))       
    except :
        print("移動に失敗しました")
        os.rename(os.path.join(comp_path, folder), os.path.join(esc_path, folder))
        excluded_folder_count += 1

#escフォルダ内のmp3およびflacファイルの数を取得（サブディレクトリは対象外）
esc_mp3_count, esc_flac_count = count_audio_files(esc_path, os.listdir(esc_path))

calculate_mp3_total = mp3_count - moved_mp3_count - esc_mp3_count
calculate_flac_total = flac_count - moved_flac_count - esc_flac_count

missed_mp3_count, missed_flac_count = count_audio_files(comp_path, os.listdir(comp_path))

print("全てのファイルを移動しました")
print(f"対象ファイル数                   : mp3 : {mp3_count}, FLAC : {flac_count}")
print(f"移動したファイル数                : mp3 : {moved_mp3_count}, flac :{moved_flac_count}")
print(f"移動漏れファイル数                : mp3 : {missed_mp3_count}, flac : {missed_flac_count}")
print(f"対象外にしたフォルダ数            : {excluded_folder_count}個")
print(f"対象外にしたフォルダ内のファイル数 : mp3 : {esc_mp3_count}, flac : {esc_flac_count}")
print(f"合計ファイル数                   : mp3 : {calculate_mp3_total}, flac : {calculate_flac_total}")

input("終了するにはEnterキーを押してください...")
