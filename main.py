class Expression:
    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op

    def __str__(self) -> str:
        if self.left:
            return '(' + self.left.__str__() + self.op + ' ' + self.right.__str__() + ')'
        else:
            return self.op


class Rule:
    def __init__(self):
        self.head = None
        self.body = None

    def __str__(self) -> str:
        return self.head.__str__() + ((' :- ' + self.body.__str__()) if self.body else '') + '.'


class Parser:
    def __init__(self, string: str):
        self.rest: str = string
        self.expr = Rule()
        self.alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.row = 1
        self.col = 1
        self.expr_list = []

    def skip_ws(self):
        for id, i in enumerate(self.rest):
            if i == ' ':
                self.col += 1
            elif i == '\n':
                self.row += 1
                self.col = 1
            else:
                self.rest = self.rest[id:]
                break

    def expect(self, sub, hard=False):
        self.skip_ws()
        if len(sub) > len(self.rest):
            if hard:
                raise IOError("Syntax error: line {}, colon {}".format(self.row, self.col))
            else:
                return False
        sub_rest = self.rest[:len(sub)]
        if sub == sub_rest:
            self.rest = self.rest[len(sub_rest):]
            self.col += len(sub)
            self.skip_ws()
        if not hard:
            return sub == sub_rest
        else:
            if sub != sub_rest:
                raise IOError("Syntax error: line {}, colon {}".format(self.row, self.col))

    def parse_word(self):
        self.skip_ws()
        word = ''
        for id, i in enumerate(self.rest):
            if i in self.alphabet:
                word += i
            else:
                self.rest = self.rest[id:]
                self.col += id
                break
        self.skip_ws()
        if word == '':
            raise IOError("Syntax error: line {}, colon {}".format(self.row, self.col))
        return Expression(None, None, word)

    def word(self):
        if self.expect('('):
            res = self.disj()
            self.expect(')', True)
            return res
        return self.parse_word()

    def head(self):
        self.expr.head = self.parse_word()

    def conj(self):
        left = self.word()
        if self.expect(','):
            right = self.conj()
            if right is None:
                raise IOError("Syntax error: line {}, colon {}".format(self.row, self.col))
            return Expression(left, right, ',')
        return left

    def disj(self):
        left = self.conj()
        if self.expect(';'):
            right = self.disj()
            if right is None:
                raise IOError("Syntax error: line {}, colon {}".format(self.row, self.col))
            return Expression(left, right, ';')
        return left

    def parser(self):
        while self.rest != '':
            self.head()
            if self.expect('.'):
                pass
            else:
                self.expect(":-", True)
                res = self.disj()
                if res is None:
                    raise IOError("Syntax error: line {}, colon {}".format(self.row, self.col))
                self.expect('.', True)
                self.expr.body = res
            self.expr_list.append(self.expr)
            self.expr = Rule()
        return self.expr_list


with open("data.prolog", "r") as reader:
    data = reader.read()
    parser = Parser(data)
    print(*parser.parser(), sep='\n')