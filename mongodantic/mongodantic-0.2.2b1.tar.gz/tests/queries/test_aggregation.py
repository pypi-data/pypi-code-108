import pytest
from random import randint

from mongodantic.models import MongoModel
from mongodantic.types import ObjectIdStr
from mongodantic.logical import Query
from mongodantic import init_db_connection_params
from mongodantic.aggregation import Sum, Max, Min, Avg, Count
from mongodantic.exceptions import MongoValidationError

product_types = {1: 'phone', 2: 'book', 3: 'food'}

init_db_connection_params("mongodb://127.0.0.1:27017", "test")


class Product(MongoModel):
    title: str
    cost: float
    quantity: int
    product_type: str
    config: dict


class ProductImage(MongoModel):
    url: str
    product_id: ObjectIdStr


Product.Q.drop_collection(force=True)
ProductImage.Q.drop_collection(force=True)


@pytest.mark.asyncio
async def test_async_aggregation_math_operation():
    data = [
        Product(
            title=str(i),
            cost=float(i),
            quantity=i,
            product_type=product_types[randint(1, 3)],
            config={'type_id': i},
        )
        for i in range(1, 5)
    ]
    await Product.AQ.insert_many(data)
    max_ = await Product.AQ.simple_aggregate(aggregation=Max('cost'))
    assert max_ == {'cost__max': 4}

    min_ = await Product.AQ.simple_aggregate(aggregation=Min('cost'))
    assert min_ == {'cost__min': 1}

    sum_ = await Product.AQ.simple_aggregate(aggregation=Sum('cost'))
    assert sum_ == {'cost__sum': 10}

    avg_ = await Product.AQ.simple_aggregate(aggregation=Avg('cost'))
    assert avg_ == {'cost__avg': 2.5}

    simple_avg = await Product.AQ.aggregate_sum('cost')
    assert simple_avg == 10.0

    simple_max = await Product.AQ.aggregate_max('cost')
    assert simple_max == 4

    simple_min = await Product.AQ.aggregate_min('cost')
    assert simple_min == 1

    simple_avg = await Product.AQ.aggregate_avg('cost')
    assert simple_avg == 2.5


