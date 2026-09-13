import os
import subprocess
from collections import Counter
from fractions import Fraction


# ==========================================
# 固定設定
# ==========================================

OUTPUT_FILENAME = "output.mp4"

# 支援的影片副檔名
VIDEO_EXTS = (
    ".mp4",
    ".mkv",
    ".mov",
    ".avi",
    ".wmv",
    ".flv",
    ".webm",
    ".m4v",
)

LIST_FILE = "filelist.txt"


# ==========================================
# FPS 格式化
# ==========================================

def format_fps(value):

    if not value or value == "0/0":
        return "未知"

    try:

        number = float(Fraction(value))

        if abs(number - round(number)) < 0.01:
            return f"{round(number)} fps"

        return f"{number:.2f} fps"

    except Exception:

        return value


# ==========================================
# FFprobe 取得 Video 資訊
# ==========================================

def get_video_info(file_path):

    cmd = [
        "ffprobe",
        "-v", "error",

        "-select_streams", "v:0",

        "-show_entries",
        (
            "stream="
            "codec_name,"
            "width,"
            "height,"
            "avg_frame_rate,"
            "r_frame_rate,"
            "time_base,"
            "start_time,"
            "duration"
        ),

        "-of",
        "default=noprint_wrappers=1:nokey=0",

        file_path
    ]

    try:

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if result.returncode != 0:
            return None

        data = {}

        for line in result.stdout.splitlines():

            if "=" in line:

                key, value = line.split(
                    "=",
                    1
                )

                data[key.strip()] = value.strip()

        width = data.get("width")
        height = data.get("height")

        if width and height:
            resolution = f"{width}x{height}"
        else:
            resolution = "未知"

        return {
            "codec": data.get(
                "codec_name",
                "未知"
            ),

            "resolution": resolution,

            "fps": format_fps(
                data.get(
                    "avg_frame_rate",
                    ""
                )
            ),

            "avg_frame_rate":
                data.get(
                    "avg_frame_rate",
                    "未知"
                ),

            "r_frame_rate":
                data.get(
                    "r_frame_rate",
                    "未知"
                ),

            "time_base":
                data.get(
                    "time_base",
                    "未知"
                ),

            "start_time":
                data.get(
                    "start_time",
                    "未知"
                ),

            "duration":
                data.get(
                    "duration",
                    "未知"
                )
        }

    except Exception:

        return None


# ==========================================
# FFprobe 取得 Audio Codec
# ==========================================

def get_audio_info(file_path):

    cmd = [
        "ffprobe",
        "-v", "error",

        "-select_streams", "a:0",

        "-show_entries",
        "stream=codec_name,sample_rate,channels",

        "-of",
        "default=noprint_wrappers=1:nokey=0",

        file_path
    ]

    try:

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if result.returncode != 0:
            return {
                "codec": "無音訊",
                "sample_rate": "-",
                "channels": "-"
            }

        data = {}

        for line in result.stdout.splitlines():

            if "=" in line:

                key, value = line.split(
                    "=",
                    1
                )

                data[key.strip()] = value.strip()

        return {
            "codec": data.get(
                "codec_name",
                "未知"
            ),

            "sample_rate": data.get(
                "sample_rate",
                "未知"
            ),

            "channels": data.get(
                "channels",
                "未知"
            )
        }

    except Exception:

        return {
            "codec": "未知",
            "sample_rate": "未知",
            "channels": "未知"
        }


# ==========================================
# FFmpeg concat list 檔名處理
# ==========================================

def escape_ffmpeg_filename(filename):

    filename = filename.replace(
        "\\",
        "/"
    )

    filename = filename.replace(
        "'",
        r"'\''"
    )

    return filename


# ==========================================
# 取得影片 duration
# ==========================================

def get_duration(file_path):

    cmd = [
        "ffprobe",
        "-v", "error",

        "-show_entries",
        "format=duration",

        "-of",
        "default=noprint_wrappers=1:nokey=1",

        file_path
    ]

    try:

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        value = result.stdout.strip()

        if value:
            return float(value)

    except Exception:
        pass

    return None


# ==========================================
# 主程式
# ==========================================

