#!/usr/bin/env python3
"""
Download Product Images from URL

Stiahne product images zo zadanej product page URL.
Použiteľné v Kroku 3 ako automatizácia získavania reference images pre generate_ads.py.

Stratégia (v poradí dôležitosti):
1. og:image meta tag (Open Graph — najspoľahlivejšie)
2. JSON-LD Product schema (Schema.org — má často viac variantov)
3. twitter:image meta tag (fallback)

Po stiahnutí: konvertuje na PNG (ak nie je) cez Pillow.

Usage:
    python download-product-images.py \\
      --url https://mojeshop.sk/moj-produkt-moja-znacka.html \\
      --output-dir brands/moja-znacka/products/moj-produkt/source-product-images/

    python download-product-images.py \\
      --url URL --output-dir DIR --max-images 3 --filename-prefix container

    python download-product-images.py --url URL --output-dir DIR --dry-run

Required deps: requests, Pillow (optional pre PNG konverziu)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError:
    print("Error: 'requests' required. Install: pip install requests")
    sys.exit(1)

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,sk;q=0.8",
}


def fetch_page(url):
    """Stiahne HTML."""
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def find_meta_image(html, property_name):
    """Nájde meta tag image (og:image, twitter:image)."""
    patterns = [
        rf'<meta\s+property=["\']{re.escape(property_name)}["\']\s+content=["\']([^"\']+)["\']',
        rf'<meta\s+content=["\']([^"\']+)["\']\s+property=["\']{re.escape(property_name)}["\']',
        rf'<meta\s+name=["\']{re.escape(property_name)}["\']\s+content=["\']([^"\']+)["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def find_json_ld_images(html):
    """Hľadá Product/ProductGroup schema v JSON-LD."""
    images = []
    pattern = r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    for script_match in re.finditer(pattern, html, re.DOTALL):
        try:
            data = json.loads(script_match.group(1).strip())
        except json.JSONDecodeError:
            continue

        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            type_field = item.get("@type", "")
            if isinstance(type_field, list):
                type_match = any(t in ("Product", "ProductGroup") for t in type_field)
            else:
                type_match = type_field in ("Product", "ProductGroup")

            if not type_match:
                continue

            image_field = item.get("image")
            if isinstance(image_field, str):
                images.append(image_field)
            elif isinstance(image_field, list):
                for img in image_field:
                    if isinstance(img, str):
                        images.append(img)
                    elif isinstance(img, dict) and "url" in img:
                        images.append(img["url"])
            elif isinstance(image_field, dict) and "url" in image_field:
                images.append(image_field["url"])

    return images


def collect_product_images(html, base_url):
    """Skombinuje všetky stratégie a vráti deduplicated list URLs."""
    all_images = []

    og_image = find_meta_image(html, "og:image")
    if og_image:
        all_images.append(og_image)

    twitter_image = find_meta_image(html, "twitter:image")
    if twitter_image and twitter_image != og_image:
        all_images.append(twitter_image)

    for img in find_json_ld_images(html):
        if img not in all_images:
            all_images.append(img)

    return [urljoin(base_url, img) for img in all_images]


def download_image(url, save_path):
    """Stiahne obrázok."""
    response = requests.get(url, headers=HEADERS, timeout=60, stream=True)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "").lower()
    if content_type and not content_type.startswith("image/"):
        raise ValueError(f"Not an image: Content-Type={content_type}")

    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return save_path


def convert_to_png(input_path, output_path):
    """Konvertuje obrázok do PNG (transparentnosť zachovaná pre RGBA)."""
    if not PILLOW_AVAILABLE:
        return False
    try:
        img = Image.open(input_path)
        if img.mode in ("RGBA", "LA"):
            pass  # Zachovaj transparency
        elif img.mode == "P" and "transparency" in img.info:
            img = img.convert("RGBA")
        else:
            img = img.convert("RGB")
        img.save(output_path, "PNG")
        return True
    except Exception as e:
        print(f"     ⚠ Conversion failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Download product images from URL (og:image + JSON-LD)")
    parser.add_argument("--url", required=True, help="Product page URL")
    parser.add_argument("--output-dir", required=True, help="Where to save images")
    parser.add_argument("--filename-prefix", default="product",
                        help="Prefix pre output filenames (default: product)")
    parser.add_argument("--max-images", type=int, default=5,
                        help="Max obrázkov stiahnutých (default: 5)")
    parser.add_argument("--no-png-convert", action="store_true",
                        help="Neprevádzaj na PNG, ponechaj originálny formát")
    parser.add_argument("--dry-run", action="store_true",
                        help="Zobrazí nájdené URLs bez sťahovania")

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  Product Image Downloader")
    print(f"  URL:      {args.url}")
    print(f"  Output:   {output_dir}")
    print(f"  Max imgs: {args.max_images}")
    print(f"{'='*60}\n")

    print("Fetching HTML...")
    try:
        html = fetch_page(args.url)
    except Exception as e:
        print(f"✗ Failed to fetch URL: {e}")
        sys.exit(1)
    print(f"  ✓ {len(html)} bytes")

    print("\nExtracting image URLs...")
    images = collect_product_images(html, args.url)

    if not images:
        print("✗ Žiadne product images sa nenašli.")
        print("  Stratégie skúšané: og:image, twitter:image, JSON-LD Product schema.")
        print("  Skús inspect page manuálne (DevTools → Elements → meta tags).")
        sys.exit(1)

    images_to_download = images[:args.max_images]
    print(f"  ✓ Nájdených {len(images)} URL(s), stiahne sa {len(images_to_download)}:\n")
    for i, img_url in enumerate(images_to_download, 1):
        display = img_url if len(img_url) <= 90 else img_url[:87] + "..."
        print(f"  [{i}] {display}")

    if args.dry_run:
        print("\n(dry-run — žiadne sťahovanie)")
        return

    print("\nDownloading...")
    saved = []
    for i, img_url in enumerate(images_to_download, 1):
        parsed = urlparse(img_url)
        original_ext = os.path.splitext(parsed.path)[1].lower() or ".jpg"
        if original_ext not in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
            original_ext = ".jpg"

        temp_name = f"{args.filename_prefix}-{i:02d}{original_ext}"
        temp_path = output_dir / temp_name

        try:
            download_image(img_url, str(temp_path))

            if not args.no_png_convert and original_ext != ".png" and PILLOW_AVAILABLE:
                png_name = f"{args.filename_prefix}-{i:02d}.png"
                png_path = output_dir / png_name
                if convert_to_png(str(temp_path), str(png_path)):
                    temp_path.unlink()
                    saved.append(png_name)
                    print(f"  ✓ [{i}] {png_name} (converted from {original_ext[1:]})")
                else:
                    saved.append(temp_name)
                    print(f"  ✓ [{i}] {temp_name}")
            else:
                saved.append(temp_name)
                print(f"  ✓ [{i}] {temp_name}")
        except Exception as e:
            print(f"  ✗ [{i}] Failed: {e}")

    print(f"\n{'='*60}")
    print(f"  Done — {len(saved)}/{len(images_to_download)} images saved")
    print(f"  Folder: {output_dir}")
    print(f"{'='*60}\n")

    if saved:
        print("Next: použi tieto images ako reference v generate_ads.py:")
        print(f"  --images-dir \"{output_dir}\"")


if __name__ == "__main__":
    main()
