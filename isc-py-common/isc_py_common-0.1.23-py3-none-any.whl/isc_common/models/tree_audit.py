import logging

from django.db.models.query import RawQuerySet

from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditManager, AuditQuerySet

logger = logging.getLogger(__name__)


class TreeAuditModelQuerySet(AuditQuerySet):
    check_dliting = True

    def delete(self):
        if self.check_dliting:
            raise Exception('Удаление без проверки !!!!')
        return super().delete()

    def get_descendants(self,
                        id=None,
                        start=None,
                        end=None,
                        child_id='child_id',
                        parent_id='parent_id',
                        child_parent_value=None,
                        include_self=True,
                        where_clause0='',
                        where_clause='',
                        where_clause1='',
                        order_by_clause='',
                        distinct='',
                        sql_text=None,
                        fields='*',
                        limit=None
                        ) -> RawQuerySet:
        db_name = self.model._meta.db_table

        if where_clause1 == '' and where_clause != '':
            where_clause1 = where_clause

        if limit is not None:
            if not isinstance(limit, int):
                raise Exception(f'limit must be int.')
            limit = f'limit {limit}'
        else:
            limit = ''
        if id is not None:
            if isinstance(id, int):
                id = tuple([id])
            elif isinstance(id, str):
                id = int(id)
            elif not isinstance(id, tuple):
                raise Exception(f'id must be list or int')

        if sql_text is not None:
            res = super().raw(sql_text)
        elif id is not None:
            if where_clause0 == '':
                where_clause0 = f'{child_id if include_self else parent_id} IN %s'

            sql_text = f'''WITH RECURSIVE r AS (
                                select s.* from (SELECT {fields}, 1 AS level
                                FROM {db_name}
                                WHERE {where_clause0}
                                      {"and " + where_clause.replace("where", "") if where_clause else ""} {limit}) as s  
    
                                union all
    
                                SELECT {db_name}.{fields}, r.level + 1 AS level
                                FROM {db_name}
                                    JOIN r
                                ON {db_name}.{parent_id} = r.{child_id})
    
                            select {distinct} {fields} from r {where_clause1} {order_by_clause} limit %s offset %s
                        '''
            # logger.debug(f'sql: {sql_text}')
            res = super().raw(sql_text, params=((id,), end, start))
        else:
            child_parent_value_str = f' = {child_parent_value}'
            if where_clause0 == '':
                where_clause0 = f'{child_id if include_self else parent_id} {"IS NULL" if child_parent_value is None else child_parent_value_str}'
            sql_text = f'''WITH RECURSIVE r AS (
                                            SELECT *, 1 AS level
                                            FROM {db_name}
                                            WHERE {where_clause0}
                                                  {"and " + where_clause.replace("where", "") if where_clause else ""}  

                                            union all

                                            SELECT {db_name}.*, r.level + 1 AS level
                                            FROM {db_name}
                                                JOIN r
                                            ON {db_name}.{parent_id} = r.{child_id})

                                        select {fields} from r {where_clause1} {order_by_clause} limit %s offset %s
                                    '''
            # logger.debug(f'sql: {sql_text}')
            res = super().raw(sql_text, params=(end, start))

        return res

    def get_parents(self,
                    id=None,
                    start=None,
                    end=None,
                    child_id='child_id',
                    parent_id='parent_id',
                    include_self=True,
                    where_clause0='',
                    where_clause='',
                    order_by_clause='',
                    distinct='',
                    sql_text=None,
                    fields='*'
                    ) -> RawQuerySet:
        db_name = self.model._meta.db_table

        if id is not None:
            if isinstance(id, int):
                id = tuple([id])
            elif not isinstance(id, tuple):
                raise Exception(f'id must be list or int')

        if where_clause0 == '':
            where_clause0=f'{parent_id if include_self else child_id} IN %s'

        sql = f'''WITH RECURSIVE r AS (
                            SELECT *, 1 AS level
                            FROM {db_name}
                            WHERE {where_clause0}

                            union all

                            SELECT {db_name}.*, r.level + 1 AS level
                            FROM {db_name}
                                JOIN r
                            ON {db_name}.{child_id} = r.{parent_id})

                        select {distinct} {fields} from r {where_clause} {order_by_clause} limit %s offset %s
                        '''

        # logger.debug(f'sql: {sql}')
        if id is not None:
            res = super().raw(sql, params=((id,), end, start))
        else:
            res = super().raw(sql, params=(end, start))

        return res

    def get_descendants_count(self,
                              id='id',
                              limit=None,
                              limit1=None,
                              offset=None,
                              child_id='child_id',
                              parent_id='parent_id',
                              child_parent_value=None,
                              include_self=True,
                              where_clause0='',
                              where_clause='',
                              where_clause1='',
                              distinct='',
                              sql_text=None,
                              fields='*',
                              ) -> int:
        return len(self.get_descendants(
            id=id,
            start=offset,
            end=limit,
            child_id=child_id,
            parent_id=parent_id,
            child_parent_value=child_parent_value,
            include_self=include_self,
            where_clause=where_clause,
            where_clause0=where_clause0,
            where_clause1=where_clause1,
            distinct=distinct,
            sql_text=sql_text,
            fields=fields,
            limit=limit1
        ))


