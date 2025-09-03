"""
Hexagonal Coordinate System for Catan
=====================================

Handles axial coordinate math, neighbor calculations, and axial <-> pixel transformations.
"""

import math
from typing import Tuple, List, Set
from dataclasses import dataclass


@dataclass(frozen=True)
class HexCoord:
    """Axial coordinates for a hexagon (q, r)."""
    q: int
    r: int
    
    @property
    def s(self) -> int:
        """Third coordinate s = -q - r (for cube coordinates)."""
        return -self.q - self.r
    
    def __add__(self, other: 'HexCoord') -> 'HexCoord':
        return HexCoord(self.q + other.q, self.r + other.r)
    
    def __sub__(self, other: 'HexCoord') -> 'HexCoord':
        return HexCoord(self.q - other.q, self.r - other.r)
    
    def __mul__(self, scalar: int) -> 'HexCoord':
        return HexCoord(self.q * scalar, self.r * scalar)


# Direction vectors for hexagon neighbors (flat-top orientation)
HEX_DIRECTIONS = [
    HexCoord(1, 0),   # Right
    HexCoord(1, -1),  # Top-right
    HexCoord(0, -1),  # Top-left
    HexCoord(-1, 0),  # Left
    HexCoord(-1, 1),  # Bottom-left
    HexCoord(0, 1),   # Bottom-right
]


def generate_radius_2_board() -> Set[HexCoord]:
    """
    Generate all hex coordinates for a radius-2 board (19 hexes).
    
    Returns:
        Set of HexCoord representing the 19-hex Catan board
    """
    hexes = set()
    
    for q in range(-2, 3):  # q from -2 to 2
        for r in range(-2, 3):  # r from -2 to 2
            if abs(q + r) <= 2:  # |q + r| <= 2 constraint
                hexes.add(HexCoord(q, r))
    
    return hexes


def hex_neighbors(hex_coord: HexCoord) -> List[HexCoord]:
    """Get all 6 neighbors of a hex coordinate."""
    return [hex_coord + direction for direction in HEX_DIRECTIONS]


def hex_distance(a: HexCoord, b: HexCoord) -> int:
    """Calculate distance between two hex coordinates."""
    return (abs(a.q - b.q) + abs(a.q + a.r - b.q - b.r) + abs(a.r - b.r)) // 2


def axial_to_pixel(hex_coord: HexCoord, size: float = 1.0) -> Tuple[float, float]:
    """
    Convert axial coordinates to pixel coordinates (flat-top orientation).
    
    Args:
        hex_coord: Axial coordinates
        size: Hex size (radius from center to vertex)
    
    Returns:
        (x, y) pixel coordinates
    """
    x = size * (3.0/2.0 * hex_coord.q)
    y = size * (math.sqrt(3.0)/2.0 * hex_coord.q + math.sqrt(3.0) * hex_coord.r)
    return (x, y)


def pixel_to_axial(x: float, y: float, size: float = 1.0) -> HexCoord:
    """
    Convert pixel coordinates to axial coordinates (flat-top orientation).
    
    Args:
        x, y: Pixel coordinates
        size: Hex size (radius from center to vertex)
    
    Returns:
        HexCoord (rounded to nearest hex)
    """
    q = (2.0/3.0 * x) / size
    r = (-1.0/3.0 * x + math.sqrt(3.0)/3.0 * y) / size
    
    return axial_round(q, r)


def axial_round(q: float, r: float) -> HexCoord:
    """Round fractional axial coordinates to the nearest hex."""
    s = -q - r
    
    rq = round(q)
    rr = round(r)
    rs = round(s)
    
    q_diff = abs(rq - q)
    r_diff = abs(rr - r)
    s_diff = abs(rs - s)
    
    if q_diff > r_diff and q_diff > s_diff:
        rq = -rr - rs
    elif r_diff > s_diff:
        rr = -rq - rs
    
    return HexCoord(rq, rr)


def hex_corners(hex_coord: HexCoord, size: float = 1.0) -> List[Tuple[float, float]]:
    """
    Get the 6 corner positions of a hexagon in pixel coordinates.
    
    Args:
        hex_coord: Axial coordinates of the hex
        size: Hex size (radius from center to vertex)
    
    Returns:
        List of (x, y) corner positions, starting from rightmost and going clockwise
    """
    center_x, center_y = axial_to_pixel(hex_coord, size)
    corners = []
    
    for i in range(6):
        angle_deg = 60 * i  # Starting from 0° (rightmost point), going clockwise
        angle_rad = math.radians(angle_deg)
        corner_x = center_x + size * math.cos(angle_rad)
        corner_y = center_y + size * math.sin(angle_rad)
        corners.append((corner_x, corner_y))
    
    return corners


def get_hex_at_pixel(x: float, y: float, board_hexes: Set[HexCoord], size: float = 1.0) -> HexCoord:
    """
    Get the hex coordinate at a given pixel position.
    
    Args:
        x, y: Pixel coordinates
        board_hexes: Set of valid hex coordinates on the board
        size: Hex size
    
    Returns:
        HexCoord if position is on a valid hex, None otherwise
    """
    hex_coord = pixel_to_axial(x, y, size)
    return hex_coord if hex_coord in board_hexes else None
