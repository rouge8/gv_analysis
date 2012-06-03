import os
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser
import parse
from models import database, Contact, Phone, SMS, settings

def gv_to_db(me):
    files = os.listdir(settings.CONVERSATIONS_DIR)
    os.chdir(settings.CONVERSATIONS_DIR)
    files = [f for f in files if f.endswith('html')]

    database.set_autocommit(False)

    print len(files)
    count = 1
    for f in files:
        print str(count) + '. ' + f
        count += 1

        # set name
        name = parse.parse('{} - {}', f).fixed[0]

        soup = BeautifulSoup(open(f))
        chat = soup.find('div', {'class': 'hChatLog hfeed'})
        if not chat:
            continue

        messages = chat.findAll('div', {'class': 'message'})
        for message in messages:
            # time
            t = message.find('abbr', {'class': 'dt'})
            if t.get('title'):
                time = parse.parse('{:ti}', t.get('title')).fixed[0]

            # telephone number
            tel = message.find('a', {'class': 'tel'})
            tel = tel.get('href').split('+')[-1].replace('tel:', '')

            # name
            name_tag = message.find('span', 'fn') or message.find('abbr', 'fn')
            name_tag = name_tag.get('title') or name_tag.string

            text = ' '.join(HTMLParser().unescape(i) for i in message.q.contents if isinstance(i, basestring))

            person = Contact.get_or_create(name=name)
            sms = SMS.get_or_create(text=text, time=time, contact=person)
            if name_tag != me.name:
                phone = Phone.get_or_create(phone=tel, contact=person)
            else:
                sms.from_me = True
            sms.phone = Phone.get(phone=tel)

            person.save()
            sms.save()
            phone.save()

    database.commit()

if __name__ == '__main__':
    database.connect()

    if not database.get_tables():
        Contact.create_table()
        SMS.create_table()
        Phone.create_table()

    me = Contact.get_or_create(name=settings.OWNER_NAME)
    me.save()
    for phone in settings.OWNER_PHONES:
        p = Phone.get_or_create(phone=phone, contact=me)
        p.save()

    gv_to_db(me)
    database.close()
