from __future__ import annotations
import asyncio
from kinopoisk.data.id import *
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime



@dataclass(frozen=True)
class Review:
    id : Id = None
    is_positive : bool = None
    is_negative : bool = None
    date : datetime = None
    author : str = None
    title : str = None
    text : str = None
    user_positive_reviews_count : int = None
    user_negative_reviews_count : int = None


    @staticmethod
    async def _create_from_json(json : dict)-> TVSeries:
        review = Review(
            id=Id(
                json.get('reviewId'),
                None
            ),
            is_positive=True if json.get('reviewType') == 'POSITIVE' else False,
            is_negative=True if json.get('reviewType') == 'NEGATIVE' else False,
            date=datetime.strptime(json.get('reviewData'), '%Y-%m-%dT%H:%M:%S') if json.get('reviewData') is not None else None,
            author=json.get('reviewAutor'),
            title=json.get('reviewTitle'),
            text=json.get('reviewDescription'),
            user_positive_reviews_count=json.get('userPositiveRating'),
            user_negative_reviews_count=json.get('userNegativeRating')
        )
        return review