class TestAggregation:
    def setup(self):
        init_db_connection_params("mongodb://127.0.0.1:27017", "test")

        class Product(MongoModel):
            title: str
            cost: float
            quantity: int
            product_type: str
            config: dict

        class ProductImage(MongoModel):
            url: str
            product_id: ObjectIdStr

        Product.Q.drop_collection(force=True)
        ProductImage.Q.drop_collection(force=True)

        self.Product = Product
        self.ProductImage = ProductImage

    def test_aggregation_math_operation(self):
        data = [
            self.Product(
                title=str(i),
                cost=float(i),
                quantity=i,
                product_type=product_types[randint(1, 3)],
                config={'type_id': i},
            )
            for i in range(1, 5)
        ]
        self.Product.Q.insert_many(data)
        max_ = self.Product.Q.simple_aggregate(aggregation=Max('cost'))
        assert max_ == {'cost__max': 4}

        min_ = self.Product.Q.simple_aggregate(aggregation=Min('cost'))
        assert min_ == {'cost__min': 1}

        sum_ = self.Product.Q.simple_aggregate(aggregation=Sum('cost'))
        assert sum_ == {'cost__sum': 10}

        avg_ = self.Product.Q.simple_aggregate(aggregation=Avg('cost'))
        assert avg_ == {'cost__avg': 2.5}

        simple_avg = self.Product.Q.aggregate_sum('cost')
        assert simple_avg == 10.0

        simple_max = self.Product.Q.aggregate_max('cost')
        assert simple_max == 4

        simple_min = self.Product.Q.aggregate_min('cost')
        assert simple_min == 1

        simple_avg = self.Product.Q.aggregate_avg('cost')
        assert simple_avg == 2.5

    def test_aggregation_multiply(self):
        data = [
            self.Product(
                title=str(i),
                cost=float(i),
                quantity=i - 1,
                product_type=product_types[2] if i != 4 else product_types[1],
                config={'type_id': 2},
            )
            for i in range(1, 5)
        ]
        self.Product.Q.insert_many(data)
        result_sum = self.Product.Q.simple_aggregate(
            aggregation=[Sum('cost'), Sum('quantity')]
        )
        assert result_sum == {'cost__sum': 10.0, 'quantity__sum': 6}

        result_max = self.Product.Q.simple_aggregate(
            aggregation=[Max('cost'), Max('quantity')]
        )
        assert result_max == {'cost__max': 4.0, 'quantity__max': 3}

        result_min = self.Product.Q.simple_aggregate(
            aggregation=[Min('cost'), Min('quantity')]
        )
        assert result_min == {'cost__min': 1.0, 'quantity__min': 0}

        result_avg = self.Product.Q.simple_aggregate(
            aggregation=(Avg('cost'), Avg('quantity'))
        )
        assert result_avg == {'cost__avg': 2.5, 'quantity__avg': 1.5}

        result_multiply = self.Product.Q.simple_aggregate(
            aggregation=(Avg('cost'), Max('quantity'))
        )
        assert result_multiply == {'cost__avg': 2.5, 'quantity__max': 3}

        result_count = self.Product.Q.simple_aggregate(
            aggregation=Count('product_type')
        )
        assert result_count == {'book': {'count': 3}, 'phone': {'count': 1}}

        result_count_agg = self.Product.Q.simple_aggregate(
            aggregation=[Count('product_type'), Sum('cost')]
        )
        assert result_count_agg == {
            'book': {'cost__sum': 6.0, 'count': 3},
            'phone': {'cost__sum': 4.0, 'count': 1},
        }

        result_sum_and_avg_agg_with_group = self.Product.Q.simple_aggregate(
            aggregation=[Avg('cost'), Sum('cost')],
            group_by=['product_type'],
        )
        assert result_sum_and_avg_agg_with_group == {
            'phone': {'cost__avg': 4.0, 'cost__sum': 4.0},
            'book': {'cost__avg': 2.0, 'cost__sum': 6.0},
        }

        result_raw_group_by_by_inners = self.Product.Q.raw_aggregate(
            data=[
                {
                    "$group": {
                        "_id": {'type_id': "$config.type_id"},
                        'count': {f'$sum': 1},
                        'names': {'$push': '$title'},
                    }
                },
            ],
        )
        assert result_raw_group_by_by_inners == [
            {'_id': {'type_id': 2}, 'count': 4, 'names': ['1', '2', '3', '4']}
        ]

        result_group_by_by_inners = self.Product.Q.simple_aggregate(
            group_by=['config.type_id'], aggregation=Count('_id')
        )
        assert result_group_by_by_inners == {'2': {'count': 4}}

        result_sum_and_avg_agg_with_group_many = self.Product.Q.simple_aggregate(
            aggregation=[Avg('cost'), Sum('cost')],
            group_by=['product_type', 'quantity'],
        )
        assert result_sum_and_avg_agg_with_group_many == {
            'book|0': {'cost__avg': 1.0, 'cost__sum': 1.0},
            'book|1': {'cost__avg': 2.0, 'cost__sum': 2.0},
            'book|2': {'cost__avg': 3.0, 'cost__sum': 3.0},
            'phone|3': {'cost__avg': 4.0, 'cost__sum': 4.0},
        }

        result_agg = self.Product.Q.simple_aggregate(
            aggregation=[Avg('cost'), Max('quantity')]
        )
        assert result_agg == {'cost__avg': 2.5, 'quantity__max': 3}

        result_not_match_agg = self.Product.Q.simple_aggregate(
            Query(title__ne='not_match') & Query(title__startswith='not'),
            aggregation=[Avg('cost'), Max('quantity')],
        )
        assert result_not_match_agg == {}

    # @pytest.mark.asyncio
    # async def test_async_aggregation_multiply(self):
    #     data = [
    #         self.Product(
    #             title=str(i),
    #             cost=float(i),
    #             quantity=i - 1,
    #             product_type=product_types[2] if i != 4 else product_types[1],
    #             config={'type_id': 2},
    #         )
    #         for i in range(1, 5)
    #     ]
    #     await self.Product.AQ.insert_many(data)
    #     result_sum = await self.Product.AQ.simple_aggregate(
    #         aggregation=[Sum('cost'), Sum('quantity')]
    #     )
    #     assert result_sum == {'cost__sum': 10.0, 'quantity__sum': 6}

    #     result_max = await self.Product.AQ.simple_aggregate(
    #         aggregation=[Max('cost'), Max('quantity')]
    #     )
    #     assert result_max == {'cost__max': 4.0, 'quantity__max': 3}

    #     result_min = await self.Product.AQ.simple_aggregate(
    #         aggregation=[Min('cost'), Min('quantity')]
    #     )
    #     assert result_min == {'cost__min': 1.0, 'quantity__min': 0}

    #     result_avg = await self.Product.AQ.simple_aggregate(
    #         aggregation=(Avg('cost'), Avg('quantity'))
    #     )
    #     assert result_avg == {'cost__avg': 2.5, 'quantity__avg': 1.5}

    #     result_multiply = await self.Product.AQ.simple_aggregate(
    #         aggregation=(Avg('cost'), Max('quantity'))
    #     )
    #     assert result_multiply == {'cost__avg': 2.5, 'quantity__max': 3}

    #     result_count = await self.Product.AQ.simple_aggregate(
    #         aggregation=Count('product_type')
    #     )
    #     assert result_count == {'book': {'count': 3}, 'phone': {'count': 1}}

    #     result_count_agg = await self.Product.AQ.simple_aggregate(
    #         aggregation=[Count('product_type'), Sum('cost')]
    #     )
    #     assert result_count_agg == {
    #         'book': {'cost__sum': 6.0, 'count': 3},
    #         'phone': {'cost__sum': 4.0, 'count': 1},
    #     }

    #     result_sum_and_avg_agg_with_group = await self.Product.AQ.simple_aggregate(
    #         aggregation=[Avg('cost'), Sum('cost')],
    #         group_by=['product_type'],
    #     )
    #     assert result_sum_and_avg_agg_with_group == {
    #         'phone': {'cost__avg': 4.0, 'cost__sum': 4.0},
    #         'book': {'cost__avg': 2.0, 'cost__sum': 6.0},
    #     }

    #     result_raw_group_by_by_inners = await self.Product.AQ.raw_aggregate(
    #         data=[
    #             {
    #                 "$group": {
    #                     "_id": {'type_id': "$config.type_id"},
    #                     'count': {f'$sum': 1},
    #                     'names': {'$push': '$title'},
    #                 }
    #             },
    #         ],
    #     )
    #     assert result_raw_group_by_by_inners == [
    #         {'_id': {'type_id': 2}, 'count': 4, 'names': ['1', '2', '3', '4']}
    #     ]

    #     result_group_by_by_inners = await self.Product.AQ.simple_aggregate(
    #         group_by=['config.type_id'], aggregation=Count('_id')
    #     )
    #     assert result_group_by_by_inners == {'2': {'count': 4}}

    #     result_sum_and_avg_agg_with_group_many = await self.Product.AQ.simple_aggregate(
    #         aggregation=[Avg('cost'), Sum('cost')],
    #         group_by=['product_type', 'quantity'],
    #     )
    #     assert result_sum_and_avg_agg_with_group_many == {
    #         'book|0': {'cost__avg': 1.0, 'cost__sum': 1.0},
    #         'book|1': {'cost__avg': 2.0, 'cost__sum': 2.0},
    #         'book|2': {'cost__avg': 3.0, 'cost__sum': 3.0},
    #         'phone|3': {'cost__avg': 4.0, 'cost__sum': 4.0},
    #     }

    #     result_agg = await self.Product.AQ.simple_aggregate(
    #         aggregation=[Avg('cost'), Max('quantity')]
    #     )
    #     assert result_agg == {'cost__avg': 2.5, 'quantity__max': 3}

    #     result_not_match_agg = await self.Product.AQ.simple_aggregate(
    #         Query(title__ne='not_match') & Query(title__startswith='not'),
    #         aggregation=[Avg('cost'), Max('quantity')],
    #     )
    # assert result_not_match_agg == {}

    def test_raises_invalid_field(self):
        with pytest.raises(MongoValidationError):
            self.Product.Q.simple_aggregate(
                title='not_match', aggregation=[Avg('cost123'), Max('quantityzzzz')]
            )

    # @pytest.mark.asyncio
    # async def test_async_raises_invalid_field(self):
    #     with pytest.raises(MongoValidationError):
    #         await self.Product.AQ.simple_aggregate(
    #             title='not_match', aggregation=[Avg('cost123'), Max('quantityzzzz')]
    #         )
