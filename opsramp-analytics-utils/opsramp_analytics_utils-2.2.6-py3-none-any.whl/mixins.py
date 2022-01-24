from flask import request, Response

from .models import Session


PAGE_SIZE = 20


def get_ordering(args, model):
    default_ordering = ''
    if hasattr(model, 'Meta'):
        if hasattr(model.Meta, 'ordering'):
            default_ordering = model.Meta.ordering

    ordering_field = args.get('ordering', default_ordering)
    ordering_dir = 'desc' if ordering_field.startswith('-') else 'asc'
    ordering_field = ordering_field.strip('-')

    return ordering_field, ordering_dir


def get_pagination(args):
    page = int(args.get('page', 1))
    page_size = int(args.get('page_size', PAGE_SIZE))
    offset = (page-1) * page_size

    return offset, page_size


def generic_create_model(model, params):
    entity = model(**params)

    with Session.begin() as session:
        session.add(entity)
        session.flush()
        resp = entity.to_dict()

    return resp


def generic_list_view(model, filter_fields={}, **kwargs):
    extra_params = kwargs.get('extra_params', {})
    if request.method == 'GET':
        args = request.args
        filter_args = {field: args.get(field) for field in filter_fields if args.get(field)}
        filter_args.update(extra_params)
        ordering_field, ordering_dir = get_ordering(args, model)
        offset, limit = get_pagination(args)

        with Session() as session:
            entities = session.query(model).filter_by(**filter_args)
            count = entities.count()
            if ordering_field:
                order_by = getattr(getattr(model, ordering_field), ordering_dir)()
                entities = entities.order_by(order_by)
            entities = entities.offset(offset).limit(limit).all()

        data = [entity.to_dict(False) for entity in entities]
        resp = {
            'results': data,
            'count': count
        }

        return resp
    elif request.method == 'POST':
        try:
            params = request.get_json()
            params.update(extra_params)
            resp = generic_create_model(model, params)
            return resp
        except:
            return Response(status=400)
    elif request.method == 'DELETE':
        args = request.args
        filter_args = {field: args.get(field) for field in filter_fields if args.get(field)}
        filter_args.update(extra_params)

        with Session.begin() as session:
            session.query(model).filter_by(**filter_args).delete()

        return Response(status=200)


def generic_detail_view(model, id):
    with Session() as session:
        entity = session.query(model).filter_by(id=id).first()
    if not entity:
        return Response(status=404)

    if request.method == 'GET':
        return entity.to_dict()
    elif request.method == 'DELETE':
        with Session.begin() as session:
            session.query(model).filter_by(id=id).delete()

        return Response(status=200)
    elif request.method == 'PUT':
        params = request.get_json()
        try:
            with Session.begin() as session:
                entity = session.query(model).filter_by(id=id).first()
                for attr, val in params.items():
                    setattr(entity, attr, val)
                resp = entity.to_dict()
            return resp
        except:
            return Response(status=400)
