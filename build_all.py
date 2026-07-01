"""
build_all.py - Arcade Cabinet Build Automation Script
=======================================================
Copies arcade_api.py into each game folder, compiles each game via pygbag,
and rewrites CDN URLs in the built index.html files.

Usage:
    uv run python build_all.py --local     # Local CDN (http://127.0.0.1:8000/cdn/...)
    uv run python build_all.py --prod      # Production CDN (https://pygame-web.github.io/cdn/...)
    uv run python build_all.py --package   # Also assembles dist/ folder

Requirements:
    pip install pygbag
"""

import os
import sys
import shutil
import subprocess
import argparse

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))

CDN_PROD = "https://pygame-web.github.io/cdn/0.9.3/"
CDN_LOCAL = "http://127.0.0.1:8000/cdn/0.9.3/"

GAMES = [
    "Tetris",
    "Space_Dodge",
    "pong",
    "snake",
    "Car_Racing",
    "Space_invader",
    "Galaxy_Fight",
    "2048",
    "Platformer",
    "checkers",
    "Asteroids",
    "Pacman",
    "Flappy",
    "Lander",
    "Minesweeper",
    "Breakout",
    "Mario",
    "Level_Devil",
]

ARCADE_API_SRC = os.path.join(ROOT, "arcade_api.py")


def copy_arcade_api(game_dir):
    dst = os.path.join(game_dir, "arcade_api.py")
    shutil.copy2(ARCADE_API_SRC, dst)
    print(f"  [API] Copied arcade_api.py -> {dst}")


def build_game(game_name, cdn_url):
    game_dir = os.path.join(ROOT, game_name)
    main_py = os.path.join(game_dir, "main.py")

    if not os.path.exists(main_py):
        print(f"  [SKIP] {game_name}: main.py not found.")
        return False

    copy_arcade_api(game_dir)

    print(f"  [BUILD] Compiling {game_name}...")
    result = subprocess.run(
        [sys.executable, "-m", "pygbag", "--build", game_dir],
        capture_output=False,
    )

    if result.returncode != 0:
        print(f"  [ERROR] pygbag failed for {game_name} (exit code {result.returncode})")
        return False

    # Patch CDN URLs in the built index.html
    built_index = os.path.join(game_dir, "build", "web", "index.html")
    if os.path.exists(built_index):
        patch_cdn(built_index, cdn_url)
        print(f"  [CDN]   Patched CDN -> {cdn_url} in {built_index}")
    else:
        print(f"  [WARN]  Built index.html not found at {built_index}")

    return True


def patch_cdn(html_path, new_cdn):
    """Replace any existing CDN URL (local or production) with the target."""
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    content = content.replace(CDN_PROD, new_cdn)
    content = content.replace(CDN_LOCAL, new_cdn)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)


def package_dist():
    """Assemble a dist/ folder with index.html, cdn/, and all built games."""
    dist_dir = os.path.join(ROOT, "dist")
    print(f"\n[PACKAGE] Assembling dist/ at {dist_dir}")

    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)

    # Copy root index.html
    shutil.copy2(os.path.join(ROOT, "index.html"), os.path.join(dist_dir, "index.html"))
    print("  [COPY] index.html")

    # Copy assets/ folder if it exists (3D React App assets)
    assets_src = os.path.join(ROOT, "assets")
    if os.path.exists(assets_src):
        shutil.copytree(assets_src, os.path.join(dist_dir, "assets"))
        print("  [COPY] assets/")

    # Copy local CDN assets
    cdn_src = os.path.join(ROOT, "cdn")
    if os.path.exists(cdn_src):
        shutil.copytree(cdn_src, os.path.join(dist_dir, "cdn"))
        print("  [COPY] cdn/")

    # Copy each game's build/web directory
    for game in GAMES:
        web_src = os.path.join(ROOT, game, "build", "web")
        web_dst = os.path.join(dist_dir, game, "build", "web")
        if os.path.exists(web_src):
            shutil.copytree(web_src, web_dst)
            print(f"  [COPY] {game}/build/web/")
        else:
            print(f"  [MISS] {game}/build/web/ not found — skipping")

    print(f"\n[PACKAGE] Done! dist/ folder ready at: {dist_dir}")


def main():
    parser = argparse.ArgumentParser(description="Arcade Cabinet Build Script")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--local", action="store_true", help="Use local CDN (127.0.0.1:8000)")
    mode.add_argument("--prod", action="store_true", help="Use production CDN (pygame-web.github.io)")
    parser.add_argument("--package", action="store_true", help="Package all builds into dist/ folder")
    parser.add_argument("--games", nargs="+", metavar="GAME", help="Only build specified games (e.g. Tetris Flappy)")
    args = parser.parse_args()

    cdn_url = CDN_LOCAL if args.local else CDN_PROD
    mode_name = "LOCAL" if args.local else "PRODUCTION"
    print(f"\n{'='*60}")
    print(f" Arcade Cabinet Build — {mode_name} CDN")
    print(f" CDN: {cdn_url}")
    print(f"{'='*60}\n")

    games_to_build = args.games if args.games else GAMES

    success = 0
    failed = []

    for game in games_to_build:
        print(f"\n[{game}]")
        ok = build_game(game, cdn_url)
        if ok:
            success += 1
        else:
            failed.append(game)

    print(f"\n{'='*60}")
    print(f" Build Complete: {success}/{len(games_to_build)} games compiled.")
    if failed:
        print(f" Failed: {', '.join(failed)}")
    print(f"{'='*60}\n")

    if args.package:
        package_dist()


if __name__ == "__main__":
    main()
