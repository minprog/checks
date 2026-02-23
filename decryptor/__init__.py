import check50
import check50.c
import check50.internal
import contextlib

helpers = check50.internal.import_file(
    "helpers",
    check50.internal.check_dir / "../helpers/helpers.py"
)
helpers.set_stdout_limit(10000)

@check50.check()
def exists():
    """decryptor.c exists"""
    check50.exists("decryptor.c")

@check50.check(exists)
def compiles():
    """decryptor.c compiles"""
    check50.c.compile("decryptor.c", lcs50=True)

@check50.check(compiles)
def test_base_case():
    """correctly decrypts "gHFrgh Fdhvdu", be sure to prompt for input"""
    (check50.run("./decryptor")
        .stdin("gHFrgh Fdhvdu")
        .stdout(r"dECode Caesar\s?\n", "dECode Caesar\n")
        .exit(0))

@check50.check(test_base_case)
def test_output1():
    """handles automatic decryption of messsages (Lbsdscr dbyyzc oxdobon Mehrkfox 1400 yx 6 Wki)"""
    with logged_check_factory("./decryptor") as decryptor_command:
        (decryptor_command("")
            .stdin("Lbsdscr dbyyzc oxdobon Mehrkfox 1400 yx 6 Wki")
            .stdout(r"British troops entered Cuxhaven 1400 on 6 May", regex=False)
            .exit(0))

@check50.check(test_base_case)
def test_output2():
    """handles automatic decryption of messsages (Rhyjyix jheefi udjuhut Sknxqlud qj 1400 ed 6 Cqo - vhec dem ed qbb hqtye jhqvvys mybb suqiu - myixydw oek qbb jxu ruij. Bj Akdaub 20)"""
    with logged_check_factory("./decryptor") as decryptor_command:
        (decryptor_command("")
            .stdin("Rhyjyix jheefi udjuhut Sknxqlud qj 1400 ed 6 Cqo - vhec dem ed qbb hqtye jhqvvys mybb suqiu - myixydw oek qbb jxu ruij. Bj Akdaub 20")
            .stdout(r"British troops entered Cuxhaven at 1400 on 6 May - from now on all radio traffic will cease - wishing you all the best. Lt Kunkel 20", regex=False)
            .exit(0))
        
# helpers --------------------------------------------------------------------

class Stream:
    """Stream-like object that stores everything it receives"""
    def __init__(self):
        self.entries = []

    @property
    def text(self):
        return "".join(self.entries)

    def write(self, entry):
        entry = entry.replace("\r\n", "\n").replace("\r", "\n")
        self.entries.append(entry)

    def flush(self):
        pass

    def reset(self):
        self.entries = []

@contextlib.contextmanager
def logged_check_factory(command):
    """
    A factory of checks that logs everything on stdin/stdout.
    The log is written to the data.output field of check50's json output.
    """
    stream = Stream()

    def create_check(params):
        check = check50.run(f"{command} {params}")
        check.process.logfile = stream
        return check

    try:
        yield create_check
    finally:
        check50.data(output=stream.text)
