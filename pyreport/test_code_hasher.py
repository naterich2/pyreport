"""
Defines the unit tests for the code hasher.
"""
import code_hasher as C
import unittest

testsuite = unittest.TestSuite()
testloader = unittest.TestLoader()
load_test = lambda t: testsuite.addTest(
               testloader.loadTestsFromTestCase(t))

def line_signature(line_object):
    return (line_object.string, line_object.end_row, line_object.options)

def line_list_signature(line_list):
    signature = [line_signature(line) for line in line_list]
    if signature[-1][0] == '':
        signature.pop()
    return signature


########################################################################
# Test the separation in logical lines

class TestCodeLines(unittest.TestCase):

    def check_signature(self, in_string, signature):
        H = C.CodeHasher(C.xreadlines(in_string))
        code_line_list = [l for l in H.yieldcodelines()]
        signature2 = line_list_signature(code_line_list)
        self.assertEqual(signature, signature2)

    def test_lines(self):
        self.check_signature('a\na', [('a\n', 1, {}), ('a\n', 2, {})])

    def test_comments(self):
        self.check_signature('a\n#a\na', [('a\n', 1, {}), ('#a\na\n', 3,
                    {})])

    def test_options(self):
        self.check_signature('a\n#pyreport -n\n', 
                        [('a\n', 1, {}), ('#pyreport -n\n', 2, {})])


########################################################################
# Test the separation in code blocks

class TestIterBlock(unittest.TestCase):

    def is_single_block(self, string):
        codeblock = C.CodeBlock(0)
        codeblock.string = ''.join(C.xreadlines(string))
        block_list = list( C.iterblocks(C.xreadlines(string)) )
        self.assertEqual(line_list_signature([codeblock]), 
                         line_list_signature(block_list))

    def test_empty(self):
        self.is_single_block("a")
    
    def test_comment_in_block(self):
        self.is_single_block("""
if 1:
    print "a"
    # foo

# foo

    print "b"
""")

    def test_double_blank_line(self):
        self.is_single_block("""
if 1:
    a = (1, 
           4)
                        

    a""")


    def test_indented_comment(self):
        self.is_single_block("""
if 1:

    # Comment

    a""")

    def test_function_declaration(self):
        self.is_single_block("def foo():\n foo")

    def test_tabbed_block(self):
        self.is_single_block("def foo():\n\tfoo")

    def test_decorator(self):
        self.is_single_block("@staticmethod\ndef foo():\n foo")

load_test(TestIterBlock)

########################################################################
if __name__ == "__main__" :
    unittest.TextTestRunner().run(testsuite)
