import peewee
try:
    import settings
except ImportError:
    import sys
    print >> sys.stderr, 'ERROR: settings.py missing.'

database = peewee.SqliteDatabase(settings.DATABASE)

class BaseModel(peewee.Model):
    class Meta:
        database = database


class Contact(BaseModel):
    name = peewee.CharField(unique=True, db_index=True)

    def __unicode__(self):
        return unicode(self.name)


class Phone(BaseModel):
    phone = peewee.CharField(unique=True, db_index=True)
    contact = peewee.ForeignKeyField(Contact, related_name='phones')

    def __unicode__(self):
        return unicode(self.phone)


class SMS(BaseModel):
    text = peewee.CharField()
    time = peewee.DateTimeField(unique=True)
    contact = peewee.ForeignKeyField(Contact, related_name='messages')
    from_me = peewee.BooleanField()
    phone = peewee.ForeignKeyField(Phone, related_name='messages')

    def __unicode__(self):
        return u'%s at ' % (self.phone) + unicode(self.time)
