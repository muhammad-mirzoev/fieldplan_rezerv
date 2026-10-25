# Приблизительные центры областей Кыргызстана (широта, долгота)
REGION_CENTERS = {
    "chui": (42.85, 74.60),
    "talas": (42.50, 72.30),
    "issyk_kul": (42.20, 77.60),
    "naryn": (41.40, 75.90),
    "osh": (40.50, 72.80),
    "jalal_abad": (41.00, 73.00),
    "batken": (39.90, 70.80),
}


def guess_region(lat, lon):
    """Ближайший центр области. Это приближение: у границ областей возможна ошибка."""
    return min(
        REGION_CENTERS,
        key=lambda r: (lat - REGION_CENTERS[r][0]) ** 2 + (lon - REGION_CENTERS[r][1]) ** 2,
    )