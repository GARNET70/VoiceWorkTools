import os
import re
import json
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
import ffmpeg
import subprocess

INPUT_JSON_NAME = "metainfo.json"

#クラス定義
class MetaInfo:
    def __init__(self, albumtitle, albumartist, artist):
        self.albumtitle = albumtitle
        self.albumartist = albumartist
        self.artist = artist

def convert_wav4mp3(path, musics_wav):

    for music_name in musics_wav:
        output_name = music_name.replace(".wav", ".mp3")
        target_path = re.sub(r"\\ ", " ", f"{path}\\{music_name}")

        # 入力ストリームを作成
        input_stream = ffmpeg.input(target_path)

        # 出力ストリームを作成
        output_stream = ffmpeg.output(input_stream, re.sub(r"\\ ", " ", f"{path}\\00 {output_name}"))

        # 変換を実行
        ffmpeg.run(output_stream)

        # wavファイルを移動
        backup_name = re.sub(r"\\ ", " ", f"{path}\\Original\\{music_name}")
        os.rename(target_path, backup_name)

def convert_flac4mp3(path, musics_flac):
    for music_name in musics_flac:
        output_name = music_name.replace(".flac", ".mp3")
        output_path = re.sub(r"\\ ", " ", f"{path}\\{output_name}")
        target_path = re.sub(r"\\ ", " ", f"{path}\\{music_name}")

        # ffmpegで変換実行
        command = [
            "ffmpeg",
            "-y",  # 上書き確認なし
            "-i", target_path,
            "-codec:a", "libmp3lame",
            "-qscale:a", "2",  # 音質（2 = 高品質）
            output_path
        ]

        # 変換を実行
        subprocess.run(command, check=True)

        # wavファイルを移動
        backup_name = re.sub(r"\\ ", " ", f"{path}\\Original\\{music_name}")
        os.rename(target_path, backup_name)

def set_MetaData(path, all_files, jdata, type):
    #フォルダ内のjpgファイル探して名称取得
    #all_files = os.listdir(re.sub(r"\\ ", " ", f"{work_path}{folder}"))
    #alubumart_extension = "jpeg"
    alubumart = [file for file in all_files if file.lower().endswith(".jpg") or file.lower().endswith(".jpeg")]

    if alubumart == []:
        alubumart = [file for file in all_files if file.lower().endswith(".png")]
        #alubumart_extension = "png"

    impath = re.sub(r"\\ ", " ", f"{path}\\{alubumart[0]}")

    #拡張子ごとに処理分岐
    if type in "mp3":
        musics_mp3 = [file for file in all_files if file.lower().endswith(".mp3")]

        for music_name in musics_mp3:
            target_path = re.sub(r"\\ ", " ", f"{path}\\{music_name}")
            
            #メタ情報設定
            try :
                target = EasyID3(target_path)
                target['title'] = music_name.replace("00 ", "").replace(".mp3", "")
                target["album"] = jdata.albumtitle
                target['albumartist'] = jdata.albumartist
                target["artist"] = jdata.artist
                target.save()

                #アートワークを設定
                tags = ID3(target_path)
                with open(impath, 'rb') as img_file:
                    cover_img_byte_str = img_file.read()
                    tags.add(APIC(mime='image/jpeg', type=3, data=cover_img_byte_str))
                    tags.save()
            except :
                print("ID3タグが見つかりませんでした。")

    elif type in "flac":
        backup_path = re.sub(r"\\ ", " ", f"{path}\\Original")
        musics_flac = [file for file in all_files if file.lower().endswith(".flac")]

        for music_name in musics_flac:
            target_path = re.sub(r"\\ ", " ", f"{path}\\{music_name}")
            
            #メタ情報設定
            target = FLAC(target_path)
            target["album"] = jdata.albumtitle
            target['albumartist'] = jdata.albumartist
            target["artist"] = jdata.artist
            target.save()
            backup_name = re.sub(r"\\ ", " ", f"{backup_path}\\{music_name}")
            os.rename(target_path, backup_name)

            #アートワークを設定
            #os.system(f'{batch_file_name} {backup_name} {impath} {target_path}')
            cmd = [
                "ffmpeg",
                "-i", backup_name,
                "-i", impath,
                "-map", "0:a",
                "-map", "1:v",
                "-c", "copy",
                "-disposition:1", "attached_pic",
                target_path
            ]
            
            try:
                subprocess.run(cmd, check=True)
                #print(f"アートワークを {target_path} に追加しました。")
            except subprocess.CalledProcessError as e:
                print(f"エラーが発生しました: {e}")

#jsonファイルの読み込み
f = open(f"{os.getcwd()}\\json\\paths.json", 'r')
dict_json = json.load(f)
f.close()

#作業フォルダを取得
work_path = dict_json['work']['path']
comp_path = dict_json['comp']['path']
esc_path = dict_json['esc']['path']
#batch_file_name = f"{os.getcwd()}\\bat\\AddImage.bat"

#フォルダの一覧を取得
files_and_folders = os.listdir(work_path)
folders = [f for f in files_and_folders if os.path.isdir(os.path.join(work_path, f))]

#各フォルダのjsonファイルを取得
for folder in folders:
    #jsonファイルの有無チェック
    target_folder = re.sub(r"\\ ", " ", f"{work_path}{folder}")
    all_files = os.listdir(target_folder)
    target_files = [file for file in all_files if file.lower().endswith(".json")]

    if target_files:
        #jsonファイルの読み込み
        json_path = re.sub(r"\\ ", " ", f"{target_folder}\\{INPUT_JSON_NAME}")
        f = open(json_path, 'r', encoding="utf-8-sig")
        meta_json = json.load(f)
        f.close()
        metadata = MetaInfo(meta_json["albumtitle"], meta_json["albumartist"], meta_json["artist"])

        # mp3以外を変換
        file_type4wav =  [file for file in all_files if file.lower().endswith(".wav")]
        if file_type4wav:
            #バックアップフォルダの作成
            if not os.path.exists(f"{target_folder}\\Original"):
                os.makedirs(f"{target_folder}\\Original")

            print(f"target : {folder}")
            convert_wav4mp3(target_folder, file_type4wav)
        
        file_type4flac =  [file for file in all_files if file.lower().endswith(".flac")]
        if file_type4flac:
            #バックアップフォルダの作成
            if not os.path.exists(f"{target_folder}\\Original"):
                os.makedirs(f"{target_folder}\\Original")

            print(f"target : {folder}")
            convert_flac4mp3(target_folder, file_type4flac)

        # メタデータを設定
        re_all_files = os.listdir(target_folder) 
        set_MetaData(target_folder, re_all_files, metadata, "mp3")

        #設定が終わったら02_okへ移動
        os.rename(os.path.join(work_path, folder), os.path.join(comp_path, folder))
    else :
        print("jsonファイルがありません")
        os.rename(os.path.join(work_path, folder), os.path.join(esc_path, folder))

print("全てのファイルの情報設定が終わりました")
