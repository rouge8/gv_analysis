from BeautifulSoup import BeautifulSoup
import os
import parse
import spark
from collections import Counter
from pytz import timezone

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

    if len(times) == 0:
        return

    if name:
        print 'Messaged %s %d times.' %(name, len(times))
    else:
        print 'Messaged everyone %d times.' %(len(times))

    hours = [t.hour for t in times]
    hour_count = Counter(hours)

    #for i in range(24):
        #print "%d: %d texts." %(i, hour_count[i])

    graph_data = [hour_count.get(i, 0) for i in range(24)]
    spark.spark_print(graph_data)
    print
    print

import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

def main():
    files = os.listdir('conversations')
    os.chdir('conversations')
    files = [f for f in files if f.endswith('html')]
    names = get_names(files)
    for name in names:
        analyze(name, files)
    analyze(None, files)


if __name__ == '__main__':
    main()
