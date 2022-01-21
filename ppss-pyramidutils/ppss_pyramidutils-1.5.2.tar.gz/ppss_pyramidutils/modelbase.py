import sys
PY2 = sys.version_info[0] == 2
if not PY2:
    unicode = str

class ModelCommonParent():

    @classmethod
    def orderAll(cls,q):
        return q

    @classmethod
    def all(cls,DBSession,orderby=None,orderdir='asc'):
        q = cls.orderAll(DBSession.query(cls))
        if orderby is not None:
            if orderdir == 'asc':
                q = q.order_by(getattr(cls,orderby).asc() )
            else:
                q = q.order_by((getattr(cls,orderby).desc()  ))
        return q.all()
        #return cls.orderAll(DBSession.query(cls)).all()
    
    @classmethod
    def byId(cls,id,DBSession):
        return DBSession.query(cls).filter(cls.id==id).first()

    @classmethod
    def byField(cls,field,value,DBSession,orderby=None,orderdir='asc'):
        q = DBSession.query(cls).filter(getattr(cls, field)==value)
        if orderby is not None:
            if orderdir == 'asc':
                q = q.order_by(getattr(cls,orderby).asc() )
            else:
                q = q.order_by((getattr(cls,orderby).desc()  ))
        return q.all()
    
    @classmethod
    def byFields(cls,fields,DBSession,orderby=None,orderdir='asc'):
        q = DBSession.query(cls)
        for i,field in enumerate(fields):
            q = q.filter(getattr(cls, field[0])==field[1])
        if orderby is not None:
            if orderdir == 'asc':
                q = q.order_by(getattr(cls,orderby).asc() )
            else:
                q = q.order_by((getattr(cls,orderby).desc()  ))
        return q.all()


    @classmethod
    def delete(cls,element,DBSession):
        DBSession.delete(element)
    @classmethod
    def deleteAll(cls,elements,DBSession):
        for e in elements:
            DBSession.delete(e)


    def __str__(self):
        return "<{}({})>".format(self.__class__.__name__,self.id) #unicode(self)

    def __repr__(self):
        return unicode(self)

    def __unicode__(self):
        return unicode(str(self))
