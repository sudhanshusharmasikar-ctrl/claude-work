# Course content: Python for DSA, for someone who already solves DSA in C++.
# Every code block is run by build.py; the page shows the real output.
# Every quiz answer is checked by running the quiz code.

def P(n, t, d):
    slug = t.lower()
    for ch in "()'?,.":
        slug = slug.replace(ch, '')
    return {'n': n, 't': t, 'd': d, 's': '-'.join(slug.split())}

LESSONS = [
{
  'id': 'basics', 'title': 'Python basics for a C++ coder',
  'intro': 'Your logic stays the same. Only the syntax changes: no semicolons, no braces, no types. Indentation is the block.',
  'map': [
    ('int x = 5;', 'x = 5'),
    ('long long big = 1e18;', 'big = 10**18          # ints never overflow'),
    ('a / b   (both int)', 'a // b                # floor division; a / b gives a float'),
    ('x++;  x--;', 'x += 1;  x -= 1        # there is no ++'),
    ('&&   ||   !', 'and   or   not'),
    ('if (a) {} else if (b) {} else {}', 'if a: ... elif b: ... else: ...'),
    ('for (int i = 0; i < n; i++)', 'for i in range(n):'),
    ('for (int i = n - 1; i >= 0; i--)', 'for i in range(n - 1, -1, -1):'),
    ('while (x > 0) {}', 'while x > 0:'),
    ('cout << a << " " << b << endl;', 'print(a, b)'),
    ('cin >> n;', 'n = int(input())'),
    ('swap(a, b);', 'a, b = b, a'),
    ('int f(int a, int b) { ... }', 'def f(a, b): ...'),
    ('true  false  NULL', 'True  False  None'),
    ('INT_MAX', "float('inf')"),
  ],
  'code': [
    {'title': 'Numbers, loops, functions', 'src': r'''n = 7
print(n // 2, n % 2, n / 2)     # floor division, remainder, true division
print(2 ** 100)                 # no overflow, ever
a, b = 3, 5
a, b = b, a                     # swap in one line
print(a, b)
for i in range(5, 0, -1):       # 5 down to 1
    print(i, end=' ')
print()
total = 0
for x in [4, 8, 15]:
    total += x
print(f"total = {total}")       # f-string: values inside {}

def add(x, y=10):               # y has a default value
    return x + y
print(add(5), add(5, 1))
if total > 20 and not total % 2:
    print("big and even")
elif total > 20:
    print("big and odd")
'''},
    {'title': 'Reading input (when the test gives you stdin)', 'stdin': '5\n4 1 3 9 2\nhello\n', 'src': r'''n = int(input())                        # first line: 5
arr = list(map(int, input().split()))   # second line: 4 1 3 9 2
s = input().strip()                     # third line: hello
print(n, arr, s)
print(max(arr), min(arr), sum(arr), len(arr))
'''},
  ],
  'watch': [
    'Indentation is the block. Use 4 spaces, the same everywhere; a wrong indent is an error or a bug.',
    '`/` always gives a float: `7 / 2` is `3.5`. Use `//` for integer division.',
    '`range(a, b)` stops before `b`, exactly like `i < b`.',
  ],
  'quiz': [
    {'code': 'print(7 // 2, 7 / 2)', 'options': ['3 3', '3 3.5', '3.5 3.5', '3 4'], 'answer': '3 3.5', 'why': '`//` is integer division, `/` always returns a float.'},
    {'code': 'for i in range(1, 10, 3):\n    print(i, end=" ")', 'options': ['1 4 7', '1 4 7 10', '1 3 6 9', '3 6 9'], 'answer': '1 4 7', 'why': 'Start 1, step 3, stop before 10.'},
    {'code': 'x = 5\nprint(++x)', 'options': ['6', '5', 'SyntaxError', '4'], 'answer': '5', 'why': 'Python has no `++`. `++x` is just plus-plus-x, so it stays 5, and x is not changed.'},
    {'code': 'a, b = 1, 2\na, b = b, a + b\nprint(a, b)', 'options': ['2 3', '2 4', '1 3', '2 2'], 'answer': '2 3', 'why': 'The right side is computed first with the old values (2, 1 + 2), then assigned.'},
  ],
  'practice': [P(412, 'Fizz Buzz', 'E'), P(9, 'Palindrome Number', 'E'), P(1480, 'Running Sum of 1d Array', 'E'),
               P(1342, 'Number of Steps to Reduce a Number to Zero', 'E'), P(1295, 'Find Numbers with Even Number of Digits', 'E'), P(7, 'Reverse Integer', 'M')],
  'drill': {'task': 'Read n, then n numbers on one line. Print their sum and the largest number.',
            'src': 'n = int(input())\nnums = list(map(int, input().split()))\nprint(sum(nums), max(nums))\n',
            'stdin': '4\n3 9 1 5\n', 'expect': '18 9'},
},
{
  'id': 'lists', 'title': 'Lists: the dynamic array (your vector)',
  'intro': 'A Python list is a C++ vector: one block of memory holding references, which grows by itself when it fills up.',
  'map': [
    ('vector<int> v;', 'v = []'),
    ('vector<int> v(n, 0);', 'v = [0] * n'),
    ('v.push_back(x);', 'v.append(x)'),
    ('v.pop_back();', 'v.pop()               # also returns the value'),
    ('v.size()', 'len(v)'),
    ('v.back()   v.front()', 'v[-1]   v[0]'),
    ('v.insert(v.begin() + i, x);', 'v.insert(i, x)'),
    ('v.erase(v.begin() + i);', 'v.pop(i)   or   del v[i]'),
    ('sort(v.begin(), v.end());', 'v.sort()              # sorted(v) returns a new list'),
    ('sort(..., greater<int>());', 'v.sort(reverse=True)'),
    ('reverse(v.begin(), v.end());', 'v.reverse()   or   v[::-1] (new list)'),
    ('*max_element(...)  accumulate(...)', 'max(v)   sum(v)'),
    ('find(v.begin(), v.end(), x) != v.end()', 'x in v'),
    ('vector<int> b = a;   (a copy)', 'b = a[:]   or   b = a.copy()     # b = a is NOT a copy'),
  ],
  'code': [
    {'title': 'Everyday list work', 'src': r'''v = [5, 2, 9]
v.append(4)              # [5, 2, 9, 4]
v.insert(0, 7)           # [7, 5, 2, 9, 4]
last = v.pop()           # removes and returns 4
print(v, last, len(v), v[-1])
print(v[1:3], v[:2], v[::-1])     # slices are new lists
v.sort()
print(v, sorted(v, reverse=True))
squares = [x * x for x in range(5)]            # list comprehension
evens = [x for x in squares if x % 2 == 0]
print(squares, evens)
for i, x in enumerate(['a', 'b', 'c']):        # index and value together
    print(i, x, end=' | ')
print()
for x, y in zip([1, 2, 3], [10, 20, 30]):      # two lists side by side
    print(x + y, end=' ')
print()
a = [1, 2, 3]
b = a          # same list, two names
c = a[:]       # a real copy
b.append(4)
print(a, c)
'''},
    {'title': 'How the dynamic array grows', 'note': 'Your numbers can differ by Python version. The point: memory grows in jumps, so append is amortized O(1), like vector::push_back.', 'src': r'''import sys
v = []
last = sys.getsizeof(v)
print(f"len={len(v):2}  bytes={last}")
for i in range(20):
    v.append(i)
    size = sys.getsizeof(v)
    if size != last:              # only print when the list had to grow
        print(f"len={len(v):2}  bytes={size}")
        last = size
'''},
    {'title': 'Build your own dynamic array (the interview answer)', 'note': 'Classes come properly in lesson 10; here, just follow the idea. A fixed block fills up, a block twice as big is made, everything is copied over. Copying is O(n) but happens rarely, so append is O(1) on average (amortized).', 'src': r'''class DynamicArray:
    def __init__(self):
        self.cap, self.n = 1, 0
        self.data = [None] * self.cap        # a fixed-size block
    def append(self, x):
        if self.n == self.cap:               # full: double the size and copy
            self.cap *= 2
            bigger = [None] * self.cap
            for i in range(self.n):
                bigger[i] = self.data[i]
            self.data = bigger
        self.data[self.n] = x
        self.n += 1
    def get(self, i):
        if not 0 <= i < self.n:
            raise IndexError("index out of range")
        return self.data[i]

arr = DynamicArray()
for x in [10, 20, 30, 40, 50]:
    arr.append(x)
    print(f"added {x}: size {arr.n}, capacity {arr.cap}")
print(arr.get(4))
'''},
  ],
  'watch': [
    'A list stores references in one block of memory. When it is full, Python allocates a bigger block (about 1.125 times plus a little) and copies, so `append` and `pop()` are O(1) on average.',
    '`pop(0)` and `insert(0, x)` shift every element: O(n). For a queue use `collections.deque` (lesson 7).',
    '`v.sort()` sorts in place and returns `None`. Never write `v = v.sort()`.',
  ],
  'quiz': [
    {'code': 'a = [1, 2, 3]\nb = a\nb.append(4)\nprint(a)', 'options': ['[1, 2, 3]', '[1, 2, 3, 4]', '[4]', 'Error'], 'answer': '[1, 2, 3, 4]', 'why': '`b = a` gives the same list a second name. Copy with `a[:]`.'},
    {'code': 'print([1, 2, 3, 4, 5][1:4])', 'options': ['[1, 2, 3, 4]', '[2, 3, 4]', '[2, 3, 4, 5]', '[1, 2, 3]'], 'answer': '[2, 3, 4]', 'why': 'Slice from index 1 up to, but not including, 4.'},
    {'code': 'print([3, 1, 2].sort())', 'options': ['[1, 2, 3]', 'None', '[3, 1, 2]', 'Error'], 'answer': 'None', 'why': '`.sort()` changes the list and returns None. `sorted()` returns a new list.'},
    {'code': 'v = [4, 5, 6]\nprint(v[-2], v[::-1])', 'options': ['5 [6, 5, 4]', '6 [6, 5, 4]', '5 [4, 5, 6]', 'Error'], 'answer': '5 [6, 5, 4]', 'why': 'Negative indexes count from the end; `[::-1]` is a reversed copy.'},
  ],
  'practice': [P(1929, 'Concatenation of Array', 'E'), P(26, 'Remove Duplicates from Sorted Array', 'E'), P(283, 'Move Zeroes', 'E'),
               P(121, 'Best Time to Buy and Sell Stock', 'E'), P(977, 'Squares of a Sorted Array', 'E'), P(88, 'Merge Sorted Array', 'E'), P(189, 'Rotate Array', 'M')],
  'drill': {'task': 'Move all zeros to the end in place, keeping the order of the other numbers (LeetCode 283).',
            'src': 'def move_zeroes(nums):\n    k = 0\n    for i in range(len(nums)):\n        if nums[i] != 0:\n            nums[k], nums[i] = nums[i], nums[k]\n            k += 1\n    return nums\n',
            'test': 'print(move_zeroes([0, 1, 0, 3, 12]))', 'expect': '[1, 3, 12, 0, 0]'},
},
{
  'id': 'matrix', 'title': '2D arrays (matrix)',
  'intro': 'A 2D array is a list of lists. One rule matters more than everything else here: build each row separately.',
  'map': [
    ('vector<vector<int>> g(n, vector<int>(m, 0));', 'g = [[0] * m for _ in range(n)]'),
    ('g[i][j]', 'g[i][j]'),
    ('g.size()   g[0].size()', 'len(g)   len(g[0])'),
    ('int dx[] = {-1, 1, 0, 0}, dy[] = {0, 0, -1, 1};', 'dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]'),
    ('transpose with two loops', '[list(r) for r in zip(*g)]'),
    ('rotate 90 degrees clockwise', '[list(r) for r in zip(*g[::-1])]'),
    ('if (r >= 0 && r < n && c >= 0 && c < m)', 'if 0 <= r < n and 0 <= c < m:'),
  ],
  'code': [
    {'title': 'Building a grid the right way (and the wrong way)', 'src': r'''n, m = 3, 4
grid = [[0] * m for _ in range(n)]   # right: 3 separate rows
grid[0][0] = 1
print(grid)
bad = [[0] * m] * n                  # wrong: 3 references to ONE row
bad[0][0] = 1
print(bad)
mat = [[1, 2, 3], [4, 5, 6]]
for row in mat:
    print(' '.join(map(str, row)))
print([list(r) for r in zip(*mat)])          # transpose
print([list(r) for r in zip(*mat[::-1])])    # rotate 90 degrees clockwise
print(sum(sum(row) for row in mat), max(max(row) for row in mat))
'''},
    {'title': 'Neighbours of a cell (grid problems)', 'src': r'''grid = ["#..",
        ".#.",
        "..."]
r, c = 1, 1
dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
for dr, dc in dirs:
    nr, nc = r + dr, c + dc
    if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
        print((nr, nc), grid[nr][nc])
'''},
    {'title': 'Reading a matrix from input', 'stdin': '2 3\n1 2 3\n4 5 6\n', 'src': r'''n, m = map(int, input().split())
mat = [list(map(int, input().split())) for _ in range(n)]
print(mat)
'''},
  ],
  'watch': [
    '`[[0] * m] * n` copies the same row n times. Changing one cell changes the whole column. Always use the `for _ in range(n)` form.',
    'Python allows chained comparisons: `0 <= r < n` is the bounds check in one go.',
    '`zip(*g)` gives tuples; wrap each in `list()` if you need to change the result.',
  ],
  'quiz': [
    {'code': 'g = [[0] * 2] * 2\ng[0][0] = 5\nprint(g)', 'options': ['[[5, 0], [0, 0]]', '[[5, 0], [5, 0]]', '[[5, 5], [0, 0]]', 'Error'], 'answer': '[[5, 0], [5, 0]]', 'why': 'Both rows are the same list object.'},
    {'code': 'g = [[0] * 2 for _ in range(2)]\ng[0][0] = 5\nprint(g)', 'options': ['[[5, 0], [0, 0]]', '[[5, 0], [5, 0]]', '[[5, 5], [0, 0]]', 'Error'], 'answer': '[[5, 0], [0, 0]]', 'why': 'Each row is built separately, so only one cell changes.'},
    {'code': 'm = [[1, 2], [3, 4]]\nprint([list(r) for r in zip(*m)])', 'options': ['[[1, 2], [3, 4]]', '[[1, 3], [2, 4]]', '[[4, 3], [2, 1]]', '[[3, 1], [4, 2]]'], 'answer': '[[1, 3], [2, 4]]', 'why': '`zip(*m)` pairs up the columns: that is the transpose.'},
    {'code': 'n = 3\nprint(0 <= 3 < n, 0 <= 2 < n)', 'options': ['True True', 'False True', 'True False', 'Error'], 'answer': 'False True', 'why': 'Chained comparison: 3 < 3 is False.'},
  ],
  'practice': [P(1672, 'Richest Customer Wealth', 'E'), P(118, "Pascal's Triangle", 'E'), P(867, 'Transpose Matrix', 'E'),
               P(48, 'Rotate Image', 'M'), P(54, 'Spiral Matrix', 'M'), P(73, 'Set Matrix Zeroes', 'M')],
  'drill': {'task': 'Rotate an n x n matrix 90 degrees clockwise, in place (LeetCode 48). Hint: transpose, then reverse each row.',
            'src': 'def rotate(mat):\n    n = len(mat)\n    for i in range(n):\n        for j in range(i + 1, n):\n            mat[i][j], mat[j][i] = mat[j][i], mat[i][j]\n    for row in mat:\n        row.reverse()\n    return mat\n',
            'test': 'print(rotate([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))', 'expect': '[[7, 4, 1], [8, 5, 2], [9, 6, 3]]'},
},
{
  'id': 'strings', 'title': 'Strings',
  'intro': 'Python strings work like C++ strings for reading, but you cannot change them in place. Build new strings instead.',
  'map': [
    ('string s = "abc";', 's = "abc"             # immutable'),
    ("s[i] = 'x';", "not allowed: use a list, then ''.join(...)"),
    ('s.size()', 'len(s)'),
    ('s.substr(i, k)', 's[i:i + k]'),
    ('reverse(s.begin(), s.end());', 's = s[::-1]'),
    ('s.find("ab")', 's.find("ab")          # -1 if not found'),
    ('s += c;   (inside a loop)', "parts.append(c), then ''.join(parts)"),
    ('stringstream ss(s); ss >> word', 'words = s.split()'),
    ('to_string(x)   stoi(s)', 'str(x)   int(s)'),
    ('isalpha(c)  isdigit(c)  tolower(c)', 'c.isalpha()  c.isdigit()  c.lower()'),
    ('s1 == s2,  s1 < s2', 's1 == s2,  s1 < s2     # same as C++'),
  ],
  'code': [
    {'title': 'String methods you will use in every problem', 'src': r'''s = "  Hello World  "
t = s.strip()
print(t, len(t), t.lower(), t.upper())
print(t.split(), t[::-1], t[0:5], t[-5:])
print(t.find("World"), t.find("xyz"), t.count("l"), t.replace("l", "L"))
print(t.startswith("He"), t.endswith("d"), "lo W" in t)
words = ["DSA", "in", "Python"]
print(" ".join(words), "-".join("abc"))
chars = list("hello")
chars[0] = 'j'                  # strings can't change, lists can
print("".join(chars))
print("abc" < "abd", "apple"[1:4], "ab" * 3)
for i, ch in enumerate("hey"):
    print(i, ch, end='  ')
print()
'''},
    {'title': 'Building strings and formatting output', 'src': r'''parts = []
for i in range(5):
    parts.append(str(i))
print(",".join(parts))
print(f"{3.14159:.2f} {42:05d} [{'ok':>5}] [{'ok':<5}]")
s = "A man, a plan, a canal: Panama"
clean = "".join(ch.lower() for ch in s if ch.isalnum())
print(clean, clean == clean[::-1])
'''},
  ],
  'watch': [
    '`s += c` in a loop builds a new string each time: O(n squared) in the worst case. Collect pieces in a list and `"".join` them once.',
    '`s.split()` with no argument splits on any run of spaces and drops empty pieces. `s.split(",")` keeps empty pieces.',
    'There is no separate `char` type: a character is a string of length 1.',
  ],
  'quiz': [
    {'code': 's = "python"\nprint(s[1:4], s[-1])', 'options': ['yth n', 'pyt n', 'yth o', 'ytho n'], 'answer': 'yth n', 'why': 'Indexes 1, 2, 3; and the last character.'},
    {'code': 's = "abc"\ns[0] = "z"', 'options': ['zbc', 'TypeError', 'abc', 'None'], 'answer': 'TypeError', 'why': 'Strings are immutable. Make a list, change it, join it.'},
    {'code': 'print("a,b,,c".split(","))', 'options': ["['a', 'b', 'c']", "['a', 'b', '', 'c']", "['a,b,,c']", 'Error'], 'answer': "['a', 'b', '', 'c']", 'why': 'Splitting on a given separator keeps the empty piece between the two commas.'},
    {'code': 'print("  a  b ".split())', 'options': ["['a', 'b']", "['', 'a', 'b', '']", "['  a  b ']", "['a', '', 'b']"], 'answer': "['a', 'b']", 'why': 'With no argument, split drops all extra spaces.'},
  ],
  'practice': [P(344, 'Reverse String', 'E'), P(125, 'Valid Palindrome', 'E'), P(58, 'Length of Last Word', 'E'),
               P(14, 'Longest Common Prefix', 'E'), P(680, 'Valid Palindrome II', 'E'), P(151, 'Reverse Words in a String', 'M')],
  'drill': {'task': 'Reverse the order of the words in a sentence, with single spaces between them (LeetCode 151).',
            'src': 'def reverse_words(s):\n    return " ".join(s.split()[::-1])\n',
            'test': 'print(reverse_words("  the sky   is blue "))', 'expect': 'blue is sky the'},
},
{
  'id': 'chars', 'title': 'Characters, ASCII and number conversions',
  'intro': "Python has no char arithmetic. `ord()` turns a character into its number, `chr()` turns a number back into a character. That covers every `c - 'a'` trick you use in C++.",
  'map': [
    ("char c = 'a';", "c = 'a'               # a 1-character string"),
    ('(int)c', 'ord(c)'),
    ('(char)65', 'chr(65)'),
    ("c - '0'   (digit to int)", "int(c)   or   ord(c) - ord('0')"),
    ("c - 'a'   (letter position)", "ord(c) - ord('a')"),
    ("'a' + 2", "chr(ord('a') + 2)"),
    ("i + '0'   (int 0-9 to digit)", "str(i)   or   chr(i + ord('0'))"),
    ('int cnt[26] = {0};', 'cnt = [0] * 26'),
    ("toupper(c)   tolower(c)", "c.upper()   c.lower()"),
    ('bitset<8>(n).to_string()', "bin(n)[2:]   or   format(n, '08b')"),
    ('stoi("ff", nullptr, 16)', "int('ff', 16)   int('1011', 2)"),
  ],
  'code': [
    {'title': 'ord, chr and char-to-int', 'note': "ASCII: 'A'-'Z' are 65-90, 'a'-'z' are 97-122, '0'-'9' are 48-57. Lowercase = uppercase + 32.", 'src': r'''print(ord('A'), ord('a'), ord('0'), chr(97), chr(ord('a') + 2))
c = '7'
print(int(c), ord(c) - ord('0'))          # both give 7
print(ord('d') - ord('a'))                # position in the alphabet: 3
print(chr(ord('a') + 25), chr(ord('G') + 32))
cnt = [0] * 26
for ch in "banana":
    cnt[ord(ch) - ord('a')] += 1
print([(chr(i + ord('a')), k) for i, k in enumerate(cnt) if k])
print('A'.lower(), 'b'.upper(), 'x'.isalpha(), '5'.isdigit(), 'a' <= 'k' <= 'z')
'''},
    {'title': 'Number and string conversions', 'src': r'''print(str(123) + "4", int("123") + 4, int("0042"))
print(bin(10), bin(10)[2:], int("1010", 2), int("ff", 16), hex(255), format(5, '08b'))
print(sum(int(d) for d in str(9875)))      # digit sum
num = 1234
digits = []
while num:
    digits.append(num % 10)
    num //= 10
print(digits[::-1])
print(int("".join(map(str, [4, 0, 7]))))   # digits back to a number
'''},
    {'title': 'A shift cipher: the classic ord/chr exercise', 'src': r'''def shift(s, k):
    out = []
    for ch in s:
        if 'a' <= ch <= 'z':
            out.append(chr((ord(ch) - ord('a') + k) % 26 + ord('a')))
        else:
            out.append(ch)
    return "".join(out)
print(shift("xyz abc", 3))
'''},
  ],
  'watch': [
    "`'9' + '1'` is `'91'` (joining strings), not 10. Convert first: `int('9') + int('1')`.",
    "`'a' + 1` is a TypeError. Use `chr(ord('a') + 1)`.",
    'Comparing characters works like C++: `\'a\' <= ch <= \'z\'` checks a lowercase letter.',
  ],
  'quiz': [
    {'code': "print(ord('b') - ord('a'), chr(ord('A') + 32))", 'options': ['1 a', '1 A', '98 a', '2 a'], 'answer': '1 a', 'why': 'Letters are consecutive; lowercase is uppercase + 32.'},
    {'code': "print('9' + '1', int('9') + int('1'))", 'options': ['10 10', '91 10', '91 91', 'Error'], 'answer': '91 10', 'why': '+ on strings joins them; convert to int to add.'},
    {'code': "print(int('101', 2), bin(6)[2:])", 'options': ['5 110', '101 110', '5 0b110', '3 110'], 'answer': '5 110', 'why': "int(s, 2) reads binary; bin() adds a '0b' prefix that [2:] removes."},
    {'code': "print('a' + 1)", 'options': ['b', '98', 'TypeError', 'a1'], 'answer': 'TypeError', 'why': 'No char arithmetic in Python: use ord and chr.'},
  ],
  'practice': [P(709, 'To Lower Case', 'E'), P(387, 'First Unique Character in a String', 'E'), P(242, 'Valid Anagram', 'E'),
               P(415, 'Add Strings', 'E'), P(67, 'Add Binary', 'E'), P(171, 'Excel Sheet Column Number', 'E'), P(13, 'Roman to Integer', 'E')],
  'drill': {'task': 'Add two non-negative numbers given as strings, digit by digit, without converting the whole string with int() (LeetCode 415).',
            'src': "def add_strings(a, b):\n    i, j, carry, out = len(a) - 1, len(b) - 1, 0, []\n    while i >= 0 or j >= 0 or carry:\n        x = ord(a[i]) - ord('0') if i >= 0 else 0\n        y = ord(b[j]) - ord('0') if j >= 0 else 0\n        carry, d = divmod(x + y + carry, 10)\n        out.append(chr(d + ord('0')))\n        i, j = i - 1, j - 1\n    return ''.join(reversed(out))\n",
            'test': 'print(add_strings("456", "77"), add_strings("999", "1"))', 'expect': '533 1000'},
},
{
  'id': 'hashing', 'title': 'Hashing: dict, set, Counter',
  'intro': 'dict is your unordered_map and set is your unordered_set. Counter and defaultdict remove most of the counting boilerplate.',
  'map': [
    ('unordered_map<int, int> m;', 'm = {}   or   defaultdict(int)'),
    ('m[k]++;', 'm[k] = m.get(k, 0) + 1   or   cnt[k] += 1 with Counter'),
    ('m.count(k)', 'k in m'),
    ('m.erase(k);', 'del m[k]   or   m.pop(k)'),
    ('for (auto& [k, v] : m)', 'for k, v in m.items():'),
    ('unordered_set<int> s;  s.insert(x);', 's = set();  s.add(x)'),
    ('map<int,int> (sorted keys)', 'sorted(m.items())   when you need the order'),
    ('pair<int,int>', '(a, b)   a tuple; tuples can be dict keys, lists cannot'),
  ],
  'code': [
    {'title': 'Counting and grouping', 'src': r'''from collections import Counter, defaultdict
nums = [3, 1, 3, 2, 3, 1]
freq = {}
for x in nums:
    freq[x] = freq.get(x, 0) + 1
print(freq)
cnt = Counter(nums)
print(cnt[3], cnt[7], cnt.most_common(2))
groups = defaultdict(list)
for w in ["eat", "tea", "tan", "ate", "nat"]:
    groups[tuple(sorted(w))].append(w)
print(list(groups.values()))
seen = set()
for x in nums:
    if x in seen:
        print("first repeat:", x)
        break
    seen.add(x)
print({1, 2, 3} & {2, 3, 4}, {1, 2} | {5}, {1, 2, 3} - {2})
m = {"b": 2, "a": 5, "c": 1}
print(sorted(m), sorted(m.items(), key=lambda kv: kv[1]), max(m, key=m.get))
'''},
    {'title': 'Two Sum with a dict', 'src': r'''def two_sum(nums, target):
    pos = {}                         # value -> index
    for i, x in enumerate(nums):
        if target - x in pos:
            return [pos[target - x], i]
        pos[x] = i
print(two_sum([2, 7, 11, 15], 9), two_sum([3, 2, 4], 6))
'''},
  ],
  'watch': [
    '`m[k]` on a missing key raises KeyError. Use `m.get(k, 0)`, `k in m`, or a defaultdict.',
    'Only immutable things can be keys: numbers, strings, tuples. Turn a list into a tuple first.',
    'Since Python 3.7 a dict keeps insertion order. It is still not sorted; use `sorted()`.',
  ],
  'quiz': [
    {'code': "d = {}\nprint(d.get('x', 0))", 'options': ['0', 'None', 'KeyError', "'x'"], 'answer': '0', 'why': '.get returns the default when the key is missing.'},
    {'code': "d = {}\nprint(d['x'])", 'options': ['0', 'None', 'KeyError', "''"], 'answer': 'KeyError', 'why': 'Square brackets on a missing key raise KeyError.'},
    {'code': 'from collections import Counter\nc = Counter("abracadabra")\nprint(c["a"], c["z"])', 'options': ['5 0', '5 KeyError', '4 0', '5 None'], 'answer': '5 0', 'why': 'A Counter returns 0 for missing keys instead of failing.'},
    {'code': 'print(len({1, 1, 2, 2, 3}))', 'options': ['5', '3', '2', 'Error'], 'answer': '3', 'why': 'A set keeps one copy of each value.'},
  ],
  'practice': [P(1, 'Two Sum', 'E'), P(217, 'Contains Duplicate', 'E'), P(205, 'Isomorphic Strings', 'E'),
               P(49, 'Group Anagrams', 'M'), P(347, 'Top K Frequent Elements', 'M'), P(128, 'Longest Consecutive Sequence', 'M'), P(560, 'Subarray Sum Equals K', 'M')],
  'drill': {'task': 'Count subarrays whose sum equals k, using prefix sums and a dict (LeetCode 560).',
            'src': 'from collections import defaultdict\ndef subarray_sum(nums, k):\n    seen = defaultdict(int)\n    seen[0] = 1\n    total = count = 0\n    for x in nums:\n        total += x\n        count += seen[total - k]\n        seen[total] += 1\n    return count\n',
            'test': 'print(subarray_sum([1, 1, 1], 2), subarray_sum([1, 2, 3], 3))', 'expect': '2 2'},
},
{
  'id': 'stackqueue', 'title': 'Stack and queue',
  'intro': 'A list is already a stack. For a queue, use collections.deque: it adds and removes at both ends in O(1).',
  'map': [
    ('stack<int> st;  st.push(x);', 'st = [];  st.append(x)'),
    ('st.top()', 'st[-1]'),
    ('st.pop();', 'st.pop()              # returns the value too'),
    ('st.empty()', 'not st'),
    ('queue<int> q;  q.push(x);', 'q = deque();  q.append(x)'),
    ('q.front(); q.pop();', 'q.popleft()'),
    ('deque: push_front / pop_back', 'q.appendleft(x) / q.pop()'),
    ('q.size()', 'len(q)'),
  ],
  'code': [
    {'title': 'Stack, queue and the bracket check', 'src': r'''from collections import deque
st = []
for x in [1, 2, 3]:
    st.append(x)
print(st[-1], st.pop(), st, bool(st))
q = deque([1, 2])
q.append(3)
q.appendleft(0)
print(q.popleft(), q.pop(), list(q), len(q))

def valid(s):
    pair = {')': '(', ']': '[', '}': '{'}
    st = []
    for ch in s:
        if ch in pair:
            if not st or st.pop() != pair[ch]:
                return False
        else:
            st.append(ch)
    return not st
print(valid("({[]})"), valid("(]"), valid("(("))
'''},
    {'title': 'Monotonic stack and a sliding-window deque', 'src': r'''from collections import deque
def next_greater(nums):
    ans = [-1] * len(nums)
    st = []                       # indices; their values are decreasing
    for i, x in enumerate(nums):
        while st and nums[st[-1]] < x:
            ans[st.pop()] = x
        st.append(i)
    return ans
print(next_greater([2, 1, 2, 4, 3]))

def max_window(nums, k):
    dq, out = deque(), []         # indices; their values are decreasing
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out
print(max_window([1, 3, -1, -3, 5, 3, 6, 7], 3))
'''},
  ],
  'watch': [
    'Never use `list.pop(0)` as a queue: it moves every element. Use `deque.popleft()`.',
    '`st.pop()` on an empty list raises IndexError. Check `if st:` first, as you check `!st.empty()` in C++.',
    'An empty list, deque, dict, set or string is False in an `if`.',
  ],
  'quiz': [
    {'code': 'st = [1, 2, 3]\nst.pop()\nprint(st[-1], len(st))', 'options': ['2 2', '3 2', '2 3', '1 2'], 'answer': '2 2', 'why': 'pop removes 3; the top is now 2.'},
    {'code': 'from collections import deque\nq = deque([1, 2, 3])\nq.popleft()\nq.append(4)\nprint(list(q))', 'options': ['[2, 3, 4]', '[1, 2, 3, 4]', '[4, 2, 3]', '[1, 2, 3]'], 'answer': '[2, 3, 4]', 'why': 'popleft removes from the front, append adds at the back.'},
    {'code': 'st = []\nprint(not st, bool([0]))', 'options': ['True True', 'True False', 'False True', 'False False'], 'answer': 'True True', 'why': 'An empty list is False, so `not st` is True. A list holding 0 is not empty, so it is True.'},
    {'code': 'st = []\nst.pop()', 'options': ['None', 'IndexError', '0', '[]'], 'answer': 'IndexError', 'why': 'Popping an empty list fails. Check `if st:` first.'},
  ],
  'practice': [P(20, 'Valid Parentheses', 'E'), P(232, 'Implement Queue using Stacks', 'E'), P(225, 'Implement Stack using Queues', 'E'),
               P(496, 'Next Greater Element I', 'E'), P(933, 'Number of Recent Calls', 'E'), P(155, 'Min Stack', 'M'), P(739, 'Daily Temperatures', 'M'), P(239, 'Sliding Window Maximum', 'H')],
  'drill': {'task': 'Daily Temperatures (LeetCode 739): for each day, how many days until a warmer one? Use a monotonic stack.',
            'src': 'def daily_temperatures(t):\n    ans = [0] * len(t)\n    st = []\n    for i, x in enumerate(t):\n        while st and t[st[-1]] < x:\n            j = st.pop()\n            ans[j] = i - j\n        st.append(i)\n    return ans\n',
            'test': 'print(daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]))', 'expect': '[1, 1, 4, 2, 1, 1, 0, 0]'},
},
{
  'id': 'heapsort', 'title': 'Heap, sorting and binary search',
  'intro': 'heapq gives you a priority queue, `key=` replaces comparators, and bisect gives you lower_bound and upper_bound.',
  'map': [
    ('priority_queue<int, vector<int>, greater<int>> pq;', 'h = []  with heapq     # heapq is a MIN-heap'),
    ('priority_queue<int> pq;   (max-heap)', 'push -x, pop and negate back'),
    ('pq.push(x);', 'heapq.heappush(h, x)'),
    ('pq.top()', 'h[0]'),
    ('pq.pop();', 'heapq.heappop(h)      # returns the value'),
    ('make_heap(v.begin(), v.end());', 'heapq.heapify(v)'),
    ('sort(v.begin(), v.end(), cmp);', 'v.sort(key=lambda x: ...)   or   cmp_to_key(cmp)'),
    ('lower_bound(v.begin(), v.end(), x)', 'bisect.bisect_left(v, x)'),
    ('upper_bound(v.begin(), v.end(), x)', 'bisect.bisect_right(v, x)'),
  ],
  'code': [
    {'title': 'Heaps', 'src': r'''import heapq
h = []
for x in [5, 1, 8, 3]:
    heapq.heappush(h, x)
print(h[0], heapq.heappop(h), heapq.heappop(h))     # smallest first
maxh = [-x for x in [5, 1, 8, 3]]
heapq.heapify(maxh)
print(-heapq.heappop(maxh))                          # max-heap trick
print(heapq.nlargest(2, [5, 1, 8, 3]), heapq.nsmallest(2, [5, 1, 8, 3]))
tasks = []
heapq.heappush(tasks, (2, "write"))                  # tuples compare by first item
heapq.heappush(tasks, (1, "read"))
print(heapq.heappop(tasks))
'''},
    {'title': 'Sorting with keys and comparators, and binary search', 'src': r'''people = [("amit", 25), ("riya", 22), ("dev", 25)]
print(sorted(people, key=lambda p: (-p[1], p[0])))   # age high to low, then name
intervals = [[1, 3], [8, 10], [2, 6]]
intervals.sort(key=lambda iv: iv[0])
print(intervals)
from functools import cmp_to_key
nums = [3, 30, 34, 5, 9]
nums.sort(key=cmp_to_key(lambda x, y: -1 if str(x) + str(y) > str(y) + str(x) else 1))
print("".join(map(str, nums)))                       # largest number
from bisect import bisect_left, bisect_right
a = [1, 2, 4, 4, 4, 7]
print(bisect_left(a, 4), bisect_right(a, 4), bisect_left(a, 5))

def lower_bound(a, x):            # the same thing by hand
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo
print(lower_bound(a, 4), lower_bound(a, 8))
'''},
  ],
  'watch': [
    'heapq is always a min-heap. For a max-heap push `-x`; for pairs push `(-key, value)`.',
    'A comparator for `cmp_to_key` returns a negative number, 0 or a positive number, not True/False like C++.',
    '`(lo + hi) // 2` cannot overflow in Python, so you do not need `lo + (hi - lo) / 2`.',
  ],
  'quiz': [
    {'code': 'import heapq\nh = [3, 1, 2]\nheapq.heapify(h)\nprint(h[0])', 'options': ['3', '1', '2', 'Error'], 'answer': '1', 'why': 'heapify makes a min-heap; the smallest is at index 0.'},
    {'code': 'print(sorted(["bb", "a", "ccc"], key=len))', 'options': ["['a', 'bb', 'ccc']", "['ccc', 'bb', 'a']", "['bb', 'a', 'ccc']", "['a', 'ccc', 'bb']"], 'answer': "['a', 'bb', 'ccc']", 'why': 'key=len sorts by length.'},
    {'code': 'from bisect import bisect_left\nprint(bisect_left([1, 3, 5], 4))', 'options': ['1', '2', '3', '4'], 'answer': '2', 'why': 'The first index whose value is at least 4 is index 2.'},
    {'code': 'print(sorted([3, 1, 2], reverse=True))', 'options': ['[1, 2, 3]', '[3, 2, 1]', '[3, 1, 2]', 'None'], 'answer': '[3, 2, 1]', 'why': 'reverse=True sorts high to low.'},
  ],
  'practice': [P(704, 'Binary Search', 'E'), P(35, 'Search Insert Position', 'E'), P(703, 'Kth Largest Element in a Stream', 'E'),
               P(215, 'Kth Largest Element in an Array', 'M'), P(973, 'K Closest Points to Origin', 'M'), P(56, 'Merge Intervals', 'M'), P(179, 'Largest Number', 'M')],
  'drill': {'task': 'Kth largest element using a min-heap of size k (LeetCode 215).',
            'src': 'import heapq\ndef kth_largest(nums, k):\n    h = []\n    for x in nums:\n        heapq.heappush(h, x)\n        if len(h) > k:\n            heapq.heappop(h)\n    return h[0]\n',
            'test': 'print(kth_largest([3, 2, 1, 5, 6, 4], 2), kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4))', 'expect': '5 4'},
},
{
  'id': 'recursion', 'title': 'Recursion, backtracking and memo',
  'intro': 'Recursion is written the same way. The Python-specific parts are copying the path into the answer, `nonlocal`, and `@cache` for memoisation.',
  'map': [
    ('vector<vector<int>> res;', 'res = []'),
    ('res.push_back(path);   (copies)', 'res.append(path[:])   # must copy yourself'),
    ('global counter in recursion', 'nonlocal counter   inside a nested function'),
    ('unordered_map memo / dp array', '@cache   from functools'),
    ('deep recursion is fine in C++', 'sys.setrecursionlimit(10**6)   (default about 1000)'),
  ],
  'code': [
    {'title': 'Subsets and permutations', 'src': r'''def subsets(nums):
    res, path = [], []
    def dfs(i):
        if i == len(nums):
            res.append(path[:])          # copy, because path keeps changing
            return
        path.append(nums[i])             # take nums[i]
        dfs(i + 1)
        path.pop()                       # undo
        dfs(i + 1)                       # skip nums[i]
    dfs(0)
    return res
print(subsets([1, 2, 3]))

def permutations(nums):
    res, path, used = [], [], [False] * len(nums)
    def dfs():
        if len(path) == len(nums):
            res.append(path[:])
            return
        for i in range(len(nums)):
            if not used[i]:
                used[i] = True
                path.append(nums[i])
                dfs()
                path.pop()
                used[i] = False
    dfs()
    return res
print(permutations([1, 2, 3]))
'''},
    {'title': 'Memo with @cache, nonlocal, and the recursion limit', 'src': r'''from functools import cache
import sys

@cache
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
print(fib(90))

def count_calls(n):
    calls = 0
    def go(k):
        nonlocal calls           # change the outer variable
        calls += 1
        if k > 0:
            go(k - 1)
    go(n)
    return calls
print(count_calls(5))
print(sys.getrecursionlimit())
'''},
  ],
  'watch': [
    '`res.append(path)` stores a reference: every entry ends up as the same final list. Append `path[:]`.',
    'Assigning to an outer variable inside a nested function needs `nonlocal`, or you get UnboundLocalError. Changing a list with `.append` does not.',
    'Never use a mutable default like `def f(x, acc=[])`: the same list is shared between calls.',
  ],
  'quiz': [
    {'code': 'res, path = [], [1]\nres.append(path)\npath.append(2)\nprint(res)', 'options': ['[[1]]', '[[1, 2]]', '[1, 2]', '[]'], 'answer': '[[1, 2]]', 'why': 'res holds a reference to path, which changed afterwards.'},
    {'code': 'def outer():\n    c = 0\n    def inc():\n        c += 1\n    inc()\n    return c\nprint(outer())', 'options': ['1', '0', 'UnboundLocalError', 'None'], 'answer': 'UnboundLocalError', 'why': 'Assigning to c inside inc makes it local there. Add `nonlocal c`.'},
    {'code': 'def f(a, acc=[]):\n    acc.append(a)\n    return acc\nf(1)\nprint(f(2))', 'options': ['[2]', '[1, 2]', '[1]', 'Error'], 'answer': '[1, 2]', 'why': 'The default list is created once and shared by every call.'},
    {'code': 'def f(n):\n    return 1 if n == 0 else n * f(n - 1)\nprint(f(5))', 'options': ['120', '24', '5', 'RecursionError'], 'answer': '120', 'why': '5 * 4 * 3 * 2 * 1.'},
  ],
  'practice': [P(509, 'Fibonacci Number', 'E'), P(78, 'Subsets', 'M'), P(90, 'Subsets II', 'M'), P(46, 'Permutations', 'M'),
               P(39, 'Combination Sum', 'M'), P(22, 'Generate Parentheses', 'M'), P(17, 'Letter Combinations of a Phone Number', 'M')],
  'drill': {'task': 'Generate all valid combinations of n pairs of parentheses (LeetCode 22).',
            'src': 'def generate(n):\n    res = []\n    def go(cur, opened, closed):\n        if len(cur) == 2 * n:\n            res.append(cur)\n            return\n        if opened < n:\n            go(cur + "(", opened + 1, closed)\n        if closed < opened:\n            go(cur + ")", opened, closed + 1)\n    go("", 0, 0)\n    return res\n',
            'test': 'print(generate(3))', 'expect': "['((()))', '(()())', '(())()', '()(())', '()()()']"},
},
{
  'id': 'linkedlist', 'title': 'Classes and linked lists',
  'intro': 'LeetCode gives you the node class. You need to read it, build test lists, and walk pointers with `.next` instead of `->next`.',
  'map': [
    ('struct ListNode { int val; ListNode* next; };', 'class ListNode: with __init__(self, val=0, next=None)'),
    ('nullptr', 'None'),
    ('node->next', 'node.next'),
    ('new ListNode(5)', 'ListNode(5)'),
    ('this->val', 'self.val'),
    ('if (!head)', 'if not head:   or   if head is None:'),
    ('class MinStack { public: void push(int x) {...} };', 'class MinStack:  def push(self, x): ...'),
  ],
  'code': [
    {'title': 'Building, printing and reversing a list', 'src': r'''class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def build(values):
    dummy = ListNode()
    cur = dummy
    for v in values:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next

def to_list(head):
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out

def reverse(head):
    prev = None
    while head:
        nxt = head.next
        head.next = prev
        prev = head
        head = nxt
    return prev

def middle(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    return slow.val

head = build([1, 2, 3, 4, 5])
print(to_list(head), middle(head))
print(to_list(reverse(head)))
'''},
    {'title': 'Your own class: Min Stack', 'src': r'''class MinStack:
    def __init__(self):
        self.st = []                      # pairs of (value, minimum so far)
    def push(self, x):
        m = x if not self.st else min(x, self.st[-1][1])
        self.st.append((x, m))
    def pop(self):
        self.st.pop()
    def top(self):
        return self.st[-1][0]
    def getMin(self):
        return self.st[-1][1]

ms = MinStack()
for x in [5, 3, 7]:
    ms.push(x)
print(ms.getMin(), ms.top())
ms.pop()
ms.pop()
print(ms.getMin())
'''},
  ],
  'watch': [
    'Every method takes `self` as its first parameter, and fields are always written `self.name`.',
    'Objects are passed by reference, like pointers. `b = a` does not copy the node.',
    'Use `is None` / `is not None` to test for a missing node.',
  ],
  'quiz': [
    {'code': 'class A:\n    def __init__(self):\n        self.x = 1\na = A()\nb = a\nb.x = 9\nprint(a.x)', 'options': ['1', '9', 'Error', 'None'], 'answer': '9', 'why': 'a and b are the same object.'},
    {'code': 'print(None is None, None == 0, not None)', 'options': ['True False True', 'True True True', 'False False True', 'True False False'], 'answer': 'True False True', 'why': 'None is only equal to None, and it is False in an `if`.'},
    {'code': 'node = None\nprint(node.val)', 'options': ['None', '0', 'AttributeError', 'NullPointerException'], 'answer': 'AttributeError', 'why': 'Python’s version of dereferencing a null pointer.'},
    {'code': 'class P:\n    def hi(self):\n        return "hi"\nprint(P().hi())', 'options': ['hi', 'TypeError', 'None', 'P'], 'answer': 'hi', 'why': 'self is passed automatically when you call a method on an object.'},
  ],
  'practice': [P(206, 'Reverse Linked List', 'E'), P(21, 'Merge Two Sorted Lists', 'E'), P(876, 'Middle of the Linked List', 'E'),
               P(141, 'Linked List Cycle', 'E'), P(160, 'Intersection of Two Linked Lists', 'E'), P(19, 'Remove Nth Node From End of List', 'M'), P(2, 'Add Two Numbers', 'M')],
  'drill': {'task': 'Merge two sorted linked lists using a dummy node (LeetCode 21).',
            'src': 'class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val, self.next = val, next\n\ndef merge(a, b):\n    dummy = cur = ListNode()\n    while a and b:\n        if a.val <= b.val:\n            cur.next, a = a, a.next\n        else:\n            cur.next, b = b, b.next\n        cur = cur.next\n    cur.next = a or b\n    return dummy.next\n',
            'test': 'def build(v):\n    d = c = ListNode()\n    for x in v:\n        c.next = ListNode(x); c = c.next\n    return d.next\nh = merge(build([1, 2, 4]), build([1, 3, 4]))\nout = []\nwhile h:\n    out.append(h.val); h = h.next\nprint(out)', 'expect': '[1, 1, 2, 3, 4, 4]'},
},
{
  'id': 'trees', 'title': 'Binary trees',
  'intro': 'Tree code is almost line-for-line the same as C++. The new tools are deque for level order, float("inf") for bounds, and nonlocal or self for a running answer.',
  'map': [
    ('TreeNode* root', 'root: Optional[TreeNode]   (LeetCode signature)'),
    ('root->left', 'root.left'),
    ('queue<TreeNode*> q; q.push(root);', 'q = deque([root])'),
    ('INT_MIN / INT_MAX as bounds', "float('-inf') / float('inf')"),
    ('int ans; (member or global)', 'self.ans   or   nonlocal ans'),
    ('stack<TreeNode*> st;', 'st = []'),
  ],
  'code': [
    {'title': 'Build a tree, then the three must-know traversals', 'src': r'''from collections import deque
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def build(level):                  # from LeetCode's list form; None = no node
    if not level:
        return None
    it = iter(level)
    root = TreeNode(next(it))
    q = deque([root])
    while q:
        node = q.popleft()
        for side in ("left", "right"):
            v = next(it, None)
            if v is not None:
                child = TreeNode(v)
                setattr(node, side, child)
                q.append(child)
    return root

def inorder(node):
    return inorder(node.left) + [node.val] + inorder(node.right) if node else []

def depth(node):
    return 1 + max(depth(node.left), depth(node.right)) if node else 0

def level_order(root):
    res, q = [], deque([root] if root else [])
    while q:
        level = []
        for _ in range(len(q)):         # one level at a time
            node = q.popleft()
            level.append(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        res.append(level)
    return res

root = build([3, 9, 20, None, None, 15, 7])
print(inorder(root), depth(root), level_order(root))
'''},
    {'title': 'A running answer with nonlocal, bounds with infinity, iterative inorder', 'src': r'''from collections import deque
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right
root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))

def diameter(root):
    best = 0
    def height(node):
        nonlocal best
        if not node:
            return 0
        l, r = height(node.left), height(node.right)
        best = max(best, l + r)
        return 1 + max(l, r)
    height(root)
    return best

def is_bst(node, lo=float('-inf'), hi=float('inf')):
    if not node:
        return True
    return lo < node.val < hi and is_bst(node.left, lo, node.val) and is_bst(node.right, node.val, hi)

def inorder_iter(root):
    res, st, cur = [], [], root
    while cur or st:
        while cur:
            st.append(cur)
            cur = cur.left
        cur = st.pop()
        res.append(cur.val)
        cur = cur.right
    return res

print(diameter(root), is_bst(root), is_bst(TreeNode(2, TreeNode(1), TreeNode(3))))
print(inorder_iter(root))
'''},
    {'title': 'What a LeetCode answer looks like', 'run': False, 'note': 'LeetCode supplies TreeNode and Optional, so this runs only there. Paste it into problem 104.', 'src': r'''class Solution:
    def maxDepth(self, root: Optional[TreeNode]) -> int:
        if not root:
            return 0
        return 1 + max(self.maxDepth(root.left), self.maxDepth(root.right))
'''},
  ],
  'watch': [
    'Inside `class Solution`, call your own helpers as `self.helper(...)`, or define them inside the method.',
    'Use `float(\'inf\')` instead of INT_MAX; it is bigger than every number, including huge Python ints.',
    'For level order, loop `for _ in range(len(q))` so each pass handles exactly one level.',
  ],
  'quiz': [
    {'code': 'from collections import deque\nq = deque([1])\nq.extend([2, 3])\nprint(q.popleft(), len(q))', 'options': ['1 2', '3 2', '1 3', '2 2'], 'answer': '1 2', 'why': 'extend adds several items at the back; popleft takes the front.'},
    {'code': 'x = None\nprint(x or 5)', 'options': ['None', '5', 'True', 'Error'], 'answer': '5', 'why': '`a or b` gives b when a is falsy. Handy for `node.left or node.right`.'},
    {'code': "print(float('-inf') < -10**18, max(3, float('-inf')))", 'options': ['True 3', 'False 3', 'True -inf', 'Error'], 'answer': 'True 3', 'why': 'Minus infinity is smaller than every number.'},
    {'code': 'print([] + [1] + [])', 'options': ['[1]', '[[], 1, []]', 'Error', '[[1]]'], 'answer': '[1]', 'why': 'Adding lists joins them, which is why the one-line inorder works.'},
  ],
  'practice': [P(94, 'Binary Tree Inorder Traversal', 'E'), P(104, 'Maximum Depth of Binary Tree', 'E'), P(226, 'Invert Binary Tree', 'E'),
               P(543, 'Diameter of Binary Tree', 'E'), P(102, 'Binary Tree Level Order Traversal', 'M'), P(199, 'Binary Tree Right Side View', 'M'),
               P(236, 'Lowest Common Ancestor of a Binary Tree', 'M'), P(98, 'Validate Binary Search Tree', 'M')],
  'drill': {'task': 'Right side view of a binary tree (LeetCode 199): the last value of every level, using a deque.',
            'src': 'from collections import deque\nclass TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val, self.left, self.right = val, left, right\n\ndef right_view(root):\n    res, q = [], deque([root] if root else [])\n    while q:\n        for i in range(len(q)):\n            node = q.popleft()\n            if node.left: q.append(node.left)\n            if node.right: q.append(node.right)\n        res.append(node.val)\n    return res\n',
            'test': 'root = TreeNode(1, TreeNode(2, None, TreeNode(5)), TreeNode(3, None, TreeNode(4)))\nprint(right_view(root))', 'expect': '[1, 3, 4]'},
},
{
  'id': 'dp', 'title': 'Dynamic programming',
  'intro': 'DP tables are lists and lists of lists; top-down DP is a recursive function with @cache. Your recurrences do not change.',
  'map': [
    ('vector<int> dp(n + 1, 0);', 'dp = [0] * (n + 1)'),
    ('vector<vector<int>> dp(n, vector<int>(m, -1));', 'dp = [[-1] * m for _ in range(n)]'),
    ('memset(dp, -1, sizeof dp);', 'build it with -1 as above'),
    ('INT_MAX in a min-DP', "float('inf')"),
    ('memo table + recursion', '@cache on a nested function'),
    ('min({a, b, c})', 'min(a, b, c)'),
  ],
  'code': [
    {'title': 'Bottom-up: 1D and 2D tables', 'src': r'''def climb(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a
print([climb(n) for n in range(1, 8)])

def rob(nums):
    prev2 = prev1 = 0
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1
print(rob([2, 7, 9, 3, 1]))

def coin_change(coins, amount):
    dp = [0] + [float('inf')] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
print(coin_change([1, 2, 5], 11), coin_change([2], 3))

def lcs(a, b):
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
    {'title': 'Top-down with @cache, and 0/1 knapsack on one row', 'src': r'''from functools import cache
def unique_paths(m, n):
    @cache
    def go(r, c):
        if r == m - 1 or c == n - 1:
            return 1
        return go(r + 1, c) + go(r, c + 1)
    return go(0, 0)
print(unique_paths(3, 7))

def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False
    target = total // 2
    dp = [True] + [False] * target
    for x in nums:
        for s in range(target, x - 1, -1):    # backwards: each item used once
            dp[s] = dp[s] or dp[s - x]
    return dp[target]
print(can_partition([1, 5, 11, 5]), can_partition([1, 2, 3, 5]))
'''},
  ],
  'watch': [
    'The 2D table rule from lesson 3 again: `[[0] * m for _ in range(n)]`, never `[[0] * m] * n`.',
    '@cache on a function defined inside your method starts fresh for every test case, which is what you want on LeetCode.',
    'Deep top-down recursion can hit the recursion limit (about 1000). For big n, go bottom-up.',
  ],
  'quiz': [
    {'code': 'dp = [[0] * 3] * 2\ndp[1][2] = 7\nprint(dp[0][2])', 'options': ['0', '7', 'Error', 'None'], 'answer': '7', 'why': 'Both rows are the same list. The classic DP bug.'},
    {'code': "print(min(3, float('inf')), float('inf') + 1 == float('inf'))", 'options': ['3 True', 'inf True', '3 False', 'Error'], 'answer': '3 True', 'why': 'Infinity plus anything is still infinity.'},
    {'code': 'a, b = 1, 1\nfor _ in range(3):\n    a, b = b, a + b\nprint(a)', 'options': ['2', '3', '5', '8'], 'answer': '3', 'why': '(1,1) → (1,2) → (2,3) → (3,5).'},
    {'code': 'print(max([1, 5, 2], default=0), max([], default=0))', 'options': ['5 0', '5 Error', '2 0', '5 None'], 'answer': '5 0', 'why': 'default= avoids a ValueError on an empty list.'},
  ],
  'practice': [P(70, 'Climbing Stairs', 'E'), P(198, 'House Robber', 'M'), P(322, 'Coin Change', 'M'), P(62, 'Unique Paths', 'M'),
               P(64, 'Minimum Path Sum', 'M'), P(1143, 'Longest Common Subsequence', 'M'), P(300, 'Longest Increasing Subsequence', 'M'), P(416, 'Partition Equal Subset Sum', 'M')],
  'drill': {'task': 'Longest Increasing Subsequence in O(n log n) with bisect (LeetCode 300).',
            'src': 'from bisect import bisect_left\ndef lis(nums):\n    tails = []\n    for x in nums:\n        i = bisect_left(tails, x)\n        if i == len(tails):\n            tails.append(x)\n        else:\n            tails[i] = x\n    return len(tails)\n',
            'test': 'print(lis([10, 9, 2, 5, 3, 7, 101, 18]), lis([7, 7, 7]))', 'expect': '4 1'},
},
{
  'id': 'gotchas', 'title': 'C++ habits that break in Python, and a timed mock',
  'intro': 'The last day: the differences that cause wrong answers, how to print and read fast, and a 45-minute mock in Python only.',
  'map': [
    ('-7 / 2 == -3', '-7 // 2 == -4;   int(-7 / 2) == -3'),
    ('-7 % 3 == -1', '-7 % 3 == 2'),
    ('int overflow', 'never happens (but huge numbers are slower)'),
    ("char + int", "TypeError: use chr(ord(c) + k)"),
    ('vector b = a;  copies', 'b = a  shares; copy with a[:]'),
    ('fast cin', 'data = sys.stdin.read().split()'),
    ('cout with spaces', 'print(*arr)   or   " ".join(map(str, arr))'),
    ('comparator returning bool', 'key=... or cmp_to_key returning -1 / 0 / 1'),
  ],
  'code': [
    {'title': 'Differences that give wrong answers', 'src': r'''print(-7 // 2, int(-7 / 2), -7 % 3)
arr = [3, 1, 2]
print(*arr)
print(*arr, sep=",")
print(" ".join(map(str, arr)))
x = 0.1 + 0.2
print(x == 0.3, abs(x - 0.3) < 1e-9)
print(round(2.5), round(3.5), round(2.567, 2))   # halves go to the even number
print(10 ** 20 + 1)
def add_item(x, bucket=None):        # the safe way to default to a list
    if bucket is None:
        bucket = []
    bucket.append(x)
    return bucket
print(add_item(1), add_item(2))
print(any(v > 2 for v in arr), all(v > 0 for v in arr), sum(1 for v in arr if v % 2))
'''},
    {'title': 'Reading everything at once (fast input)', 'stdin': '4\n1 2 3 4\n', 'src': r'''import sys
data = sys.stdin.read().split()
n = int(data[0])
nums = list(map(int, data[1:1 + n]))
print(sum(nums))
'''},
    {'title': 'A "complete the function" question', 'src': r'''def solution(arr):
    # Return the second largest distinct value, or -1 if there is none.
    distinct = sorted(set(arr), reverse=True)
    return distinct[1] if len(distinct) > 1 else -1
print(solution([4, 9, 2, 9, 7]), solution([5, 5]))
'''},
  ],
  'watch': [
    'Many online assessments give you a function to complete; others read from standard input. Practise both forms before your test.',
    '`round()` rounds halves to the even number: `round(2.5)` is 2. If the question says round half up, use `int(x + 0.5)` for positive numbers.',
    'Python is slower than C++. Prefer built-ins (`sum`, `max`, `sorted`, `Counter`) over hand-written loops when the limits are big.',
  ],
  'quiz': [
    {'code': 'print(-7 % 3, int(-7 / 2))', 'options': ['2 -3', '-1 -3', '2 -4', '-1 -4'], 'answer': '2 -3', 'why': 'Python % follows the sign of the divisor; int() of a float cuts toward zero.'},
    {'code': 'print(*[1, 2, 3], sep="-")', 'options': ['1-2-3', '[1, 2, 3]', '1 2 3', '-1-2-3-'], 'answer': '1-2-3', 'why': '`*` spreads the list into separate arguments.'},
    {'code': 'print(0.1 + 0.2 == 0.3)', 'options': ['True', 'False', 'Error', '0.3'], 'answer': 'False', 'why': 'Floating point, same as C++. Compare with a small tolerance.'},
    {'code': 'print(round(2.5), round(3.5))', 'options': ['3 4', '2 4', '2 3', '3 3'], 'answer': '2 4', 'why': 'Python rounds halves to the nearest even number.'},
  ],
  'practice': [P(1365, 'How Many Numbers Are Smaller Than the Current Number', 'E'), P(1748, 'Sum of Unique Elements', 'E'),
               P(3, 'Longest Substring Without Repeating Characters', 'M'), P(238, 'Product of Array Except Self', 'M')],
  'practiceNote': 'Timed mock: set 45 minutes and solve two of these in Python with no notes, then the other two the same way.',
  'drill': {'task': 'Read T test cases from standard input. Each has n and then n numbers. Print the largest number of each test case.',
            'src': 'import sys\ndata = sys.stdin.read().split()\nt = int(data[0])\ni = 1\nfor _ in range(t):\n    n = int(data[i]); i += 1\n    arr = list(map(int, data[i:i + n])); i += n\n    print(max(arr))\n',
            'stdin': '2\n3\n4 9 2\n2\n-5 -1\n', 'expect': '9\n-1'},
},
]