def main():

    # --------------------------------------
    # 1. 輸入來源資料夾
    # --------------------------------------

    raw_input_path = input(
        "請輸入影片資料夾的絕對路徑: "
    )

    source_folder = (
        raw_input_path
        .strip()
        .strip('"')
    )

    if not os.path.isdir(source_folder):

        print(
            f"\n錯誤：找不到此來源資料夾 -> "
            f"{source_folder}"
        )

        return
        
    OUTPUT_FILE_PATH = os.path.join(
        source_folder,
        OUTPUT_FILENAME
    )
    
    # --------------------------------------
    # 2. 切換來源資料夾
    # --------------------------------------

    os.chdir(source_folder)

    # --------------------------------------
    # 3. 找所有影片
    # --------------------------------------

    files = [
        f
        for f in os.listdir(".")
        if (
            os.path.isfile(f)
            and f.lower().endswith(VIDEO_EXTS)
            and f.lower() != "output.mp4"
        )
    ]

    if not files:

        print(
            "\n錯誤：找不到任何影片檔案。"
        )

        print("\n支援的副檔名：")

        print(
            " ".join(VIDEO_EXTS)
        )

        return

    # --------------------------------------
    # 4. 讀取影片資訊
    # --------------------------------------

    print("\n")
    print("========================================")
    print("正在讀取影片資訊...")
    print("========================================")
    print()

    video_info = []

    for index, file in enumerate(
        files,
        start=1
    ):

        print(
            f"[{index}/{len(files)}] {file}"
        )

        video = get_video_info(file)
        audio = get_audio_info(file)

        if video is None:

            video = {
                "codec": "未知",
                "resolution": "未知",
                "fps": "未知",
                "avg_frame_rate": "未知",
                "r_frame_rate": "未知",
                "time_base": "未知",
                "start_time": "未知",
                "duration": "未知"
            }

        video_info.append({
            "name": file,
            **video,
            "audio_codec": audio["codec"],
            "sample_rate": audio["sample_rate"],
            "channels": audio["channels"]
        })

    # --------------------------------------
    # 5. 解析度統計
    # --------------------------------------

    resolution_counter = Counter(
        item["resolution"]
        for item in video_info
    )

    print("\n")
    print("========================================")
    print("影片解析度統計")
    print("========================================")

    for resolution, count in (
        resolution_counter.most_common()
    ):

        print(
            f"{resolution}：{count} 個"
        )

    print(
        f"\n總影片數：{len(files)} 個"
    )

    # --------------------------------------
    # 6. 詳細資訊
    # --------------------------------------

    print("\n")
    print("========================================")
    print("影片詳細資訊")
    print("========================================")

    for index, item in enumerate(
        video_info,
        start=1
    ):

        print()
        print(
            f"[{index}] {item['name']}"
        )

        print(
            f"    解析度       : "
            f"{item['resolution']}"
        )

        print(
            f"    FPS          : "
            f"{item['fps']}"
        )

        print(
            f"    Video Codec  : "
            f"{item['codec']}"
        )

        print(
            f"    Audio Codec  : "
            f"{item['audio_codec']}"
        )

        print(
            f"    Sample Rate  : "
            f"{item['sample_rate']}"
        )

        print(
            f"    Channels     : "
            f"{item['channels']}"
        )

        print(
            f"    r_frame_rate : "
            f"{item['r_frame_rate']}"
        )

        print(
            f"    avg_frame_rate: "
            f"{item['avg_frame_rate']}"
        )

        print(
            f"    time_base    : "
            f"{item['time_base']}"
        )

        print(
            f"    start_time   : "
            f"{item['start_time']}"
        )

        print(
            f"    duration     : "
            f"{item['duration']}"
        )

    # --------------------------------------
    # 7. 選擇排序
    # --------------------------------------

    print("\n")
    print("========================================")
    print("請選擇影片排序方式")
    print("========================================")

    print("1. 依檔案名稱排序")
    print("2. 依檔案修改時間排序")

    while True:

        sort_choice = input(
            "\n請輸入 1 或 2: "
        ).strip()

        if sort_choice in ["1", "2"]:
            break

        print(
            "輸入錯誤，請輸入 1 或 2。"
        )

    if sort_choice == "1":

        print(
            "\n已選擇：依檔案名稱排序"
        )

        files.sort(
            key=lambda x: x.lower()
        )

    else:

        print(
            "\n已選擇：依檔案修改時間排序"
        )

        files.sort(
            key=lambda x: os.path.getmtime(x)
        )

    # --------------------------------------
    # 8. 顯示最終順序
    # --------------------------------------

    print("\n")
    print("========================================")
    print("最後合併順序")
    print("========================================")

    for index, file in enumerate(
        files,
        start=1
    ):

        print(
            f"{index:>3}. {file}"
        )

    # --------------------------------------
    # 9. 確認
    # --------------------------------------

    print()

    confirm = input(
        "確定要按照以上順序合併嗎？(Y/N): "
    ).strip().lower()

    if confirm != "y":

        print(
            "\n已取消合併。"
        )

        return

    # --------------------------------------
    # 10. 建立 filelist.txt
    # --------------------------------------

    with open(
        LIST_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        for file in files:

            safe_name = (
                escape_ffmpeg_filename(file)
            )

            f.write(
                f"file '{safe_name}'\n"
            )

    print(
        f"\n成功建立清單：{LIST_FILE}"
    )
    # ==========================================
    # 11. 預估所有來源影片總長度
    # ==========================================

    expected_duration = 0.0

    print("\n")
    print("========================================")
    print("計算來源影片總長度...")
    print("========================================")

    for file in files:

        duration = get_duration(file)

        if duration is not None:

            expected_duration += duration

            print(
                f"{file:<40} "
                f"{duration:.3f} 秒"
            )

    print(
        f"\n來源影片總長度：約 "
        f"{expected_duration:.3f} 秒"
    )


    # ==========================================
    # 12. 建立暫存 TS 資料夾
    # ==========================================

    TEMP_TS_FOLDER = os.path.join(
        source_folder,
        "_ffmpeg_temp_ts"
    )

    os.makedirs(
        TEMP_TS_FOLDER,
        exist_ok=True
    )

    ts_files = []


    # ==========================================
    # 13. 每個影片先轉成 TS
    #
    # 注意：
    # 這裡「不重新編碼」
    # H.264 / AAC 都直接 copy
    # ==========================================

    print("\n")
    print("========================================")
    print("正在建立暫存 TS...")
    print("========================================")

    for index, file in enumerate(
        files,
        start=1
    ):

        ts_path = os.path.join(
            TEMP_TS_FOLDER,
            f"part_{index:05d}.ts"
        )

        print()
        print(
            f"[{index}/{len(files)}] "
            f"{file}"
        )

        cmd_ts = [
            "ffmpeg",

            "-hide_banner",

            "-i",
            file,

            # ----------------------------------
            # 只取第一組 Video / Audio
            # ----------------------------------

            "-map", "0:v:0",
            "-map", "0:a:0?",

            # ----------------------------------
            # 不重新編碼
            # ----------------------------------

            "-c", "copy",

            # ----------------------------------
            # 讓 timestamp 從 0 開始
            # ----------------------------------

            "-start_at_zero",

            "-avoid_negative_ts",
            "make_zero",

            # ----------------------------------
            # H.264 → Annex B
            #
            # TS 使用 H.264 Annex B
            # ----------------------------------

            "-bsf:v",
            "h264_mp4toannexb",

            # ----------------------------------
            # MPEG-TS
            # ----------------------------------

            "-f",
            "mpegts",

            "-y",

            ts_path
        ]

        try:

            result = subprocess.run(
                cmd_ts,
                check=False
            )

        except FileNotFoundError:

            print(
                "\n錯誤：找不到 ffmpeg。"
            )

            return

        if result.returncode != 0:

            print()
            print(
                "❌ 無法建立 TS："
                f"{file}"
            )

            print(
                "\n暫存資料保留："
                f"{TEMP_TS_FOLDER}"
            )

            return

        ts_files.append(ts_path)


    # ==========================================
    # 14. 建立 TS concat 清單
    # ==========================================

    TS_LIST_FILE = os.path.join(
        TEMP_TS_FOLDER,
        "tslist.txt"
    )

    with open(
        TS_LIST_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        for ts_file in ts_files:

            safe_path = (
                ts_file
                .replace("\\", "/")
                .replace("'", r"'\''")
            )

            f.write(
                f"file '{safe_path}'\n"
            )


    # ==========================================
    # 15. 使用 TS concat + stream copy
    # ==========================================

    print("\n")
    print("========================================")
    print("正在串接 TS...")
    print("========================================")

    TEMP_OUTPUT_TS = os.path.join(
        TEMP_TS_FOLDER,
        "merged.ts"
    )

    cmd_concat_ts = [
        "ffmpeg",

        "-hide_banner",

        "-f",
        "concat",

        "-safe",
        "0",

        "-i",
        TS_LIST_FILE,

        # ----------------------------------
        # 直接複製
        # ----------------------------------

        "-c",
        "copy",

        "-y",

        TEMP_OUTPUT_TS
    ]

    try:

        result = subprocess.run(
            cmd_concat_ts,
            check=False
        )

    except FileNotFoundError:

        print(
            "\n錯誤：找不到 ffmpeg。"
        )

        return

    if result.returncode != 0:

        print()
        print(
            "❌ TS 串接失敗。"
        )

        print(
            f"\n暫存資料保留："
            f"{TEMP_TS_FOLDER}"
        )

        return


    # ==========================================
    # 16. TS → 最終 MP4
    #
    # 仍然不重新編碼
    # ==========================================

    print("\n")
    print("========================================")
    print("正在輸出 MP4...")
    print("========================================")

    cmd_final = [
        "ffmpeg",

        "-hide_banner",

        "-i",
        TEMP_OUTPUT_TS,

        # ----------------------------------
        # Video / Audio
        # ----------------------------------

        "-map", "0:v:0",
        "-map", "0:a:0?",

        # ----------------------------------
        # 完全不重新編碼
        # ----------------------------------

        "-c",
        "copy",

        # ----------------------------------
        # 避免負 timestamp
        # ----------------------------------

        "-avoid_negative_ts",
        "make_zero",

        # ----------------------------------
        # MP4
        # ----------------------------------

        "-movflags",
        "+faststart",

        "-y",

        OUTPUT_FILE_PATH
    ]

    try:

        result = subprocess.run(
            cmd_final,
            check=False
        )

    except FileNotFoundError:

        print(
            "\n錯誤：找不到 ffmpeg。"
        )

        return

    if result.returncode != 0:

        print()
        print(
            "❌ 最終 MP4 輸出失敗。"
        )

        print(
            f"\n暫存資料保留："
            f"{TEMP_TS_FOLDER}"
        )

        return


    # ==========================================
    # 17. 驗證最終輸出 duration
    # ==========================================

    print("\n")
    print("========================================")
    print("正在驗證輸出影片...")
    print("========================================")

    output_duration = get_duration(
        OUTPUT_FILE_PATH
    )

    if output_duration is None:

        print(
            "\n❌ 無法讀取輸出影片 duration。"
        )

        return


    print(
        f"\n來源影片總長度："
        f"{expected_duration:.3f} 秒"
    )

    print(
        f"輸出影片長度："
        f"{output_duration:.3f} 秒"
    )


    # ==========================================
    # 18. 檢查 duration
    # ==========================================

    if expected_duration > 0:

        difference = abs(
            output_duration
            - expected_duration
        )

        print(
            f"時間差："
            f"{difference:.3f} 秒"
        )

        # --------------------------------------
        # 如果差距超過 2 秒，視為異常
        # --------------------------------------

        if difference > 2.0:

            print("\n")
            print("========================================")
            print("❌ 時間軸仍然異常")
            print("========================================")

            print(
                "\n程式不會把這個結果判定為成功。"
            )

            print(
                "\n來源與輸出 duration 差異過大。"
            )

            print(
                f"\n暫存 TS 保留於："
                f"{TEMP_TS_FOLDER}"
            )

            return


    # ==========================================
    # 19. 成功
    # ==========================================

    print("\n")
    print("========================================")
    print("✅ 合併成功！")
    print("========================================")

    print(
        f"\n輸出："
        f"{OUTPUT_FILE_PATH}"
    )

    print(
        f"\n最終長度："
        f"{output_duration:.3f} 秒"
    )

    print(
        "\n影片沒有重新編碼。"
    )

    print(
        "H.264 / AAC 均使用 Stream Copy。"
    )


    # ==========================================
    # 20. 清理暫存
    # ==========================================

    try:

        if os.path.exists(
            TS_LIST_FILE
        ):
            os.remove(
                TS_LIST_FILE
            )

        if os.path.exists(
            TEMP_OUTPUT_TS
        ):
            os.remove(
                TEMP_OUTPUT_TS
            )

        for ts_file in ts_files:

            if os.path.exists(ts_file):

                os.remove(ts_file)

        if os.path.exists(
            TEMP_TS_FOLDER
        ):

            os.rmdir(
                TEMP_TS_FOLDER
            )

        print(
            "\n已清理所有暫存 TS。"
        )

    except Exception as e:

        print(
            "\n⚠️ 暫存檔清理失敗："
            f"{e}"
        )



# ==========================================
# 程式入口
# ==========================================

if __name__ == "__main__":
    main()
