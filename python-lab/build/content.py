# Course content for the Python DSA Lab: 7 days from C++ to Python, then a short mock.
# build.py runs every example (to show its real output) and checks every solution
# against its tests with the same judge the browser uses.
import re


def F(pid, title, statement, solution, tests, hint, lc=None, slug=None, diff='E', mode='exact'):
    """A "complete the function" problem. tests = [(args_tuple, expected), ...]"""
    m = re.search(r'^def (\w+)\((.*?)\):', solution, re.M)
    func, params = m.group(1), m.group(2)
    note = '    # change the list in place; you do not need to return anything\n' if mode == 'inplace' else ''
    starter = f'def {func}({params}):\n{note}    # write your code here\n    pass\n'
    return {'id': pid, 'kind': 'func', 'title': title, 'statement': statement, 'func': func,
            'starter': starter, 'solution': solution.strip() + '\n', 'mode': mode, 'hint': hint,
            'lc': lc, 'slug': slug, 'diff': diff,
            'tests': [{'args': list(a), 'expected': e} for a, e in tests]}


def S(pid, title, statement, solution, tests, hint, diff='E'):
    """A "read from standard input, print the answer" problem. tests = [(stdin, expected_stdout), ...]"""
    return {'id': pid, 'kind': 'stdin', 'title': title, 'statement': statement,
            'starter': '# Read the input with input() and print the answer.\n',
            'solution': solution.strip() + '\n', 'hint': hint, 'lc': None, 'slug': None, 'diff': diff,
            'tests': [{'stdin': i, 'expected': o} for i, o in tests]}