class TreeAuditModelManager(AuditManager):
    def get_range_rows1(self, request, function=None, distinct_field_names=None):
        request = DSRequest(request=request)
        self.alive_only = request.alive_only
        self.enabledAll = request.enabledAll
        res = self.get_queryset().get_range_rows(start=request.startRow, end=request.endRow, function=function, distinct_field_names=distinct_field_names, json=request.json)
        return res

    def get_descendants(self,
                        id=None,
                        limit=None,
                        limit1=None,
                        offset=None,
                        child_id='child_id',
                        parent_id='parent_id',
                        child_parent_value=None,
                        include_self=True,
                        where_clause0='',
                        where_clause='',
                        where_clause1='',
                        order_by_clause='',
                        distinct='',
                        fields='*',
                        sql_text=None,
                        ) -> RawQuerySet:
        return self.get_queryset().get_descendants(
            id=id,
            start=offset,
            end=limit,
            child_id=child_id,
            parent_id=parent_id,
            child_parent_value=child_parent_value,
            include_self=include_self,
            where_clause0=where_clause0,
            where_clause=where_clause,
            where_clause1=where_clause1,
            order_by_clause=order_by_clause,
            distinct=distinct,
            fields=fields, sql_text=sql_text,
            limit=limit1
        )

    def get_parents(self,
                    id=None,
                    limit=None,
                    offset=None,
                    child_id='child_id',
                    parent_id='parent_id',
                    include_self=True,
                    where_clause0='',
                    where_clause='',
                    distinct='',
                    order_by_clause='',
                    fields='*',
                    sql_text=None,
                    ) -> RawQuerySet:
        return self.get_queryset().get_parents(
            id=id,
            start=offset,
            end=limit,
            child_id=child_id,
            parent_id=parent_id,
            include_self=include_self,
            where_clause0=where_clause0,
            where_clause=where_clause,
            distinct=distinct,
            order_by_clause=order_by_clause,
            fields=fields,
            sql_text=sql_text
        )

    def get_descendants_count(self,
                              id=None,
                              limit=None,
                              limit1=None,
                              offset=None,
                              child_id='child_id',
                              parent_id='parent_id',
                              child_parent_value=None,
                              include_self=True,
                              where_clause0='',
                              where_clause='',
                              where_clause1='',
                              distinct='',
                              sql_text=None,
                              fields='*'
                              ) -> int:
        return self.get_queryset().get_descendants_count(
            id=id,
            limit=limit,
            offset=offset,
            child_id=child_id,
            parent_id=parent_id,
            child_parent_value=child_parent_value,
            include_self=include_self,
            distinct=distinct,
            where_clause=where_clause,
            where_clause0=where_clause0,
            where_clause1=where_clause1,
            sql_text=sql_text,
            fields=fields,
            limit1=limit1
        )

    def get_queryset(self):
        return TreeAuditModelQuerySet(self.model, using=self._db)
