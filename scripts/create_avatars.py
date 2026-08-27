"""
Create animated avatar GIFs for the debate agents
Blue agent (Tech Optimist) and Red agent (Tech Skeptic)

Requires optional deps: `uv sync --extra avatars`
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path


def _require_imaging():
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise SystemExit(
            "Pillow required. Install with: uv sync --extra avatars"
        ) from exc
    return Image, ImageDraw


def create_pulsing_avatar(color_name, base_color, output_file):
    """Create a pulsing animated avatar GIF"""
    Image, ImageDraw = _require_imaging()
    frames = []
    size = (100, 100)
    center = (50, 50)

    for i in range(20):
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        pulse = math.sin(i * math.pi / 10) * 5 + 35
        glow_radius = pulse + 10

        for r in range(int(glow_radius), int(pulse), -1):
            alpha = int(255 * (1 - (r - pulse) / (glow_radius - pulse)) * 0.3)
            glow_color = (*base_color, alpha)
            draw.ellipse(
                [center[0] - r, center[1] - r, center[0] + r, center[1] + r],
                fill=glow_color,
            )

        draw.ellipse(
            [center[0] - pulse, center[1] - pulse, center[0] + pulse, center[1] + pulse],
            fill=(*base_color, 255),
        )

        inner_radius = pulse * 0.8
        lighter_color = tuple(min(255, c + 50) for c in base_color)
        draw.ellipse(
            [
                center[0] - inner_radius,
                center[1] - inner_radius,
                center[0] + inner_radius,
                center[1] + inner_radius,
            ],
            fill=(*lighter_color, 200),
        )

        if i % 10 < 5:
            eye_y = center[1] - 5
            draw.ellipse(
                [center[0] - 15, eye_y - 3, center[0] - 9, eye_y + 3],
                fill=(255, 255, 255, 255),
            )
            draw.ellipse(
                [center[0] + 9, eye_y - 3, center[0] + 15, eye_y + 3],
                fill=(255, 255, 255, 255),
            )
            draw.ellipse(
                [center[0] - 13, eye_y - 1, center[0] - 11, eye_y + 1],
                fill=(0, 0, 0, 255),
            )
            draw.ellipse(
                [center[0] + 11, eye_y - 1, center[0] + 13, eye_y + 1],
                fill=(0, 0, 0, 255),
            )
        else:
            eye_y = center[1] - 5
            draw.line(
                [center[0] - 15, eye_y, center[0] - 9, eye_y],
                fill=(255, 255, 255, 255),
                width=2,
            )
            draw.line(
                [center[0] + 9, eye_y, center[0] + 15, eye_y],
                fill=(255, 255, 255, 255),
                width=2,
            )

        mouth_y = center[1] + 8
        if i % 4 == 0:
            draw.arc(
                [center[0] - 10, mouth_y - 5, center[0] + 10, mouth_y + 5],
                start=0,
                end=180,
                fill=(255, 255, 255, 255),
                width=2,
            )
        elif i % 4 == 1:
            draw.ellipse(
                [center[0] - 8, mouth_y - 3, center[0] + 8, mouth_y + 3],
                fill=(255, 255, 255, 255),
            )
        elif i % 4 == 2:
            draw.arc(
                [center[0] - 12, mouth_y - 5, center[0] + 12, mouth_y + 5],
                start=0,
                end=180,
                fill=(255, 255, 255, 255),
                width=3,
            )
        else:
            draw.line(
                [center[0] - 8, mouth_y, center[0] + 8, mouth_y],
                fill=(255, 255, 255, 255),
                width=2,
            )

        frames.append(img)

    frames[0].save(
        output_file,
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0,
        transparency=0,
    )
    print(f"Created {output_file}")


def create_static_avatar(color_name, base_color, output_file):
    """Create a static avatar as fallback"""
    Image, ImageDraw = _require_imaging()
    size = (100, 100)
    center = (50, 50)

    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for r in range(45, 35, -1):
        alpha = int(255 * (1 - (r - 35) / 10) * 0.3)
        glow_color = (*base_color, alpha)
        draw.ellipse(
            [center[0] - r, center[1] - r, center[0] + r, center[1] + r],
            fill=glow_color,
        )

    draw.ellipse(
        [center[0] - 35, center[1] - 35, center[0] + 35, center[1] + 35],
        fill=(*base_color, 255),
    )

    lighter_color = tuple(min(255, c + 50) for c in base_color)
    draw.ellipse(
        [center[0] - 28, center[1] - 28, center[0] + 28, center[1] + 28],
        fill=(*lighter_color, 200),
    )

    eye_y = center[1] - 5
    draw.ellipse(
        [center[0] - 15, eye_y - 3, center[0] - 9, eye_y + 3],
        fill=(255, 255, 255, 255),
    )
    draw.ellipse(
        [center[0] + 9, eye_y - 3, center[0] + 15, eye_y + 3],
        fill=(255, 255, 255, 255),
    )
    draw.ellipse(
        [center[0] - 13, eye_y - 1, center[0] - 11, eye_y + 1],
        fill=(0, 0, 0, 255),
    )
    draw.ellipse(
        [center[0] + 11, eye_y - 1, center[0] + 13, eye_y + 1],
        fill=(0, 0, 0, 255),
    )

    mouth_y = center[1] + 8
    draw.arc(
        [center[0] - 10, mouth_y - 5, center[0] + 10, mouth_y + 5],
        start=0,
        end=180,
        fill=(255, 255, 255, 255),
        width=2,
    )

    img.save(output_file)
    print(f"Created static {output_file}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("."),
        help="Directory for generated avatar files (default: cwd)",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    create_pulsing_avatar("blue", (0, 120, 255), str(out / "avatar_blue.gif"))
    create_static_avatar("blue", (0, 120, 255), str(out / "avatar_blue_static.png"))
    create_pulsing_avatar("red", (255, 50, 50), str(out / "avatar_red.gif"))
    create_static_avatar("red", (255, 50, 50), str(out / "avatar_red_static.png"))

    print("\nAvatars created successfully!")
    print(f"- {out / 'avatar_blue.gif'}: Animated blue avatar")
    print(f"- {out / 'avatar_red.gif'}: Animated red avatar")
    print(f"- {out / 'avatar_blue_static.png'}: Static blue avatar (fallback)")
    print(f"- {out / 'avatar_red_static.png'}: Static red avatar (fallback)")


if __name__ == "__main__":
    main()
