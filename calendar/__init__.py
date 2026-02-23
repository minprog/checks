import check50
import check50.c

@check50.check()
def exists():
    """calendar.c exists"""
    check50.exists('calendar.c')

@check50.check(exists)
def compiles():
    """calendar.c compiles"""
    try:
        check50.c.compile('calendar.c', lcs50=True)
    except check50.Failure as f:
        raise check50.Failure(f"calendar.c does not compile\n{str(f)}") from None


@check50.check(compiles)
def cal_1_1800():
    """displays the correct calendar for Jan 1800"""
    check = check50.run('./calendar').stdin('1800').stdin('1')
    check_calendar_output(check, 'Jan 1800', 3, 31)


@check50.check(cal_1_1800)
def cal_11_2021():
    """displays the correct calendar for Nov 2021"""
    check = check50.run('./calendar').stdin('2021').stdin('11')
    check_calendar_output(check, 'Nov 2021', 1, 30)


@check50.check(cal_11_2021)
def cal_leap_years():
    """displays the correct calendar for Feb/Mar in leap years"""

    # not a leap year
    check = check50.run('./calendar').stdin('1900').stdin('2')
    check_calendar_output(check, 'Feb 1900', 4, 28)

    # march in a leap year
    check = check50.run('./calendar').stdin('2016').stdin('3')
    check_calendar_output(check, 'Mar 2016', 2, 31)

    # special leap year
    check = check50.run('./calendar').stdin('2000').stdin('2')
    check_calendar_output(check, 'Feb 2000', 2, 29)

    # march in that special leap year
    check = check50.run('./calendar').stdin('2000').stdin('3')
    check_calendar_output(check, 'Mar 2000', 3, 31)


# @check50.check(compiles)
# def rejects_wrong_command_line():
#     """rejects any wrong number of command-line arguments"""
#     check50.run('./calendar').stdout('Usage: ./calendar year month').exit(1)
#     check50.run('./calendar 2021 11 -l').stdout('Usage: ./calendar year month').exit(1)


def check_calendar_output(check, month_display, n_padding, n_days):
    # header
    check.stdout(month_display)

    # weekdays until first day of month
    check.stdout('Sun Mon Tue Wed Thu Fri Sat')

    # padding before first day
    check.stdout('\n' + '    ' * n_padding + format(1, '3d'), '<padding> 1')

    # all days but last
    for daynum in range(2, n_days):
        check.stdout(format(daynum, '3d'), format(daynum, 'd'))

    # final day + newline
    check.stdout(f'{n_days}' + r'\s*\n', f'{n_days}\n')

    # make sure nothing follows
    remainder = str(check.stdout())
    if len(remainder) > 0:
        raise check50.Failure('expected end of output after the last day of the month')
