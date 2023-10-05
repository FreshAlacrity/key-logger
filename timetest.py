from time import monotonic

MIN_SECONDS = 0.1


# Via https://stackoverflow.com/a/26151604
def parametrized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)
        return repl
    return layer


@parametrized
def time_test(func, name):
    def aux(*xs, **kws):
        t1 = monotonic()
        result = func(*xs, **kws)
        t2 = monotonic()
        if t2 - t1 > MIN_SECONDS:
            args_len = len(f"{list(xs)} {dict(kws)}")
            if args_len < 2000 and args_len > len("[] {}"):
                print(f"{name} executed in {(t2-t1)}\n(arguments {list(xs)} {dict(kws)})\n\n")
            else:
                print(f"{name} executed in {(t2-t1)}")
        return result
    return aux