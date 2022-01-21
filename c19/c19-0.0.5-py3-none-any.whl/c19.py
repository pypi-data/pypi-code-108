import countries
import getopt
import sys
import os
import pycountry

if __name__ == '__main__':
    pk = None
    try:
        opts, _ = getopt.getopt(sys.argv[1:], 'hsvdxrct', ['help', 'vaccinations',
            'dosage', 'deaths', 'recoveries', 'cases', 'tests'])
    except Exception as e:
        print(e)
        sys.exit(1)

    if opts == []: print('\033[1mHelp\033[0m\t$c19 -h')

    for o, _ in opts:
        if o in ('-h', '--help'):
            print('\033[1mShow this help\033[0m\t\t\t$c19 -h|--help')
            print('\033[1mShow vaccinations\033[0m\t\t$c19 -v|--vaccinations')
            print('\033[1mShow dosage\033[0m\t\t\t$c19 -d|--dosage')
            print('\033[1mShow deaths\033[0m\t\t\t$c19 -x|--deaths')
            print('\033[1mShow cases\033[0m\t\t\t$c19 -c|--cases')
            print('\033[1mShow recoveries\033[0m\t\t\t$c19 -r|--recoveries')
        else:
            if pk is None: pk = countries.pk()
            if o in ('-v', '--vaccinations'):
                vaccs = pk.vaccinations()
                print('\nVACCINATION STATS')
                print('===================')
                print('Partial Vaccinations: {}'.format(vaccs['partial']['total']))
                print('\tPartial Vaccinations Rate: {}'.format(vaccs['partial']['rate']))
                print('Full Vaccinations: {}'.format(vaccs['full']['total']))
                print('\tFull Vaccinations Rate: {}'.format(vaccs['full']['rate']))
            elif o in ('-x', '--deaths'):
                deaths = pk.deaths()
                print('\nDEATHS STATS')
                print('============')
                print('Total Deaths: {}'.format(deaths['total']))
                print('\tDeath Rate: {}'.format(deaths['rate']))
            elif o in ('-d', '--dosage'):
                doses = pk.doses()
                print('\nDOSAGE STATS')
                print('============')
                print('Total Doses Administered: {}'.format(doses['total']))
                print('\tDosage Rate: {}'.format(doses['rate']))
            elif o in ('-r', '--recoveries'):
                recoveries = pk.recoveries()
                print('\nRECOVERY STATS')
                print('==============')
                print('Total Recoveries: {}'.format(recoveries['total']))
                print('\tRecovery Rate: {}'.format(recoveries['rate']))
            elif o in ('-t', '--tests'):
                tests = pk.tests()
                print('\nTESTS STATS')
                print('===========')
                print('Total Tests: {}'.format(tests['total']))
                print('\tTest Rate: {}'.format(tests['rate']))
            elif o in ('-c', '--cases'):
                cases = pk.cases()
                print('\nCASE STATS')
                print('==========')
                print('Total Cases: {}'.format(cases['total']))
                print('\tCase Rate: {}'.format(cases['rate']))
                print('\tCritical Cases: {}'.format(cases['critical']['total']))
                print('\tCritical Case Rate: {}'.format(cases['critical']['rate']))
