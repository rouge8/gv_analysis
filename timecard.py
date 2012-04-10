from BeautifulSoup import BeautifulSoup
import os
import parse
import spark
from collections import Counter, namedtuple
from pytz import timezone
from datetime import datetime, date
import sys
import codecs

YEAR = None


def get_names(files):
    names = []
    for f in files:
        r = parse.parse('{} - {}', f)
        names.append(r.fixed[0])

    return set(names)


def analyze(name, files):
    if name:
        files = [f for f in files if f.startswith(name)]
    times = []
    central = timezone('US/Central')

    for f in files:
        soup = BeautifulSoup(open(f))
        chat = soup.find('div', {'class': 'hChatLog hfeed'})
        if not(chat):
            continue
        timetags = chat.findAll('abbr', {'class': 'dt'})
        for t in timetags:
            if t.get('title'):
                time = parse.parse('{:ti}', t.get('title')).fixed[0]
                if time:
                    time = time.astimezone(central)
                    times.append(time)

    if not times:
        return

    first_contact = min(times).date()

    if YEAR:
        times = [t for t in times if t.year == YEAR]
        first_contact = max(first_contact, date(YEAR, 1, 1))

    if not times:
        return


    days = sorted({t.date() for t in times})
    total = len(times)

    span = (days[-1] - first_contact).days
    span = span if span >= 1 else 1
    texts_per_day = (total*1.0)/span

    if not YEAR or date(YEAR, 12, 31) > datetime.now().date():
        avg_span = (datetime.now().date() - first_contact).days
    elif YEAR:
        avg_span = (date(YEAR,12,31) - first_contact).days

    avg_span = avg_span if avg_span >= 1 else 1
    avg = (total*1.0) / avg_span

    if name:
        print 'Messaged %s %d times, %f/day.' %(name, total, avg)
    else:
        print 'Messaged everyone %d times.' %(len(times))

    hours = [t.hour for t in times]
    hour_count = Counter(hours)

    #for i in range(24):
        #print "%d: %d texts." %(i, hour_count[i])

    hour_data = [hour_count.get(i, 0) for i in range(24)]
    spark.spark_print(hour_data)
    print
    print

    Count = namedtuple('Count', ['name', 'count', 'avgday', 'avg'])
    return Count(name, total, texts_per_day, avg)

sys.stdout = codecs.getwriter('utf8')(sys.stdout)

def main():
    files = os.listdir('conversations')
    os.chdir('conversations')
    files = [f for f in files if f.endswith('html')]
    names = get_names(files)

    message_counts = []

    for name in names:
        result = analyze(name, files)
        if result:
            message_counts.append(result)
    analyze(None, files)

    # totals
    print 'TOP TEN TEXTERS:'
    top = [(i.name, i.count) for i in sorted(message_counts, key=lambda k: k.count, reverse=True) if i.count > 0]
    #for i in range(10):
    for i in range(len(top)):
        print '%d.' %(i+1), top[i][0], top[i][1]

    print

    # averages
    print 'TOP TEN TEXTERS ON DAILY AVERAGES:'
    avgs = [(i.name, round(i.avgday, 2)) for i in sorted(message_counts, key=lambda k: k.avgday, reverse=True) if i.avgday > 0 and i.avgday != i.count]
    for i in range(len(avgs)):
    #for i in range(10):
        print '%d.' %(i+1), avgs[i][0], avgs[i][1]

    print

    # actual averages
    print 'TOP TEXTERS FOR ACTUAL AVERAGES SINCE FIRST TEXT:'
    actual_avgs =  [(i.name, round(i.avg, 2)) for i in sorted(message_counts, key=lambda k: k.avg, reverse=True) if i.count > 0 and i.count != i.avg ]#and i.avg > 1]

    for i, a in enumerate(actual_avgs):
        print '%d.' % (i+1), a[0], a[1]




if __name__ == '__main__':
    main()
