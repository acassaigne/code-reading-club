from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Callable


class KindOfDirection(Enum):
    CARDINAL = 0
    ORDINAL = 1


class Direction(Enum):
    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3
    NORTH_WEST = 4
    NORTH_EAST = 5
    SOUTH_WEST = 6
    SOUTH_EAST = 7

    def kind_of_direction(self) -> KindOfDirection:
        if self in (Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST):
            return KindOfDirection.CARDINAL
        if self in (Direction.NORTH_WEST, Direction.NORTH_EAST, Direction.SOUTH_WEST, Direction.SOUTH_EAST):
            return KindOfDirection.ORDINAL


@dataclass
class TupleCardinalDirections:
    first: Optional[Direction]
    second: Optional[Direction]


def first_component_of(ordinal_direction: Direction) -> Direction:
    if ordinal_direction in (Direction.NORTH_WEST, Direction.NORTH_EAST):
        return Direction.NORTH
    if ordinal_direction in (Direction.SOUTH_WEST, Direction.SOUTH_EAST):
        return Direction.SOUTH


def second_component_of(ordinal_direction: Direction) -> Direction:
    if ordinal_direction in (Direction.NORTH_WEST, Direction.SOUTH_WEST):
        return Direction.WEST
    if ordinal_direction in (Direction.NORTH_EAST, Direction.SOUTH_EAST):
        return Direction.EAST


@dataclass
class Interval:
    minimum: int
    maximum: int

    def include_this(self, value: int) -> bool:
        return self.minimum <= value <= self.maximum


class Position:

    def __init__(self, row: int, column: int):
        self._row = row
        self._column = column

    def __eq__(self, other) -> bool:
        return self._row == other._row and self._column == other._column

    def __hash__(self) -> int:
        return hash((self._row, self._column))

    def new_position_to(self, direction: Direction) -> Position:
        if direction.kind_of_direction() == KindOfDirection.CARDINAL:
            return self._new_cardinal_position_to(direction=direction)
        if direction.kind_of_direction() == KindOfDirection.ORDINAL:
            return self._new_ordinal_position_to(direction=direction)

    def _new_cardinal_position_to(self, direction: Direction) -> Position:
        if direction in (Direction.NORTH, Direction.SOUTH):
            return self._new_position_on_axe_north_south(direction=direction)
        if direction in (Direction.EAST, Direction.WEST):
            return self._new_position_on_axe_east_west(direction=direction)

    def _new_ordinal_position_to(self, direction: Direction) -> Position:
        tuple_cardinals = convert_ordinal_to_cardinal_directions(ordinal_direction=direction)
        return self.new_position_to(direction=tuple_cardinals.first) \
            .new_position_to(direction=tuple_cardinals.second)

    def _new_position_on_axe_north_south(self, direction: Direction) -> Position:
        shift_value = self._shift_value(direction)
        return Position(row=self._row + shift_value,
                        column=self._column)

    def _new_position_on_axe_east_west(self, direction: Direction) -> Position:
        shift_value = self._shift_value(direction)
        return Position(row=self._row,
                        column=self._column + shift_value)

    def _shift_value(self, direction: Direction) -> int:
        values = {Direction.NORTH: +1, Direction.SOUTH: -1,
                  Direction.EAST : +1, Direction.WEST: -1}
        return values.get(direction)

    def __repr__(self):
        return f"Position(row={self._row} column={self._column})"

    def generate_neighbors_positions(self) -> CollectionPositions:
        result = CollectionPositions()
        for compass_direction in Direction:
            result.register(self.new_position_to(direction=compass_direction))
        return result


    def if_column_between(self, minimum: int, maximum: int, a_callable: Callable) -> None:
        if minimum <= self._column <= maximum:
            a_callable()

    def if_column_inner(self, the_interval: Interval, then_call_me: Callable) -> None:
        if the_interval.include_this(value=self._column):
            then_call_me()
    def if_row_inner(self, the_interval: Interval, then_call_me: Callable) -> None:
        if the_interval.include_this(value=self._row):
            then_call_me()


class CollectionPositions:

    def __init__(self):
        self._collection: List[Position] = []

    def register(self, position: Position):
        self._collection.append(position)

    def __len__(self) -> int:
        return len(self._collection)

    def __iter__(self):
        return iter(self._collection)


def convert_ordinal_to_cardinal_directions(ordinal_direction: Direction) -> TupleCardinalDirections:
    return TupleCardinalDirections(first=first_component_of(ordinal_direction),
                                   second=second_component_of(ordinal_direction))
