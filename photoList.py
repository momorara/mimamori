
import time

photo_fileName = str(int(time.time())) + '.jpg'

print(photo_fileName)
 # cronで起動する際には絶対パスが必要
path = '/home/' + 'pi' + '/mimamori/'

"""
カレントディレクトリにある .jpg ファイルのリストを作り
timeの値を持つファイルに対して、
一定過去のファイルは除外したリストを作る
2022/05/14
2022/05/15  新しい順に並べ替える
            顔認識できた一番新しいファィル名を返す
            顔認証出来なかった場合は、-1

"""
import glob
import copy
import time

def photoList(past_time,path):
    # jpgの付いたファイル名のリストを作る
    files = glob.glob("*.jpg")

    # 秒のリストを作る
    files_time = copy.copy(files)
    for i in range(len(files)):
        try:
            files_time[i] = int(files[i].replace('.jpg',''))
        except:
            # 秒に変換できない場合は、0として、次のステップで削除する
            files_time[i] = 0

    # 現在から一定程度過去のリストを削除
    current_time = time.time() # 現在
    # past_time   これ以上の過去は削除
    for i in reversed(range(len(files))):
        if files_time[i] < current_time - past_time:
            del files[-1]     # 指定以上の過去は削除

    # 新しい順に並べ替え
    files = sorted(files, reverse=True)

    # パスを追加
    for i in range(len(files)):
        files[i] = path + files[i]

    return files

def moviePhotoList(path):
    # jpgの付いたファイル名のリストを作る
    files = glob.glob("*.jpg")
    # 新しい順に並べ替え
    # files = sorted(files, reverse=True)
    # パスを追加
    # for i in range(len(files)):
    #     files[i] = path + files[i]
    return files

# 全ての jpgリストを作る
def photoList_all(path):
    # jpgの付いたファイル名のリストを作る
    files = glob.glob("*.jpg")
    # パスを追加
    print(files)
    # for i in range(len(files)):
    #     files[i] = path + files[i]
    return files

#[1652402510, 1652402612, 1652402613, 1652402614, 1652402611]
#['1652402510.jpg', '1652402612.jpg', '1652402613.jpg', '1652402614.jpg', '1652402611.jpg']



files = photoList(12000,path)
print(files)