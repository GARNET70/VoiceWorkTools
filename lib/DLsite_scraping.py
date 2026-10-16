import json
from pathlib import Path
import time
from typing import Any
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 Safari/537.36"
    )
}
DEFAULT_OUTPUT_ROOT = "downloads"
REQUEST_TIMEOUT = 30
DOWNLOAD_REQUEST_INTERVAL_SECONDS = 1.0
METADATA_FIELDS_NAME = "dlsite_info.json"

class DLsiteDownloader:
    """DLsite作品のメタ情報と画像を取得して保存する。"""

    def __init__(
        self,
        rj_id: str,
        output_root: str | Path = DEFAULT_OUTPUT_ROOT,
        timeout: int = REQUEST_TIMEOUT,
    ) -> None:
        """作品番号と保存先を設定し、ダウンロードに必要な情報を初期化する。"""
        self.rj_id = rj_id.upper()
        self.timeout = timeout
        self.product_url = (
            "https://www.dlsite.com/maniax/work/"
            f"=/product_id/{self.rj_id}.html"
        )
        #self.output_dir = Path(output_root) / self.rj_id
        self.output_dir = Path(output_root)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.image_urls: list[str] = []

        self.metadata: dict[str, Any] = {
            "rj_id": self.rj_id,
            "url": self.product_url,
            "title": None,
            "circle": None,
            "sale_date": None,
            "voice_actor": None,
            "age_rating": None,
            "images": [],
        }

    def get_soup(self) -> BeautifulSoup:
        """作品ページを取得し、解析可能なBeautifulSoupオブジェクトを返す。"""
        response = requests.get(
            self.product_url,
            headers=HEADERS,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def get_image_urls(self, soup: BeautifulSoup) -> list[str]:
        """作品ページの画像欄から重複を除いた画像URL一覧を取得する。
        Args:
            soup: 解析対象の作品ページ。
        Returns:
            絶対URL形式の画像URL一覧。
        Raises:
            ValueError: ページに画像欄が見つからない場合。
        """
        image_container = soup.select_one("#work_left")
        if image_container is None:
            raise ValueError("作品ページに画像欄 (#work_left) が見つかりません。")

        image_urls: list[str] = []
        seen_urls: set[str] = set()
        image_elements = image_container.select(
            'meta[itemprop="image"][content], [data-src], img[src]'
        )

        for element in image_elements:
            image_url = (
                element.get("data-src")
                or element.get("content")
                or element.get("src")
            )
            if not isinstance(image_url, str) or not image_url.strip():
                continue

            absolute_url = urljoin(self.product_url, image_url.strip())
            if absolute_url not in seen_urls:
                seen_urls.add(absolute_url)
                image_urls.append(absolute_url)

        return image_urls

    @staticmethod
    def get_text_by_label(
        soup: BeautifulSoup,
        labels: list[str],
    ) -> str | None:
        """指定したラベルに対応する表の値をページから取得する。
        Args:
            soup: 解析対象の作品ページ。
            labels: 値を探す際に照合するラベル文字列。
        Returns:
            最初に一致したラベルの値。一致しない場合はNone。
        """
        for row in soup.select("tr"):
            header = row.find("th")
            value = row.find("td")
            if not header or not value:
                continue

            label = header.get_text(strip=True)
            if any(candidate in label for candidate in labels):
                return value.get_text(" ", strip=True)

        return None

    def fetch_metadata(self) -> None:
        """作品ページからメタ情報と掲載画像URLを取得して保持する。"""
        print("メタ情報取得中")
        soup = self.get_soup()
        self.image_urls = self.get_image_urls(soup)

        title_meta = soup.find("meta", property="og:title")
        title = title_meta.get("content") if title_meta else None
        if not title:
            title_heading = soup.find("h1")
            title = title_heading.get_text(strip=True) if title_heading else None
        self.metadata["title"] = title

        self.metadata["circle"] = self.get_text_by_label(
            soup,
            ["サークル名", "サークル"],
        )
        self.metadata["sale_date"] = self.get_text_by_label(
            soup,
            ["販売日", "発売日"],
        )
        self.metadata["voice_actor"] = self.get_text_by_label(
            soup,
            ["声優", "CV"],
        )

        age_rating = self.get_text_by_label(
            soup,
            ["年齢指定", "年齢認証"],
        )
        if not age_rating:
            page_text = soup.get_text(" ", strip=True)
            for rating in ("R18", "R15", "全年齢"):
                if rating in page_text:
                    age_rating = rating
                    break
        self.metadata["age_rating"] = age_rating

    def download_file(self, url: str, save_path: Path) -> bool:
        """URLからファイルを取得し、指定先に保存する。
        リクエスト前にサーバー負荷を抑えるための待機時間を設ける。
        Args:
            url: ダウンロードするファイルのURL。
            save_path: ファイルの保存先。
        Returns:
            保存に成功した場合はTrue、失敗した場合はFalse。
        """
        try:
            time.sleep(DOWNLOAD_REQUEST_INTERVAL_SECONDS)
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=self.timeout,
                stream=True,
            )
            if response.status_code != 200:
                return False

            with save_path.open("wb") as output_file:
                for chunk in response.iter_content(8192):
                    if chunk:
                        output_file.write(chunk)

            return True
        except Exception as error:
            print(f"ERROR: {error}")
            return False

    def download_images(self) -> None:
        """作品ページから取得済みの画像URLを順番にダウンロードする。"""
        if not self.image_urls:
            print("画像欄から画像URLを取得できませんでした。")

        for url in self.image_urls:
            filename = Path(unquote(urlsplit(url).path)).name
            if not filename:
                print(f"画像URLからファイル名を取得できません: {url}")
                continue

            save_path = self.output_dir / filename

            if self.download_file(url, save_path):
                print(f"取得: {filename}")
                image_info: dict[str, Any] = {
                    "type": "main" if "_img_main" in filename else "sample",
                    "file": filename,
                    "url": url,
                }
                if "_img_smp" in filename:
                    image_info["index"] = int(
                        filename.split("_img_smp", maxsplit=1)[1].split(".", maxsplit=1)[0]
                    )
                self.metadata["images"].append(image_info)

    def save_json(self) -> None:
        """取得した作品メタ情報を作品フォルダ内のJSONファイルに保存する。"""
        #json_file = self.output_dir / f"{self.rj_id}.json"
        json_file = self.output_dir / f"{METADATA_FIELDS_NAME}"
        with json_file.open("w", encoding="utf-8") as output_file:
            json.dump(
                self.metadata,
                output_file,
                ensure_ascii=False,
                indent=4,
            )

        print(f"JSON保存: {json_file}")

    def run(self) -> None:
        """メタ情報と画像を取得し、結果を保存する一連の処理を実行する。"""
        print(f"開始: {self.rj_id}")
        self.fetch_metadata()
        self.download_images()
        self.save_json()
        print(f"完了: {len(self.metadata['images'])}画像取得")


if __name__ == "__main__":

    rj_id = input("RJ番号を入力してください: ").strip()
    output_root = input(
        f"保存先フォルダを入力してください (空欄の場合は {DEFAULT_OUTPUT_ROOT}): "
    ).strip() or DEFAULT_OUTPUT_ROOT

    """
    rj_id = "RJ01669833"
    output_root = "D:\\python\\19_GUFileOrganizer\\downloads\\RJ01669833"
    """
    downloader = DLsiteDownloader(rj_id, output_root)
    downloader.run()
