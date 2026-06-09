#!/usr/bin/env python3
"""
Scraper for Mazaya.eg and Faces.eg fragrance products.
Extracts all fragrances with name, brand, price, images, and details.

Usage:
    python scrape_fragrances.py --site mazaya --output mazaya_fragrances.json
    python scrape_fragrances.py --site faces --output faces_fragrances.json
    python scrape_fragrances.py --site all --output all_fragrances.json
"""

import argparse
import json
import time
import os
import sys
import requests
from urllib.parse import urljoin

# ─── MAZAYA SCRAPER ──────────────────────────────────────────────────────────

MAZAYA_GRAPHQL = "https://mazaya.eg/graphql"
MAZAYA_BASE = "https://mazaya.eg/en"

PRODUCT_QUERY = """
query Products($page: Int, $pageSize: Int, $filter: ProductAttributeFilterInput, $sort: ProductAttributeSortInput, $search: String) {
  connection: products(currentPage: $page, pageSize: $pageSize, filter: $filter, sort: $sort, search: $search) {
    page_info {
      total_pages
      current_page
      page_size
    }
    total_count
    nodes: items {
      __typename
      id
      name
      rating_summary
      sku
      url_key
      is_best_seller
      new_from_date
      new_to_date
      stock_status
      attributes {
        key
        value
      }
      brand {
        url_key
        name
      }
      thumbnail {
        url
        label
      }
      media_gallery {
        label
        url
        disabled
      }
      price_range {
        maximum_price {
          final_price {
            value
          }
          regular_price {
            value
          }
        }
        minimum_price {
          final_price {
            value
          }
          regular_price {
            value
          }
        }
      }
      potential_gift_promotions {
        gifts {
          items {
            only_x_left_in_stock
          }
        }
      }
      ...on ConfigurableProduct {
        configurable_options {
          attribute_code
          values {
            swatch_data {
              value
            }
            uid
          }
        }
      }
    }
  }
}
"""