DAYS = [
# ---------------------------------------------------------------- Day 1
{
  'id': 'd1', 'n': 1, 'title': 'Basics: variables, loops, functions',
  'goal': 'Write loops, conditions and functions in Python, and read input the way a test gives it.',
  'map': [
    ('int x = 5; double d = 2.5;', 'x = 5\nd = 2.5          # no types'),
    ('long long big = 1e18;', 'big = 10**18     # ints never overflow'),
    ('a / b   (both int)', 'a // b           # a / b gives a float'),
    ('x++;   x += 2;', 'x += 1;  x += 2  # there is no ++'),
    ('&&   ||   !', 'and   or   not'),
    ('if (a) {...} else if (b) {...} else {...}', 'if a:\n    ...\nelif b:\n    ...\nelse:\n    ...'),
    ('for (int i = 0; i < n; i++)', 'for i in range(n):'),
    ('for (int i = a; i <= b; i++)', 'for i in range(a, b + 1):'),
    ('for (int i = n - 1; i >= 0; i--)', 'for i in range(n - 1, -1, -1):'),
    ('for (int i = 0; i < n; i += 2)', 'for i in range(0, n, 2):'),
    ('for (auto x : v)', 'for x in v:'),
    ('while (n > 0) {...}', 'while n > 0:'),
    ('cin >> n;', 'n = int(input())'),
    ('cout << a << " " << b << endl;', 'print(a, b)'),
    ('int add(int a, int b) { return a + b; }', 'def add(a, b):\n    return a + b'),
    ('return {lo, hi};   // a pair', 'return lo, hi    # caller: lo, hi = f()'),
    ('INT_MAX   INT_MIN', "float('inf')   float('-inf')"),
    ('true   false   nullptr', 'True   False   None'),
  ],
  'examples': [
    {'title': 'Variables, maths and printing', 'src': '''a, b = 17, 5
print(a // b, a % b, a / b)        # floor division, remainder, true division
print(2 ** 10, 10 ** 18 + 1)       # powers; no overflow ever
x = 5
x += 1                             # there is no x++
print("x is", x)
print(f"{a} = {b} * {a // b} + {a % b}")   # f-string: values inside {}
print(max(3, 9, 4), min(3, 9, 4), abs(-7))
'''},
    {'title': 'Loops written like C++', 'src': '''for i in range(5):            # 0 1 2 3 4
    print(i, end=" ")
print()
for i in range(2, 11, 2):     # 2 4 6 8 10
    print(i, end=" ")
print()
for i in range(5, 0, -1):     # 5 down to 1
    print(i, end=" ")
print()
n = 1234
while n > 0:                  # digits from the right
    print(n % 10, end=" ")
    n //= 10
print()
for x in [10, 20, 30]:        # like for (auto x : v)
    print(x, end=" ")
print()
'''},
    {'title': 'Functions and returning two values', 'src': '''def add(a, b):
    return a + b

def min_max(nums):
    return min(nums), max(nums)      # returns a tuple, like a pair

lo, hi = min_max([4, 9, 1])          # like auto [lo, hi] = ...
print(add(2, 3), lo, hi)

def greet(name="friend"):            # a default value
    print("Hello,", name)

greet()
greet("Asha")
'''},
    {'title': 'Pass by value or by reference?', 'src': '''def change(num, nums):
    num += 100        # numbers can't change: only the local copy changes
    nums.append(4)    # lists are shared: the caller sees this (like vector<int>&)
    nums = [0]        # this only points the local name somewhere else

x = 1
v = [1, 2, 3]
change(x, v)
print(x, v)
'''},
    {'title': 'Reading input like cin', 'stdin': '5\n3 1 4 1 5\n', 'src': '''n = int(input())                        # first line: 5
nums = list(map(int, input().split()))   # second line: 3 1 4 1 5
print(n, nums, sum(nums))
'''},
  ],
  'traps': [
    'Indentation is the block. Use 4 spaces, the same for every line in the block; a wrong indent is an error.',
    '`/` always gives a float: `7 / 2` is `3.5`. Use `//` for integer division.',
    '`range(a, b)` stops before `b`, exactly like `i < b`.',
    'Numbers and strings behave like pass-by-value; lists, dicts and sets behave like pass-by-reference. Return results with `return`.',
  ],
  'problems': [
    F('sum-digits', 'Sum of digits', 'Return the sum of the digits of a non-negative integer `n`. For example, `1234` gives `10`.', '''
def sum_digits(n):
    total = 0
    while n > 0:
        total += n % 10
        n //= 10
    return total
''', [((1234,), 10), ((0,), 0), ((9,), 9), ((1000000,), 1), ((987654321,), 45)],
      'Take the last digit with `n % 10`, then remove it with `n //= 10`. Repeat while `n > 0`.'),
    F('count-evens', 'Count the even numbers', 'Return how many numbers in the list `nums` are even.', '''
def count_evens(nums):
    count = 0
    for x in nums:
        if x % 2 == 0:
            count += 1
    return count
''', [(([1, 2, 3, 4, 6],), 3), (([],), 0), (([1, 3, 5],), 0), (([0, -2, 7],), 2)],
      '`for x in nums:` and `if x % 2 == 0:`. Keep a counter and return it.'),
    F('reverse-number', 'Reverse a number', 'Return the digits of the non-negative integer `n` in reverse order: `123` gives `321`, and `1200` gives `21`.', '''
def reverse_number(n):
    rev = 0
    while n > 0:
        rev = rev * 10 + n % 10
        n //= 10
    return rev
''', [((123,), 321), ((1200,), 21), ((0,), 0), ((7,), 7), ((90817,), 71809)],
      'Build the answer digit by digit: `rev = rev * 10 + n % 10`, then `n //= 10`.'),
    F('fizz-buzz', 'Fizz Buzz', 'Return a list of strings for 1 to `n`: "FizzBuzz" for multiples of 15, "Fizz" for multiples of 3, "Buzz" for multiples of 5, otherwise the number as a string.', '''
def fizz_buzz(n):
    out = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            out.append("FizzBuzz")
        elif i % 3 == 0:
            out.append("Fizz")
        elif i % 5 == 0:
            out.append("Buzz")
        else:
            out.append(str(i))
    return out
''', [((3,), ['1', '2', 'Fizz']), ((5,), ['1', '2', 'Fizz', '4', 'Buzz']),
      ((15,), ['1', '2', 'Fizz', '4', 'Buzz', 'Fizz', '7', '8', 'Fizz', 'Buzz', '11', 'Fizz', '13', '14', 'FizzBuzz']), ((1,), ['1'])],
      'Loop `for i in range(1, n + 1)`, check 15 first, and use `str(i)` for the number.', lc=412, slug='fizz-buzz'),
    F('min-max', 'Smallest and largest (return a pair)', 'Return the smallest and the largest number of the non-empty list `nums` as a pair: `return lo, hi`. Try it with a loop instead of `min()` and `max()`.', '''
def min_max(nums):
    lo = hi = nums[0]
    for x in nums:
        if x < lo:
            lo = x
        if x > hi:
            hi = x
    return lo, hi
''', [(([4, 9, 1],), [1, 9]), (([5],), [5, 5]), (([-3, -1, -7],), [-7, -1]), (([2, 2, 2],), [2, 2])],
      'Start both with `nums[0]` (not 0, or negative lists break), update in one loop, and `return lo, hi`.'),
    S('stdin-sum-max', 'Read input, print two answers', 'The first line has `n`. The second line has `n` numbers separated by spaces. Print their sum on the first line and the largest number on the second line.', '''
n = int(input())
nums = list(map(int, input().split()))
print(sum(nums))
print(max(nums))
''', [('4\n3 9 1 5\n', '18\n9'), ('1\n-5\n', '-5\n-5'), ('3\n10 20 30\n', '60\n30')],
      '`n = int(input())`, then `nums = list(map(int, input().split()))`, then two `print` lines.'),
  ],
},
# ---------------------------------------------------------------- Day 2
{
  'id': 'd2', 'n': 2, 'title': 'Strings and characters',
  'goal': 'Build and change strings, and convert between characters and numbers (the ASCII tricks).',
  'map': [
    ('string s = "abc";', 's = "abc"        # \'abc\' works too'),
    ('s.size()', 'len(s)'),
    ('s[i]   s.back()', 's[i]   s[-1]'),
    ("s += 'a';   s.push_back(c);", "s += 'a'   s += c      # works the same"),
    ('s.substr(i, k)', 's[i:i + k]'),
    ('reverse(s.begin(), s.end());', 's = s[::-1]'),
    ("s[i] = 'x';", "not allowed: chars = list(s); chars[i] = 'x'; s = ''.join(chars)"),
    ("c - 'a'   (letter position)", "ord(c) - ord('a')"),
    ("c - '0'   (char to number)", "int(c)   or   ord(c) - ord('0')"),
    ("(char)('a' + k)", "chr(ord('a') + k)"),
    ("d + '0'   (number to char)", "str(d)   or   chr(ord('0') + d)"),
    ('to_string(n)   stoi(s)', 'str(n)   int(s)'),
    ('isalpha(c) isdigit(c) isalnum(c)', 'c.isalpha() c.isdigit() c.isalnum()'),
    ('toupper(c)   tolower(c)', 'c.upper()   c.lower()'),
    ('s.find("ab")', 's.find("ab")     # -1 if missing'),
    ('int cnt[26] = {0};', 'cnt = [0] * 26'),
    ('split by spaces (stringstream)', 's.split()   and back: " ".join(words)'),
  ],
  'examples': [
    {'title': 'Building and slicing strings', 'src': '''s = "hello"
s += "!"                  # like s += "!" in C++
s += 'a'                  # one character
print(s, len(s), s[0], s[-1])
print(s[1:4], s[::-1])    # a slice, and the string reversed
print(s.upper(), "Hello World".lower())
words = "the sky is blue".split()
print(words, " ".join(reversed(words)))
chars = list("cat")
chars[0] = "b"            # strings can't change; lists can
print("".join(chars))
'''},
    {'title': 'Characters and numbers (ASCII)', 'src': '''print(ord('a'), ord('A'), ord('0'))      # 97 65 48
print(chr(97), chr(ord('a') + 2))        # a c
c = '7'
print(int(c) + 1, ord(c) - ord('0'))     # char to number: 8 7
d = 5
print(str(d), chr(ord('0') + d))         # number to char: '5'
print(ord('e') - ord('a'))               # position in the alphabet: 4
cnt = [0] * 26
for ch in "banana":
    cnt[ord(ch) - ord('a')] += 1
print(cnt[0], cnt[ord('n') - ord('a')])  # a appears 3 times, n twice
'''},
    {'title': 'Looping over a string', 'src': '''s = "a1b2c3"
total = 0
for ch in s:
    if ch.isdigit():
        total += int(ch)
print(total)
for i, ch in enumerate("abc"):     # index and character together
    print(i, ch)
print("an" in "banana", "banana".count("a"), "banana".find("n"))
'''},
    {'title': 'Building a long string quickly', 'src': '''parts = []
for i in range(5):
    parts.append(str(i))
print("-".join(parts))       # collect pieces, join once at the end
'''},
  ],
  'traps': [
    "Strings can't be changed: `s[0] = 'x'` is an error. Make a list, change it, and `''.join(...)` it back.",
    "`'9' + '1'` is `'91'`. Convert with `int()` before adding.",
    "`'a' + 1` is an error. Use `chr(ord('a') + 1)`.",
    '`s += c` in a very long loop is slower than collecting pieces in a list and joining once.',
  ],
  'problems': [
    F('reverse-words', 'Reverse the words', 'Return the words of `s` in reverse order, separated by single spaces. `s` may have extra spaces anywhere.', '''
def reverse_words(s):
    return " ".join(s.split()[::-1])
''', [(('the sky is blue',), 'blue is sky the'), (('  hello world  ',), 'world hello'), (('a good   example',), 'example good a'), (('one',), 'one')],
      '`s.split()` with no argument drops extra spaces. Reverse the list with `[::-1]` and join with `" "`.', lc=151, slug='reverse-words-in-a-string', diff='M'),
    F('valid-palindrome', 'Valid palindrome', 'Return `True` if `s` reads the same forwards and backwards after keeping only letters and digits and ignoring capitals.', '''
def is_palindrome(s):
    clean = "".join(ch.lower() for ch in s if ch.isalnum())
    return clean == clean[::-1]
''', [(('A man, a plan, a canal: Panama',), True), (('race a car',), False), ((' ',), True), (('0P',), False), (('Madam',), True)],
      'Keep `ch.lower()` for each `ch` where `ch.isalnum()`, join them, and compare with the reversed string.', lc=125, slug='valid-palindrome'),
    F('first-unique', 'First unique character', 'Return the index of the first character that appears only once in `s`, or `-1` if there is none. `s` has only lowercase letters.', '''
def first_uniq_char(s):
    cnt = [0] * 26
    for ch in s:
        cnt[ord(ch) - ord('a')] += 1
    for i, ch in enumerate(s):
        if cnt[ord(ch) - ord('a')] == 1:
            return i
    return -1
''', [(('leetcode',), 0), (('loveleetcode',), 2), (('aabb',), -1), (('z',), 0)],
      'Count with `cnt = [0] * 26` and `ord(ch) - ord("a")`. Then loop again with `enumerate` and return the first index whose count is 1.', lc=387, slug='first-unique-character-in-a-string'),
    F('caesar', 'Shift the letters (Caesar cipher)', 'Shift every lowercase letter of `s` forward by `k` places, wrapping from `z` back to `a`. Leave every other character unchanged.', '''
def caesar_cipher(s, k):
    out = []
    for ch in s:
        if 'a' <= ch <= 'z':
            out.append(chr((ord(ch) - ord('a') + k) % 26 + ord('a')))
        else:
            out.append(ch)
    return "".join(out)
''', [(('abc xyz', 3), 'def abc'), (('hello', 26), 'hello'), (('a-z', 1), 'b-a'), (('python', 13), 'clguba')],
      'Position: `ord(ch) - ord("a")`. Add k, wrap with `% 26`, and turn it back into a letter with `chr(... + ord("a"))`.'),
    F('digits-in-string', 'Add the digits in a string', 'Return the sum of all the digit characters in `s`: `"a1b2c3"` gives `6`.', '''
def sum_digits_in_string(s):
    total = 0
    for ch in s:
        if ch.isdigit():
            total += int(ch)
    return total
''', [(('a1b2c3',), 6), (('abc',), 0), (('9z9',), 18), (('1234',), 10)],
      '`if ch.isdigit(): total += int(ch)`.'),
    F('compress', 'Compress a string', 'Replace each run of the same character by the character and the run length: `"aaabccdd"` gives `"a3b1c2d2"`.', '''
def compress(s):
    out = ""
    i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        out += s[i] + str(j - i)
        i = j
    return out
''', [(('aaabccdd',), 'a3b1c2d2'), (('a',), 'a1'), (('',), ''), (('zzzz',), 'z4')],
      'Two pointers: `j` walks forward while `s[j] == s[i]`. Add `s[i] + str(j - i)` to the answer, then jump `i = j`.'),
    F('valid-anagram', 'Valid anagram (count with 26 slots)', 'Return `True` if `t` uses exactly the same letters as `s`, the same number of times. Both have only lowercase letters. Use `cnt = [0] * 26`.', '''
def is_anagram(s, t):
    if len(s) != len(t):
        return False
    cnt = [0] * 26
    for ch in s:
        cnt[ord(ch) - ord('a')] += 1
    for ch in t:
        cnt[ord(ch) - ord('a')] -= 1
    return all(c == 0 for c in cnt)
''', [(('anagram', 'nagaram'), True), (('rat', 'car'), False), (('a', 'ab'), False), (('listen', 'silent'), True)],
      'Add 1 for each letter of `s`, subtract 1 for each letter of `t`; every slot must end at 0.', lc=242, slug='valid-anagram'),
  ],
},
# ---------------------------------------------------------------- Day 3
{
  'id': 'd3', 'n': 3, 'title': 'Lists (vector), 2D lists, sorting, pairs',
  'goal': 'Use lists like vectors, build 2D grids correctly, and sort anything, including pairs.',
  'map': [
    ('vector<int> v;', 'v = []'),
    ('vector<int> v(n, 0);', 'v = [0] * n'),
    ('v.push_back(x);   v.pop_back();', 'v.append(x)   v.pop()'),
    ('v.back()   v.front()', 'v[-1]   v[0]'),
    ('v.size()   v.empty()', 'len(v)   not v'),
    ('v.insert(v.begin() + i, x);', 'v.insert(i, x)'),
    ('v.erase(v.begin() + i);', 'v.pop(i)   or   del v[i]'),
    ('sort(v.begin(), v.end());', 'v.sort()           # new sorted list: sorted(v)'),
    ('sort(..., greater<int>());', 'v.sort(reverse=True)'),
    ('reverse(v.begin(), v.end());', 'v.reverse()        # new reversed list: v[::-1]'),
    ('vector<vector<int>> g(n, vector<int>(m, 0));', 'g = [[0] * m for _ in range(n)]'),
    ('pair<int,int> p = {1, 2};', 'p = (1, 2)         # a tuple: p[0], p[1]'),
    ("pair<char,int> p = {'a', 3};", "p = ('a', 3)"),
    ('auto [a, b] = p;', 'a, b = p'),
    ('vector<pair<int,int>> v; v.push_back({x, y});', 'v = []; v.append((x, y))'),
    ('sort by .second (comparator)', 'v.sort(key=lambda p: p[1])'),
    ('*max_element   accumulate', 'max(v)   min(v)   sum(v)'),
    ('find(...) != v.end()', 'x in v             # v.index(x) gives the position'),
    ('vector<int> b = a;   // a copy', 'b = a[:]   or   b = a.copy()      # b = a is NOT a copy'),
  ],
  'examples': [
    {'title': 'Everyday list work', 'src': '''v = [5, 2, 9]
v.append(4)
v.insert(0, 7)
print(v, len(v), v[0], v[-1])
x = v.pop()              # removes and returns the last item
print(x, v)
v.sort()
print(v, sorted(v, reverse=True))
v.reverse()
print(v, v[::-1])
print(9 in v, v.index(9), sum(v), max(v))
print([i * i for i in range(5)])          # a list comprehension
'''},
    {'title': '2D lists (the right way and the wrong way)', 'src': '''n, m = 3, 4
grid = [[0] * m for _ in range(n)]   # 3 separate rows
grid[0][1] = 5
print(grid)
bad = [[0] * m] * n                  # WRONG: the same row 3 times
bad[0][1] = 5
print(bad)
for row in grid:
    print(" ".join(map(str, row)))
print(len(grid), len(grid[0]))       # rows, columns
'''},
    {'title': 'Pairs are tuples; sorting them', 'src': '''p = (3, 'x')
a, b = p
print(p[0], p[1], a, b)
pairs = [('b', 2), ('a', 5), ('c', 2)]
pairs.sort()                               # by first, then second
print(pairs)
pairs.sort(key=lambda q: q[1])             # by the number
print(pairs)
pairs.sort(key=lambda q: (-q[1], q[0]))    # number high to low, then letter
print(pairs)
'''},
    {'title': 'Copies, and lists passed to functions', 'src': '''a = [1, 2, 3]
b = a          # the same list with two names
c = a[:]       # a real copy
b.append(4)
print(a, c)

def fill(arr):
    arr[0] = 99      # changes the caller's list (like vector<int>&)

nums = [1, 2]
fill(nums)
print(nums)
'''},
  ],
  'traps': [
    '`[[0] * m] * n` copies one row n times; changing one cell changes the whole column. Use `[[0] * m for _ in range(n)]`.',
    '`v.sort()` changes the list and returns `None`. Never write `v = v.sort()`.',
    '`b = a` does not copy a list. Use `a[:]`.',
    'Tuples cannot be changed: `p[0] = 5` is an error. Make a new tuple instead.',
  ],
  'problems': [
    F('move-zeroes', 'Move zeroes', 'Move all `0`s in `nums` to the end **in place**, keeping the order of the other numbers.', '''
def move_zeroes(nums):
    k = 0
    for i in range(len(nums)):
        if nums[i] != 0:
            nums[k], nums[i] = nums[i], nums[k]
            k += 1
''', [(([0, 1, 0, 3, 12],), [1, 3, 12, 0, 0]), (([0],), [0]), (([1, 2],), [1, 2]), (([0, 0, 1],), [1, 0, 0])],
      'Keep `k`, the place for the next non-zero. For each non-zero, swap it to position `k` and do `k += 1`.', lc=283, slug='move-zeroes', mode='inplace'),
    F('rotate-image', 'Rotate a matrix 90 degrees', 'Rotate the n × n `matrix` 90 degrees clockwise **in place**.', '''
def rotate(matrix):
    n = len(matrix)
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for row in matrix:
        row.reverse()
''', [(([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), [[7, 4, 1], [8, 5, 2], [9, 6, 3]]), (([[1]],), [[1]]),
      (([[1, 2], [3, 4]],), [[3, 1], [4, 2]]),
      (([[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]],), [[15, 13, 2, 5], [14, 3, 4, 1], [12, 6, 8, 9], [16, 7, 10, 11]])],
      'Transpose (swap `matrix[i][j]` with `matrix[j][i]` for `j > i`), then reverse every row.', lc=48, slug='rotate-image', diff='M', mode='inplace'),
    F('sort-pairs', 'Sort pairs by their number', 'Each item of `pairs` is a pair `[letter, count]`. Return them sorted by count from high to low; when counts are equal, by letter from a to z.', '''
def sort_pairs(pairs):
    return sorted(pairs, key=lambda p: (-p[1], p[0]))
''', [(([['a', 2], ['b', 5], ['c', 2]],), [['b', 5], ['a', 2], ['c', 2]]), (([['x', 1]],), [['x', 1]]),
      (([['d', 3], ['a', 3], ['b', 4]],), [['b', 4], ['a', 3], ['d', 3]]), (([],), [])],
      '`sorted(pairs, key=lambda p: (-p[1], p[0]))`: a minus sign makes numbers go high to low.'),
    F('merge-intervals', 'Merge intervals', 'Merge all overlapping intervals `[start, end]` and return the merged list, sorted by start.', '''
def merge(intervals):
    intervals.sort()
    out = []
    for s, e in intervals:
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out
''', [(([[1, 3], [2, 6], [8, 10], [15, 18]],), [[1, 6], [8, 10], [15, 18]]), (([[1, 4], [4, 5]],), [[1, 5]]),
      (([[1, 4], [0, 4]],), [[0, 4]]), (([[1, 4], [2, 3]],), [[1, 4]]), (([[5, 7]],), [[5, 7]])],
      'Sort by start. Walk through; if a start is at most the last end, stretch the last interval, otherwise append a new one.', lc=56, slug='merge-intervals', diff='M'),
    F('pascal', "Pascal's triangle", "Return the first `num_rows` rows of Pascal's triangle as a list of lists.", '''
def generate(num_rows):
    rows = []
    for i in range(num_rows):
        row = [1] * (i + 1)
        for j in range(1, i):
            row[j] = rows[i - 1][j - 1] + rows[i - 1][j]
        rows.append(row)
    return rows
''', [((5,), [[1], [1, 1], [1, 2, 1], [1, 3, 3, 1], [1, 4, 6, 4, 1]]), ((1,), [[1]]), ((2,), [[1], [1, 1]])],
      'Each row starts as `[1] * (i + 1)`. Each inner value is the sum of the two values above it.', lc=118, slug='pascals-triangle'),
    F('spiral', 'Spiral order', 'Return all the values of the `m × n` matrix in spiral order (right, down, left, up, and repeat).', '''
def spiral_order(matrix):
    out = []
    top, bottom, left, right = 0, len(matrix) - 1, 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for j in range(left, right + 1):
            out.append(matrix[top][j])
        top += 1
        for i in range(top, bottom + 1):
            out.append(matrix[i][right])
        right -= 1
        if top <= bottom:
            for j in range(right, left - 1, -1):
                out.append(matrix[bottom][j])
            bottom -= 1
        if left <= right:
            for i in range(bottom, top - 1, -1):
                out.append(matrix[i][left])
            left += 1
    return out
''', [(([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), [1, 2, 3, 6, 9, 8, 7, 4, 5]),
      (([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],), [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]),
      (([[1]],), [1]), (([[1, 2], [3, 4], [5, 6]],), [1, 2, 4, 6, 5, 3])],
      'Keep four borders: top, bottom, left, right. Walk one side, then move that border in. Check `top <= bottom` and `left <= right` before the last two sides.', lc=54, slug='spiral-matrix', diff='M'),
  ],
},
# ---------------------------------------------------------------- Day 4
{
  'id': 'd4', 'n': 4, 'title': 'Hash maps (dict) and sets',
  'goal': 'Use dict as unordered_map, get sorted order like map, and use sets, Counter and defaultdict.',
  'map': [
    ('unordered_map<string,int> m;', 'm = {}'),
    ('m[key] = 5;', 'm[key] = 5'),
    ('m[key]++;   // missing key starts at 0', 'm[key] = m.get(key, 0) + 1'),
    ('m.count(key)   m.find(key) != m.end()', 'key in m'),
    ('m[key]   (key exists)', 'm[key]      # KeyError if missing; m.get(key) gives None'),
    ('m.erase(key);', 'del m[key]   or   m.pop(key, None)'),
    ('for (auto& [k, v] : m)', 'for k, v in m.items():'),
    ('m.size()   m.empty()', 'len(m)   not m'),
    ('map<int,int>   (keys in sorted order)', 'use a dict, then loop over sorted(m)'),
    ('unordered_set<int> s;   s.insert(x);', 's = set();   s.add(x)'),
    ('s.count(x)', 'x in s'),
    ('s.erase(x);', 's.discard(x)     # s.remove(x) errors if x is missing'),
    ('map<pair<int,int>,int>', 'm[(r, c)] = 1    # tuples can be keys, lists cannot'),
    ('counting frequencies', 'from collections import Counter;  cnt = Counter(nums)'),
    ('map<int, vector<int>>', 'from collections import defaultdict;  g = defaultdict(list)'),
  ],
  'examples': [
    {'title': 'dict is your unordered_map', 'src': '''m = {}
m["apple"] = 3
m["mango"] = 5
m["apple"] += 1
print(m, len(m))
print(m["apple"], m.get("kiwi"), m.get("kiwi", 0))
print("mango" in m, "kiwi" in m)
del m["mango"]                # erase
print(m)
print(m.pop("apple"), m)      # pop removes and returns the value
'''},
    {'title': 'Counting, looping, and sorted order like map', 'src': '''nums = [3, 1, 3, 2, 3, 1]
freq = {}
for x in nums:
    freq[x] = freq.get(x, 0) + 1
print(freq)
for k, v in freq.items():
    print(k, "->", v)
for k in sorted(freq):            # like std::map: keys in order
    print(k, freq[k], end=" | ")
print()
print(max(freq, key=freq.get))    # the key with the biggest count
'''},
    {'title': 'Counter and defaultdict', 'src': '''from collections import Counter, defaultdict
cnt = Counter("mississippi")
print(cnt["s"], cnt["z"], cnt.most_common(2))
groups = defaultdict(list)
for w in ["eat", "tea", "tan", "ate"]:
    groups["".join(sorted(w))].append(w)
print(dict(groups))
'''},
    {'title': 'Sets', 'src': '''s = set()
s.add(3)
s.add(1)
s.add(3)                 # already there
print(s, len(s), 3 in s)
s.discard(10)            # no error when missing
s.remove(3)              # error when missing
print(s)
a, b = {1, 2, 3}, {2, 3, 4}
print(a & b, a | b, a - b)
print(sorted({5, 1, 4}))
'''},
  ],
  'traps': [
    '`m[k]` on a missing key is a KeyError. Use `m.get(k, 0)`, check `k in m` first, or use `defaultdict`.',
    'Lists cannot be keys. Use a tuple like `(r, c)` or a string.',
    'A dict keeps insertion order, but it is not sorted. When you need sorted keys, loop over `sorted(m)`.',
    "Don't add or delete keys while looping over a dict; loop over `list(m)` instead.",
  ],
  'problems': [
    F('two-sum', 'Two sum', 'Return the indexes of the two numbers in `nums` that add up to `target`. There is exactly one answer; you may return the indexes in any order.', '''
def two_sum(nums, target):
    pos = {}
    for i, x in enumerate(nums):
        if target - x in pos:
            return [pos[target - x], i]
        pos[x] = i
''', [(([2, 7, 11, 15], 9), [0, 1]), (([3, 2, 4], 6), [1, 2]), (([3, 3], 6), [0, 1]), (([-1, -2, -3, -4, -5], -8), [2, 4])],
      'Keep `pos = {}` from value to index. For each `x`, check whether `target - x` is already in `pos`.', lc=1, slug='two-sum', mode='any_order'),
    F('contains-duplicate', 'Contains duplicate', 'Return `True` if any value appears at least twice in `nums`.', '''
def contains_duplicate(nums):
    seen = set()
    for x in nums:
        if x in seen:
            return True
        seen.add(x)
    return False
''', [(([1, 2, 3, 1],), True), (([1, 2, 3, 4],), False), (([],), False), (([1, 1, 1, 3, 3, 4, 3, 2, 4, 2],), True)],
      'A set remembers what you have seen: `if x in seen: return True`, else `seen.add(x)`. Or compare `len(set(nums))` with `len(nums)`.', lc=217, slug='contains-duplicate'),
    F('group-anagrams', 'Group anagrams', 'Group the words of `strs` that are anagrams of each other. The groups, and the words inside them, may be in any order.', '''
from collections import defaultdict

def group_anagrams(strs):
    groups = defaultdict(list)
    for w in strs:
        groups["".join(sorted(w))].append(w)
    return list(groups.values())
''', [((['eat', 'tea', 'tan', 'ate', 'nat', 'bat'],), [['bat'], ['nat', 'tan'], ['ate', 'eat', 'tea']]), (([''],), [['']]),
      ((['a'],), [['a']]), ((['ab', 'ba', 'abc'],), [['ab', 'ba'], ['abc']])],
      'Words that are anagrams have the same sorted letters. Use `"".join(sorted(w))` as the key of a `defaultdict(list)`.', lc=49, slug='group-anagrams', diff='M', mode='groups'),
    F('top-k', 'Top k frequent elements', 'Return the `k` most frequent values in `nums`, in any order.', '''
from collections import Counter

def top_k_frequent(nums, k):
    return [x for x, _ in Counter(nums).most_common(k)]
''', [(([1, 1, 1, 2, 2, 3], 2), [1, 2]), (([1], 1), [1]), (([4, 4, 5, 5, 5, 6], 1), [5]), (([3, 0, 1, 0], 1), [0])],
      'Count with `Counter(nums)`. `most_common(k)` gives the k most common `(value, count)` pairs.', lc=347, slug='top-k-frequent-elements', diff='M', mode='any_order'),
    F('longest-consecutive', 'Longest consecutive sequence', 'Return the length of the longest run of consecutive numbers (like 1, 2, 3, 4) that can be made from the values in `nums`, in O(n).', '''
def longest_consecutive(nums):
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:
            y = x
            while y + 1 in s:
                y += 1
            best = max(best, y - x + 1)
    return best
''', [(([100, 4, 200, 1, 3, 2],), 4), (([0, 3, 7, 2, 5, 8, 4, 6, 0, 1],), 9), (([],), 0), (([1, 2, 0, 1],), 3)],
      'Put everything in a set. Only start counting at numbers where `x - 1` is not in the set, then walk `x + 1, x + 2, ...`.', lc=128, slug='longest-consecutive-sequence', diff='M'),
    F('subarray-sum-k', 'Subarray sum equals k', 'Return how many continuous subarrays of `nums` add up to exactly `k`.', '''
def subarray_sum(nums, k):
    seen = {0: 1}
    total = count = 0
    for x in nums:
        total += x
        count += seen.get(total - k, 0)
        seen[total] = seen.get(total, 0) + 1
    return count
''', [(([1, 1, 1], 2), 2), (([1, 2, 3], 3), 2), (([1, -1, 0], 0), 3), (([3], 3), 1)],
      'Prefix sums: keep how many times each running total has appeared, starting with `{0: 1}`. Each time, add the count of `total - k`.', lc=560, slug='subarray-sum-equals-k', diff='M'),
    F('word-count', 'Word counts in sorted order (like map)', 'Return a list of `[word, count]` pairs for the words in `text`, sorted by word.', '''
def word_count_sorted(text):
    cnt = {}
    for w in text.split():
        cnt[w] = cnt.get(w, 0) + 1
    return [[w, cnt[w]] for w in sorted(cnt)]
''', [(('b a b c a b',), [['a', 2], ['b', 3], ['c', 1]]), (('one',), [['one', 1]]), (('',), []), (('x y x',), [['x', 2], ['y', 1]])],
      'Count into a dict, then loop over `sorted(cnt)`. Returning `(w, count)` tuples is fine too.'),
  ],
},
# ---------------------------------------------------------------- Day 5
{
  'id': 'd5', 'n': 5, 'title': 'Stack, queue and heap',
  'goal': 'Use a list as a stack, deque as a queue, and heapq as a priority queue.',
  'map': [
    ('stack<int> st;', 'st = []'),
    ('st.push(x);', 'st.append(x)'),
    ('st.top()', 'st[-1]'),
    ('st.pop();', 'st.pop()           # also returns the value'),
    ('st.empty()', 'not st             # True when empty'),
    ('queue<int> q;', 'from collections import deque;   q = deque()'),
    ('q.push(x);', 'q.append(x)'),
    ('q.front();   q.pop();', 'q[0]   q.popleft()'),
    ('deque: push_front / pop_back', 'q.appendleft(x)   q.pop()'),
    ('priority_queue<int, vector<int>, greater<int>>   (min-heap)', 'import heapq;   h = []'),
    ('pq.push(x);', 'heapq.heappush(h, x)'),
    ('pq.top()', 'h[0]               # the smallest'),
    ('pq.pop();', 'heapq.heappop(h)   # returns the smallest'),
    ('priority_queue<int>   (max-heap)', 'push -x; the top is -h[0]'),
    ('priority_queue<pair<int,int>>', 'heapq.heappush(h, (dist, node))   # compares the first item first'),
    ('make_heap(v.begin(), v.end());', 'heapq.heapify(v)'),
  ],
  'examples': [
    {'title': 'Stack', 'src': '''st = []
st.append(1)
st.append(2)
st.append(3)
print(st[-1], len(st))     # top and size
print(st.pop(), st)        # pop gives back the top
if not st:
    print("empty")
else:
    print("not empty")
while st:                  # pop until empty
    st.pop()
print(not st)
'''},
    {'title': 'Queue with deque', 'src': '''from collections import deque
q = deque([1, 2])
q.append(3)               # push at the back
q.appendleft(0)           # push at the front
print(q, q[0], q[-1])
print(q.popleft(), q.pop(), q)   # remove from the front and from the back
print(len(q), not q)
'''},
    {'title': 'Heaps (priority queue)', 'src': '''import heapq
h = []
for x in [5, 1, 8, 3]:
    heapq.heappush(h, x)
print(h[0], heapq.heappop(h), heapq.heappop(h))   # smallest first
maxh = []
for x in [5, 1, 8, 3]:
    heapq.heappush(maxh, -x)                       # max-heap trick
print(-maxh[0], -heapq.heappop(maxh))
tasks = []
heapq.heappush(tasks, (2, "write"))
heapq.heappush(tasks, (1, "read"))
print(heapq.heappop(tasks))                        # (priority, value) pairs
nums = [4, 1, 7, 3]
heapq.heapify(nums)
print(nums[0], heapq.nlargest(2, nums))
'''},
    {'title': 'BFS on a grid (a queue at work)', 'src': '''from collections import deque
grid = ["..#",
        ".#.",
        "..."]
n, m = len(grid), len(grid[0])
dist = [[-1] * m for _ in range(n)]
dist[0][0] = 0
q = deque([(0, 0)])
while q:
    r, c = q.popleft()
    for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < n and 0 <= nc < m and grid[nr][nc] == '.' and dist[nr][nc] == -1:
            dist[nr][nc] = dist[r][c] + 1
            q.append((nr, nc))
print(dist[n - 1][m - 1])      # steps to the bottom-right corner
'''},
  ],
  'traps': [
    '`st.pop()` and `st[-1]` on an empty list are IndexErrors. Check `if st:` first.',
    'Never use `list.pop(0)` as a queue: it moves every element. Use `deque.popleft()`.',
    'heapq is always a min-heap. For a max-heap push `-x` and negate when you read.',
    'Python lets you write `0 <= r < n` for the bounds check.',
  ],
  'problems': [
    F('valid-parentheses', 'Valid parentheses', 'Return `True` if every bracket in `s` (`()[]{}`) is closed by the same type, in the right order.', '''
def is_valid(s):
    pair = {')': '(', ']': '[', '}': '{'}
    st = []
    for ch in s:
        if ch in pair:
            if not st or st.pop() != pair[ch]:
                return False
        else:
            st.append(ch)
    return not st
''', [(('()',), True), (('()[]{}',), True), (('(]',), False), (('([)]',), False), (('{[]}',), True), (('(',), False), ((']',), False)],
      'Push opening brackets. For a closing one, the stack must not be empty and its top must be the matching opener. At the end the stack must be empty.', lc=20, slug='valid-parentheses'),
    F('next-greater', 'Next greater element', 'For each number, return the first larger number to its right, or `-1` if there is none.', '''
def next_greater(nums):
    ans = [-1] * len(nums)
    st = []
    for i, x in enumerate(nums):
        while st and nums[st[-1]] < x:
            ans[st.pop()] = x
        st.append(i)
    return ans
''', [(([2, 1, 2, 4, 3],), [4, 2, 4, -1, -1]), (([1, 2, 3],), [2, 3, -1]), (([3, 2, 1],), [-1, -1, -1]), (([5],), [-1])],
      'Monotonic stack of indexes still waiting for an answer. When a bigger `x` arrives, pop them and set their answer to `x`.'),
    F('daily-temperatures', 'Daily temperatures', 'For each day, return how many days you wait for a warmer temperature, or `0` if it never comes.', '''
def daily_temperatures(temperatures):
    ans = [0] * len(temperatures)
    st = []
    for i, t in enumerate(temperatures):
        while st and temperatures[st[-1]] < t:
            j = st.pop()
            ans[j] = i - j
        st.append(i)
    return ans
''', [(([73, 74, 75, 71, 69, 72, 76, 73],), [1, 1, 4, 2, 1, 1, 0, 0]), (([30, 40, 50, 60],), [1, 1, 1, 0]), (([30, 60, 90],), [1, 1, 0])],
      'Same stack as "Next greater element", but store the distance `i - j`.', lc=739, slug='daily-temperatures', diff='M'),
    F('kth-largest', 'Kth largest element (heap)', 'Return the `k`-th largest number in `nums`. Use a min-heap that keeps only `k` numbers.', '''
import heapq

def find_kth_largest(nums, k):
    h = []
    for x in nums:
        heapq.heappush(h, x)
        if len(h) > k:
            heapq.heappop(h)
    return h[0]
''', [(([3, 2, 1, 5, 6, 4], 2), 5), (([3, 2, 3, 1, 2, 4, 5, 5, 6], 4), 4), (([1], 1), 1), (([7, 7, 7], 2), 7)],
      'Push each number; when the heap holds more than k, pop the smallest. The top `h[0]` is the answer.', lc=215, slug='kth-largest-element-in-an-array', diff='M'),
    F('last-stone', 'Last stone weight (max-heap)', 'Each turn, smash the two heaviest stones. Equal stones both break; otherwise the heavier one becomes the difference. Return the last stone\'s weight, or `0`.', '''
import heapq

def last_stone_weight(stones):
    h = [-s for s in stones]
    heapq.heapify(h)
    while len(h) > 1:
        a = -heapq.heappop(h)
        b = -heapq.heappop(h)
        if a != b:
            heapq.heappush(h, -(a - b))
    return -h[0] if h else 0
''', [(([2, 7, 4, 1, 8, 1],), 1), (([1],), 1), (([2, 2],), 0), (([10, 4, 4, 2],), 0)],
      'Max-heap trick: store `-s`. Pop two, push back the difference (negated) when it is not zero.', lc=1046, slug='last-stone-weight'),
    F('num-islands', 'Number of islands (BFS)', '`grid` is a list of rows of "1" (land) and "0" (water). Return the number of islands; land cells join up, down, left and right.', '''
from collections import deque

def num_islands(grid):
    n, m = len(grid), len(grid[0])
    seen = [[False] * m for _ in range(n)]
    count = 0
    for r in range(n):
        for c in range(m):
            if grid[r][c] == "1" and not seen[r][c]:
                count += 1
                seen[r][c] = True
                q = deque([(r, c)])
                while q:
                    x, y = q.popleft()
                    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < n and 0 <= ny < m and grid[nx][ny] == "1" and not seen[nx][ny]:
                            seen[nx][ny] = True
                            q.append((nx, ny))
    return count
''', [(([['1', '1', '1', '1', '0'], ['1', '1', '0', '1', '0'], ['1', '1', '0', '0', '0'], ['0', '0', '0', '0', '0']],), 1),
      (([['1', '1', '0', '0', '0'], ['1', '1', '0', '0', '0'], ['0', '0', '1', '0', '0'], ['0', '0', '0', '1', '1']],), 3),
      (([['0']],), 0), (([['1', '0', '1']],), 2)],
      'For each unseen "1", count an island and BFS from it with a deque, marking cells as seen.', lc=200, slug='number-of-islands', diff='M'),
  ],
},
# ---------------------------------------------------------------- Day 6
{
  'id': 'd6', 'n': 6, 'title': 'Two pointers and sliding window',
  'goal': 'Write the two-pointer and sliding-window patterns you know from C++ in Python.',
  'map': [
    ('int l = 0, r = n - 1;', 'l, r = 0, len(nums) - 1'),
    ('while (l < r) { ...; l++; r--; }', 'while l < r:\n    ...\n    l += 1\n    r -= 1'),
    ('for (int r = 0; r < n; r++) { while (bad) l++; }', 'l = 0\nfor r in range(len(nums)):\n    while bad:\n        l += 1'),
    ('ans = max(ans, r - l + 1);', 'ans = max(ans, r - l + 1)'),
    ('unordered_map<char,int> window;', 'window = {}   or   Counter()'),
    ('int best = INT_MAX;', "best = float('inf')"),
    ('swap(a[l], a[r]);', 'a[l], a[r] = a[r], a[l]'),
  ],
  'examples': [
    {'title': 'Two pointers on a sorted list', 'src': '''def pair_with_sum(nums, target):
    l, r = 0, len(nums) - 1
    while l < r:
        s = nums[l] + nums[r]
        if s == target:
            return l, r
        if s < target:
            l += 1
        else:
            r -= 1
    return -1, -1

print(pair_with_sum([1, 3, 4, 6, 9], 10))
print(pair_with_sum([1, 2], 10))
'''},
    {'title': 'Fixed-size window', 'src': '''def max_window_sum(nums, k):
    window = sum(nums[:k])
    best = window
    for r in range(k, len(nums)):
        window += nums[r] - nums[r - k]    # add the new one, drop the old one
        best = max(best, window)
    return best

print(max_window_sum([2, 1, 5, 1, 3, 2], 3))
'''},
    {'title': 'Growing window: longest with no repeats', 'src': '''def longest_unique(s):
    last = {}              # character -> its last index
    l = best = 0
    for r, ch in enumerate(s):
        if ch in last and last[ch] >= l:
            l = last[ch] + 1
        last[ch] = r
        best = max(best, r - l + 1)
    return best

print(longest_unique("abcabcbb"), longest_unique("bbbbb"))
'''},
    {'title': 'Shrinking window: shortest with sum at least target', 'src': '''def min_len(target, nums):
    l = total = 0
    best = float('inf')
    for r in range(len(nums)):
        total += nums[r]
        while total >= target:
            best = min(best, r - l + 1)
            total -= nums[l]
            l += 1
    return 0 if best == float('inf') else best

print(min_len(7, [2, 3, 1, 2, 4, 3]))
'''},
  ],
  'traps': [
    'The window length is `r - l + 1`.',
    'Update the answer when the window is valid: after shrinking (for "longest") or inside the shrink loop (for "shortest").',
    "For a minimum, start with `float('inf')` and turn it into the required value (often 0) when nothing was found.",
    "`while l < r:` needs `l += 1` or `r -= 1` on every path, or it loops forever (the lab stops it after a few seconds).",
  ],
  'problems': [
    F('two-sum-sorted', 'Two sum on a sorted list', '`numbers` is sorted. Return the **1-based** positions `[i, j]` (i < j) of the two numbers that add up to `target`.', '''
def two_sum_sorted(numbers, target):
    l, r = 0, len(numbers) - 1
    while l < r:
        s = numbers[l] + numbers[r]
        if s == target:
            return [l + 1, r + 1]
        if s < target:
            l += 1
        else:
            r -= 1
''', [(([2, 7, 11, 15], 9), [1, 2]), (([2, 3, 4], 6), [1, 3]), (([-1, 0], -1), [1, 2]), (([1, 2, 3, 4, 4, 9, 56, 90], 8), [4, 5])],
      'Start at both ends. Sum too small: move `l` right. Too big: move `r` left.', lc=167, slug='two-sum-ii-input-array-is-sorted', diff='M'),
    F('max-sum-k', 'Maximum sum of k in a row', 'Return the largest sum of `k` consecutive numbers in `nums`.', '''
def max_sum_k(nums, k):
    window = sum(nums[:k])
    best = window
    for r in range(k, len(nums)):
        window += nums[r] - nums[r - k]
        best = max(best, window)
    return best
''', [(([2, 1, 5, 1, 3, 2], 3), 9), (([1, 2, 3], 3), 6), (([5, -1, 3], 1), 5), (([-2, -3, -1], 2), -4)],
      'Sum the first k, then slide: add `nums[r]`, subtract `nums[r - k]`. Start `best` at the first window, not at 0.'),
    F('longest-unique', 'Longest substring without repeating characters', 'Return the length of the longest substring of `s` with no repeated characters.', '''
def length_of_longest_substring(s):
    last = {}
    l = best = 0
    for r, ch in enumerate(s):
        if ch in last and last[ch] >= l:
            l = last[ch] + 1
        last[ch] = r
        best = max(best, r - l + 1)
    return best
''', [(('abcabcbb',), 3), (('bbbbb',), 1), (('pwwkew',), 3), (('',), 0), (('dvdf',), 3), (('abba',), 2)],
      'Remember the last index of each character. If it is inside the window, move `l` just past it.', lc=3, slug='longest-substring-without-repeating-characters', diff='M'),
    F('max-ones', 'Max consecutive ones with k flips', '`nums` has only 0s and 1s. You may flip at most `k` zeros. Return the longest run of 1s you can get.', '''
def longest_ones(nums, k):
    l = zeros = best = 0
    for r in range(len(nums)):
        if nums[r] == 0:
            zeros += 1
        while zeros > k:
            if nums[l] == 0:
                zeros -= 1
            l += 1
        best = max(best, r - l + 1)
    return best
''', [(([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2), 6), (([0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1], 3), 10),
      (([0, 0], 0), 0), (([1, 1], 0), 2)],
      'Grow the window and count its zeros. While there are more than k zeros, shrink from the left.', lc=1004, slug='max-consecutive-ones-iii', diff='M'),
    F('min-subarray-len', 'Shortest subarray with a big enough sum', 'All numbers are positive. Return the length of the shortest continuous subarray whose sum is at least `target`, or `0` if there is none.', '''
def min_sub_array_len(target, nums):
    l = total = 0
    best = float('inf')
    for r in range(len(nums)):
        total += nums[r]
        while total >= target:
            best = min(best, r - l + 1)
            total -= nums[l]
            l += 1
    return 0 if best == float('inf') else best
''', [((7, [2, 3, 1, 2, 4, 3]), 2), ((4, [1, 4, 4]), 1), ((11, [1, 1, 1, 1, 1, 1, 1, 1]), 0), ((15, [1, 2, 3, 4, 5]), 5)],
      "Add `nums[r]`. While the sum is at least target, record the length and shrink from the left. Start with `float('inf')`.", lc=209, slug='minimum-size-subarray-sum', diff='M'),
    F('container-water', 'Container with most water', 'Choose two lines; the water between them is `min(height) * distance`. Return the most water.', '''
def max_area(height):
    l, r = 0, len(height) - 1
    best = 0
    while l < r:
        best = max(best, min(height[l], height[r]) * (r - l))
        if height[l] < height[r]:
            l += 1
        else:
            r -= 1
    return best
''', [(([1, 8, 6, 2, 5, 4, 8, 3, 7],), 49), (([1, 1],), 1), (([4, 3, 2, 1, 4],), 16), (([1, 2, 1],), 2)],
      'Start at both ends and always move the shorter line inwards.', lc=11, slug='container-with-most-water', diff='M'),
    F('longest-limit', 'Longest continuous subarray within a limit', 'Return the length of the longest continuous subarray in which the difference between the largest and smallest number is at most `limit`.', '''
from collections import deque

def longest_subarray(nums, limit):
    mx, mn = deque(), deque()
    l = best = 0
    for r, x in enumerate(nums):
        while mx and mx[-1] < x:
            mx.pop()
        mx.append(x)
        while mn and mn[-1] > x:
            mn.pop()
        mn.append(x)
        while mx[0] - mn[0] > limit:
            if nums[l] == mx[0]:
                mx.popleft()
            if nums[l] == mn[0]:
                mn.popleft()
            l += 1
        best = max(best, r - l + 1)
    return best
''', [(([8, 2, 4, 7], 4), 2), (([10, 1, 2, 4, 7, 2], 5), 4), (([4, 2, 2, 2, 4, 4, 2, 2], 0), 3), (([1], 0), 1)],
      'Sliding window plus two deques: one keeps the window maximum at the front (decreasing), one keeps the minimum (increasing). Shrink while max - min > limit.', lc=1438, slug='longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit', diff='M'),
  ],
},
# ---------------------------------------------------------------- Day 7
{
  'id': 'd7', 'n': 7, 'title': 'Recursion and dynamic programming',
  'goal': 'Write DP tables and memoised recursion in Python, including House Robber.',
  'map': [
    ('vector<int> dp(n + 1, 0);', 'dp = [0] * (n + 1)'),
    ('vector<vector<int>> dp(n, vector<int>(m, -1));', 'dp = [[-1] * m for _ in range(n)]'),
    ('memset(dp, -1, sizeof dp);', 'build the table with -1 as above'),
    ('memo map + recursion', 'from functools import cache;   put @cache above the function'),
    ('INT_MAX in a min-DP', "float('inf')"),
    ('a global counter used in recursion', 'nonlocal counter   inside a nested function'),
    ('max({a, b, c})', 'max(a, b, c)'),
    ('res.push_back(path);   // copies', 'res.append(path[:])   # copy it yourself'),
  ],
  'examples': [
    {'title': 'Bottom-up 1D DP', 'src': '''def climb(n):
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        dp[i] = dp[i - 1] + (dp[i - 2] if i >= 2 else 0)
    return dp[n]

print([climb(n) for n in range(1, 8)])
'''},
    {'title': 'Top-down with @cache (memoisation)', 'src': '''from functools import cache

def min_coins(coins, amount):
    @cache
    def go(a):
        if a == 0:
            return 0
        best = float('inf')
        for c in coins:
            if c <= a:
                best = min(best, go(a - c) + 1)
        return best
    ans = go(amount)
    return ans if ans != float('inf') else -1

print(min_coins([1, 2, 5], 11), min_coins([2], 3))
'''},
    {'title': 'A 2D DP table', 'src': '''def lcs(a, b):
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]

print(lcs("abcde", "ace"))
'''},
    {'title': 'Recursion helpers: copying the path, and nonlocal', 'src': '''def subsets(nums):
    res, path = [], []
    def dfs(i):
        if i == len(nums):
            res.append(path[:])     # copy: path keeps changing
            return
        path.append(nums[i])
        dfs(i + 1)
        path.pop()
        dfs(i + 1)
    dfs(0)
    return res

print(subsets([1, 2]))

def count_calls(n):
    total = 0
    def go(k):
        nonlocal total              # change the outer variable
        total += 1
        if k > 0:
            go(k - 1)
    go(n)
    return total

print(count_calls(4))
'''},
  ],
  'traps': [
    'Build 2D tables with `[[0] * m for _ in range(n)]`, never `[[0] * m] * n`.',
    '`@cache` needs arguments that can be dictionary keys: numbers, strings, tuples. Not lists.',
    'Deep recursion (more than about 1000 calls) fails in Python. When n can be large, write the DP bottom-up.',
    '`res.append(path)` stores the same list again and again; append `path[:]`.',
  ],
  'problems': [
    F('climb-stairs', 'Climbing stairs', 'You can climb 1 or 2 steps at a time. Return the number of different ways to reach step `n`.', '''
def climb_stairs(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a
''', [((2,), 2), ((3,), 3), ((5,), 8), ((1,), 1), ((10,), 89)],
      '`ways(n) = ways(n - 1) + ways(n - 2)`: Fibonacci. Two variables are enough.', lc=70, slug='climbing-stairs'),
    F('house-robber', 'House robber', 'You cannot rob two houses next to each other. Return the most money you can rob from `nums`.', '''
def rob(nums):
    prev2 = prev1 = 0
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1
''', [(([1, 2, 3, 1],), 4), (([2, 7, 9, 3, 1],), 12), (([5],), 5), (([2, 1, 1, 2],), 4), (([0],), 0)],
      'For each house: skip it (`prev1`) or rob it (`prev2 + x`). Keep the best of the two.', lc=198, slug='house-robber', diff='M'),
    F('max-subarray', 'Maximum subarray (Kadane)', 'Return the largest sum of a non-empty continuous subarray.', '''
def max_sub_array(nums):
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best
''', [(([-2, 1, -3, 4, -1, 2, 1, -5, 4],), 6), (([1],), 1), (([5, 4, -1, 7, 8],), 23), (([-3, -1, -2],), -1)],
      'Either start fresh at `x` or extend: `cur = max(x, cur + x)`. Start with `nums[0]`, not 0.', lc=53, slug='maximum-subarray', diff='M'),
    F('coin-change', 'Coin change', 'Return the fewest coins needed to make `amount`, or `-1` if it cannot be made.', '''
def coin_change(coins, amount):
    dp = [0] + [float('inf')] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
''', [(([1, 2, 5], 11), 3), (([2], 3), -1), (([1], 0), 0), (([2, 5, 10, 1], 27), 4), (([186, 419, 83, 408], 6249), 20)],
      "`dp[a]` = fewest coins for amount a. `dp[0] = 0`, others start at `float('inf')`; try every coin.", lc=322, slug='coin-change', diff='M'),
    F('unique-paths', 'Unique paths (2D DP)', 'A robot moves only right or down in an `m × n` grid. Return the number of paths from the top-left to the bottom-right.', '''
def unique_paths(m, n):
    dp = [[1] * n for _ in range(m)]
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1]
    return dp[m - 1][n - 1]
''', [((3, 7), 28), ((3, 2), 3), ((1, 1), 1), ((10, 10), 48620)],
      'First row and first column are all 1. Every other cell is the cell above plus the cell to the left.', lc=62, slug='unique-paths', diff='M'),
    F('lcs', 'Longest common subsequence', 'Return the length of the longest subsequence that both strings share.', '''
def longest_common_subsequence(text1, text2):
    n, m = len(text1), len(text2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]
''', [(('abcde', 'ace'), 3), (('abc', 'abc'), 3), (('abc', 'def'), 0), (('bsbininm', 'jmjkbkjkv'), 1)],
      'A `(n + 1) × (m + 1)` table. Same letters: diagonal + 1. Otherwise the max of up and left.', lc=1143, slug='longest-common-subsequence', diff='M'),
    F('house-robber-2', 'House robber II (houses in a circle)', 'Same as House robber, but the first and last houses are neighbours.', '''
def rob_circle(nums):
    def line(arr):
        prev2 = prev1 = 0
        for x in arr:
            prev2, prev1 = prev1, max(prev1, prev2 + x)
        return prev1
    if len(nums) == 1:
        return nums[0]
    return max(line(nums[1:]), line(nums[:-1]))
''', [(([2, 3, 2],), 3), (([1, 2, 3, 1],), 4), (([1, 2, 3],), 3), (([5],), 5), (([1, 2],), 2)],
      'Run normal House Robber twice: without the first house, and without the last house. Take the max. One house is a special case.', lc=213, slug='house-robber-ii', diff='M'),
  ],
},
# ---------------------------------------------------------------- Mock
{
  'id': 'mock', 'n': 8, 'title': 'Mock test',
  'goal': 'Three questions in the two styles you may meet: read input and print, or complete a function. Give yourself 45 minutes, no hints.',
  'map': [
    ('read n, then n numbers', 'n = int(input())\nnums = list(map(int, input().split()))'),
    ('read until the end of input', 'import sys\ndata = sys.stdin.read().split()'),
    ('print numbers with spaces', 'print(*nums)   or   print(" ".join(map(str, nums)))'),
    ('print with 2 decimals', 'print(f"{x:.2f}")'),
  ],
  'examples': [
    {'title': 'Reading everything at once (fast input)', 'stdin': '3\n4 5 6\n', 'src': '''import sys
data = sys.stdin.read().split()
n = int(data[0])
nums = list(map(int, data[1:1 + n]))
print(*nums)
print(f"{sum(nums) / n:.2f}")
'''},
  ],
  'traps': [
    'Read the question twice: is it "complete the function" (return the answer) or "read input and print"?',
    'Print exactly what is asked: no extra words, no extra spaces.',
    'Check the edge cases: one element, all equal, negative numbers, empty answers.',
  ],
  'problems': [
    S('above-average', 'Above average', 'The first line has `n`, the second line `n` numbers. Print how many numbers are strictly greater than their average.', '''
n = int(input())
nums = list(map(int, input().split()))
avg = sum(nums) / n
print(sum(1 for x in nums if x > avg))
''', [('5\n1 2 3 4 5\n', '2'), ('3\n5 5 5\n', '0'), ('4\n10 -10 3 1\n', '2'), ('1\n7\n', '0')],
      'Average is `sum(nums) / n`. Count the numbers `x > avg`.'),
    S('best-day', 'Best day to sell', 'The first line has `n`, the second line the share price on each of `n` days. Buy on one day and sell on a later day. Print the largest profit, or `0`.', '''
n = int(input())
prices = list(map(int, input().split()))
low = prices[0]
best = 0
for p in prices:
    low = min(low, p)
    best = max(best, p - low)
print(best)
''', [('6\n7 1 5 3 6 4\n', '5'), ('5\n7 6 4 3 1\n', '0'), ('2\n1 2\n', '1'), ('1\n5\n', '0')],
      'Keep the lowest price so far; the best profit today is `price - lowest`.', diff='E'),
    F('count-pairs', 'Count pairs with a given sum', 'Return how many index pairs `i < j` have `nums[i] + nums[j] == k`.', '''
def count_pairs(nums, k):
    seen = {}
    count = 0
    for x in nums:
        count += seen.get(k - x, 0)
        seen[x] = seen.get(x, 0) + 1
    return count
''', [(([1, 5, 7, -1], 6), 2), (([1, 1, 1, 1], 2), 6), (([1, 2, 3], 10), 0), (([3, 3, 3], 6), 3)],
      'For each x, every earlier number equal to `k - x` makes a pair. Count earlier numbers in a dict.', diff='M'),
  ],
},
]
