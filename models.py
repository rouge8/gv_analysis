import peewee

database = peewee.SqliteDatabase('gv.db')

class BaseModel(peewee.Model):
    class Meta:
        database = database


class Contact(BaseModel):
    name = peewee.CharField(unique=True, db_index=True)

    def __unicode__(self):
        return u'%s at %s' % (self.name, self.phone)


class Phone(BaseModel):
    phone = peewee.CharField(unique=True, db_index=True)
    contact = peewee.ForeignKeyField(Contact, related_name='phones')


class SMS(BaseModel):
    text = peewee.CharField()
    time = peewee.DateTimeField(unique=True)
    contact = peewee.ForeignKeyField(Contact, related_name='messages')
    from_me = peewee.BooleanField()
    phone = peewee.ForeignKeyField(Phone, related_name='messages')

    def __unicode__(self):
        return u'%s on ' % (self.phone) + unicode(self.time)