def scrape_mazaya(max_pages=None):
    """Scrape all perfume products from Mazaya.eg via GraphQL."""
    products = []
    page = 1
    total_pages = None

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://mazaya.eg",
        "Referer": "https://mazaya.eg/en/fragrances",
    })

    while True:
        if max_pages and page > max_pages:
            break

        variables = {
            "page": page,
            "pageSize": 50,
            "sort": {"position": "ASC"},
            "filter": {"category_uid": {"eq": "NA=="}},
            "search": "",
        }

        payload = {"query": PRODUCT_QUERY, "variables": variables}

        try:
            resp = session.post(MAZAYA_GRAPHQL, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  [Mazaya] Error on page {page}: {e}", file=sys.stderr)
            break

        if "errors" in data:
            print(f"  [Mazaya] GraphQL errors: {data['errors']}", file=sys.stderr)
            break

        connection = data.get("data", {}).get("connection", {})
        if not connection:
            break

        if total_pages is None:
            page_info = connection.get("page_info", {})
            total_pages = page_info.get("total_pages", 1)
            total_count = connection.get("total_count", 0)
            print(f"  [Mazaya] Found {total_count} products across {total_pages} pages")

        items = connection.get("nodes", [])
        if not items:
            break

        for item in items:
            product = {
                "id": item.get("id"),
                "name": item.get("name"),
                "brand": item.get("brand", {}).get("name") if item.get("brand") else None,
                "sku": item.get("sku"),
                "url": f"{MAZAYA_BASE}/{item.get('url_key', '')}",
                "price_min": item.get("price_range", {}).get("minimum_price", {}).get("final_price", {}).get("value"),
                "price_max": item.get("price_range", {}).get("maximum_price", {}).get("final_price", {}).get("value"),
                "regular_price_min": item.get("price_range", {}).get("minimum_price", {}).get("regular_price", {}).get("value"),
                "regular_price_max": item.get("price_range", {}).get("maximum_price", {}).get("regular_price", {}).get("value"),
                "currency": "EGP",
                "thumbnail": item.get("thumbnail", {}).get("url") if item.get("thumbnail") else None,
                "images": [m["url"] for m in item.get("media_gallery", []) if not m.get("disabled")],
                "rating_summary": item.get("rating_summary"),
                "stock_status": item.get("stock_status"),
                "is_best_seller": item.get("is_best_seller", False),
                "is_new": bool(item.get("new_from_date")),
                "has_gift": bool(item.get("potential_gift_promotions")),
                "attributes": {a["key"]: a["value"] for a in item.get("attributes", [])},
                "variants": [],
            }

            # Extract size variants from configurable options
            for opt in item.get("configurable_options", []):
                if opt.get("attribute_code") == "size":
                    product["variants"] = [
                        {"uid": v.get("uid"), "label": v.get("swatch_data", {}).get("value")}
                        for v in opt.get("values", [])
                    ]

            products.append(product)

        print(f"  [Mazaya] Page {page}/{total_pages}: {len(items)} products (total: {len(products)})")

        if page >= total_pages:
            break

        page += 1
        time.sleep(0.5)  # Be polite

    return products


# ─── FACES SCRAPER ───────────────────────────────────────────────────────────

FACES_BASE = "https://www.faces.eg"
FACES_SEARCH_HTML_URL = f"{FACES_BASE}/on/demandware.store/Sites-Faces_EG-Site/en_EG/Search-UpdateGrid"


def scrape_faces(max_pages=None):
    """Scrape all perfume products from Faces.eg via HTML parsing of their Demandware search results."""
    products = []
    seen_urls = set()

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("  [Faces] BeautifulSoup not installed. Install with: pip install beautifulsoup4")
        print("  [Faces] Falling back to regex-based parsing...")
        return scrape_faces_regex(max_pages)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    })

    # First visit the main perfume page to get session cookies
    try:
        session.get(f"{FACES_BASE}/en/perfume", timeout=30)
    except Exception as e:
        print(f"  [Faces] Warning: Could not get session cookies: {e}", file=sys.stderr)

    # Now update headers for AJAX requests
    session.headers.update({
        "Accept": "text/html,application/xhtml+xml",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"{FACES_BASE}/en/perfume",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    })

    start = 0
    page_size = 24  # Faces loads 24 per page in the HTML response
    page = 1
    total = None

    while True:
        if max_pages and page > max_pages:
            break

        params = {
            "cgid": "perfume",
            "start": start,
            "sz": page_size,
            "format": "ajax",
            "requesttype": "ajax",
        }

        try:
            resp = session.get(FACES_SEARCH_HTML_URL, params=params, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            print(f"  [Faces] Error on page {page}: {e}", file=sys.stderr)
            break

        soup = BeautifulSoup(resp.text, "html.parser")

        # Find total count
        if total is None:
            count_el = soup.select_one(".results-hits, [class*='results-count'], [class*='total-count']")
            if count_el:
                import re
                nums = re.findall(r'\d+', count_el.get_text())
                if nums:
                    total = int(nums[0])
            if total is None:
                # Try to find it in the page text
                import re
                match = re.search(r'(\d+)\s*items?', resp.text)
                if match:
                    total = int(match.group(1))
            if total:
                print(f"  [Faces] Found {total} products")

        # Parse product tiles
        tiles = soup.select(".product-tile, .js-product-tile, [class*='product-tile']")
        if not tiles:
            # Try broader selectors
            tiles = soup.select("[data-pid], [data-product-id]")

        if not tiles:
            print(f"  [Faces] No product tiles found on page {page}")
            break

        new_count = 0
        for tile in tiles:
            # Extract product URL
            link_el = tile.select_one("a[href*='/p/'], a[href*='product']")
            if not link_el:
                continue
            href = link_el.get("href", "")
            if href.startswith("/"):
                href = f"{FACES_BASE}{href}"
            if not href.startswith("http"):
                href = f"{FACES_BASE}/{href}"
            if href in seen_urls:
                continue
            seen_urls.add(href)

            # Extract product ID
            pid = tile.get("data-pid") or tile.get("data-product-id")
            if not pid:
                import re
                m = re.search(r'/p/([^/?#]+)', href)
                if m:
                    pid = m.group(1)

            # Extract name
            name_el = tile.select_one(
                ".product-name, [class*='product-name'], .product-tile-name, "
                "[class*='tile-name'], .name, h2, h3"
            )
            name = name_el.get_text(strip=True) if name_el else None

            # Extract brand
            brand_el = tile.select_one(
                ".product-brand, [class*='product-brand'], .brand, [class*='brand-name']"
            )
            brand = brand_el.get_text(strip=True) if brand_el else None

            # If no brand element, try to extract from name (Faces format: "BRAND Product Name")
            if not brand and name:
                parts = name.split(None, 1)
                if len(parts) == 2 and parts[0].isupper():
                    brand = parts[0]
                    name = parts[1]

            # Extract price
            price_el = tile.select_one(
                ".price, [class*='price'], .product-price, [class*='product-price'], "
                ".sale-price, [class*='sale-price']"
            )
            price_text = price_el.get_text(strip=True) if price_el else None
            price = _parse_price(price_text)
            price_original = _parse_original_price(tile)

            # Extract images
            images = []
            for img in tile.select("img"):
                src = img.get("src") or img.get("data-src") or img.get("data-lazy")
                if src:
                    if src.startswith("//"):
                        src = f"https:{src}"
                    if src not in images:
                        images.append(src)

            # Extract gender/category
            gender_el = tile.select_one("[class*='gender'], [class*='category'], .product-category")
            gender = gender_el.get_text(strip=True) if gender_el else None

            # Extract badges
            badges = []
            for badge in tile.select(".badge, [class*='badge'], .tag, [class*='tag'], .promo, [class*='promo']"):
                badge_text = badge.get_text(strip=True)
                if badge_text:
                    badges.append(badge_text)

            # Extract rating
            rating_el = tile.select_one("[class*='rating'], .star-rating, [class*='star']")
            rating = None
            if rating_el:
                rating_text = rating_el.get("data-rating") or rating_el.get("title") or rating_el.get_text(strip=True)
                rating = _parse_price(rating_text)

            product = {
                "id": pid,
                "name": name,
                "brand": brand,
                "url": href,
                "price": price,
                "price_original": price_original,
                "currency": "EGP",
                "images": images,
                "thumbnail": images[0] if images else None,
                "gender": gender,
                "badges": badges,
                "rating": rating,
            }
            products.append(product)
            new_count += 1

        print(f"  [Faces] Page {page}: {new_count} new products (total: {len(products)})")

        if new_count == 0:
            break

        start += page_size
        if total and start >= total:
            break

        page += 1
        time.sleep(0.5)

    return products


def scrape_faces_regex(max_pages=None):
    """Fallback Faces scraper using regex (no BeautifulSoup dependency)."""
    import re
    products = []
    seen_urls = set()

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })
    # Get session cookies first
    try:
        session.get(f"{FACES_BASE}/en/perfume", timeout=30)
    except Exception:
        pass
    session.headers.update({
        "Accept": "text/html",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"{FACES_BASE}/en/perfume",
    })

    start = 0
    page_size = 24
    page = 1
    total = None

    while True:
        if max_pages and page > max_pages:
            break

        params = {"cgid": "perfume", "start": start, "sz": page_size, "format": "ajax", "requesttype": "ajax"}
        try:
            resp = session.get(FACES_SEARCH_HTML_URL, params=params, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            print(f"  [Faces] Error on page {page}: {e}", file=sys.stderr)
            break

        html = resp.text

        if total is None:
            m = re.search(r'(\d+)\s*items?', html)
            if m:
                total = int(m.group(1))
                print(f"  [Faces] Found {total} products")

        # Extract product tiles
        tile_pattern = re.compile(r'<div[^>]*class="[^"]*product-tile[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>', re.DOTALL)
        tiles = tile_pattern.findall(html)

        if not tiles:
            # Try simpler pattern
            tile_pattern = re.compile(r'<div[^>]*class="[^"]*product-tile[^"]*"[^>]*data-pid="([^"]+)"[^>]*>', re.DOTALL)
            pids = tile_pattern.findall(html)
            if not pids:
                break

        new_count = 0
        for tile_html in tiles:
            # Extract URL
            url_m = re.search(r'href="(/en/p/[^"]+)"', tile_html)
            if not url_m:
                continue
            href = f"{FACES_BASE}{url_m.group(1)}"
            if href in seen_urls:
                continue
            seen_urls.add(href)

            # Extract name
            name_m = re.search(r'class="[^"]*product-name[^"]*"[^>]*>(.*?)</', tile_html, re.DOTALL)
            name = re.sub(r'<[^>]+>', '', name_m.group(1)).strip() if name_m else None

            # Extract price
            price_m = re.search(r'class="[^"]*price[^"]*"[^>]*>[^<]*?(\d[\d,]+)', tile_html)
            price = float(price_m.group(1).replace(',', '')) if price_m else None

            # Extract image
            img_m = re.search(r'(?:src|data-src)="(https?://[^"]+faces\.eg[^"]+)"', tile_html)
            img = img_m.group(1) if img_m else None

            products.append({
                "url": href,
                "name": name,
                "price": price,
                "currency": "EGP",
                "images": [img] if img else [],
                "thumbnail": img,
            })
            new_count += 1

        print(f"  [Faces] Page {page}: {new_count} new products (total: {len(products)})")

        if new_count == 0:
            break

        start += page_size
        if total and start >= total:
            break
        page += 1
        time.sleep(0.5)

    return products


def _parse_price(text):
    """Parse price from text like '⁦7900⁩ EGP' or 'EGP 7,900'."""
    if not text:
        return None
    import re
    # Remove invisible Unicode characters
    cleaned = re.sub(r'[\u202a-\u202f\u200b-\u200f\ufeff]', '', text)
    nums = re.findall(r'[\d,]+\.?\d*', cleaned)
    if nums:
        return float(nums[0].replace(',', ''))
    return None


def _parse_original_price(tile):
    """Parse original/list price from product tile."""
    import re
    from bs4 import BeautifulSoup
    # Look for list price / was price
    list_el = tile.select_one(".list-price, [class*='list-price'], .was-price, [class*='was-price'], .original-price")
    if list_el:
        return _parse_price(list_el.get_text(strip=True))
    return None


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Scrape fragrance data from Mazaya.eg and Faces.eg")
    parser.add_argument("--site", choices=["mazaya", "faces", "all"], default="all", help="Which site to scrape")
    parser.add_argument("--output", default="fragrances.json", help="Output JSON file path")
    parser.add_argument("--max-pages", type=int, default=None, help="Max pages to scrape (for testing)")
    parser.add_argument("--download-images", action="store_true", help="Download product images locally")
    parser.add_argument("--images-dir", default="product_images", help="Directory for downloaded images")
    args = parser.parse_args()

    all_data = {}

    if args.site in ("mazaya", "all"):
        print("\n=== Scraping Mazaya.eg ===")
        mazaya_products = scrape_mazaya(max_pages=args.max_pages)
        all_data["mazaya"] = {
            "source": "https://mazaya.eg",
            "total": len(mazaya_products),
            "products": mazaya_products,
        }
        print(f"  Total Mazaya products: {len(mazaya_products)}")

    if args.site in ("faces", "all"):
        print("\n=== Scraping Faces.eg ===")
        faces_products = scrape_faces(max_pages=args.max_pages)
        all_data["faces"] = {
            "source": "https://www.faces.eg",
            "total": len(faces_products),
            "products": faces_products,
        }
        print(f"  Total Faces products: {len(faces_products)}")

    # Save to JSON
    output_path = args.output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {output_path}")

    # Optionally download images
    if args.download_images:
        print("\n=== Downloading Images ===")
        os.makedirs(args.images_dir, exist_ok=True)

        for site_name, site_data in all_data.items():
            site_dir = os.path.join(args.images_dir, site_name)
            os.makedirs(site_dir, exist_ok=True)

            session = requests.Session()
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            })

            for i, product in enumerate(site_data["products"]):
                product_dir = os.path.join(site_dir, str(product.get("id", i)))
                os.makedirs(product_dir, exist_ok=True)

                images = product.get("images", [])
                if not images and product.get("thumbnail"):
                    images = [product["thumbnail"]]

                for j, img_url in enumerate(images):
                    if not img_url:
                        continue
                    ext = "jpg"
                    if ".png" in img_url.lower():
                        ext = "png"
                    elif ".webp" in img_url.lower():
                        ext = "webp"
                    img_path = os.path.join(product_dir, f"image_{j}.{ext}")

                    if os.path.exists(img_path):
                        continue

                    try:
                        r = session.get(img_url, timeout=15)
                        if r.status_code == 200:
                            with open(img_path, "wb") as imgf:
                                imgf.write(r.content)
                    except Exception as e:
                        print(f"  Failed to download {img_url}: {e}")

                if (i + 1) % 50 == 0:
                    print(f"  Downloaded images for {i+1}/{len(site_data['products'])} products")

        print(f"  Images saved to {args.images_dir}/")

    # Print summary
    print("\n=== Summary ===")
    for site_name, site_data in all_data.items():
        print(f"\n{site_name.upper()}:")
        print(f"  Products: {site_data['total']}")
        if site_data["products"]:
            sample = site_data["products"][0]
            print(f"  Sample: {sample.get('name', 'N/A')} by {sample.get('brand', 'N/A')}")
            print(f"  Price: {sample.get('price_min') or sample.get('price', 'N/A')} EGP")
            print(f"  Images: {len(sample.get('images', []))}")


if __name__ == "__main__":
    main()
