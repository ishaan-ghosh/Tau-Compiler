from tau import tokens, error
from tau.tokens import Span, Coord, Token, punctuation, keywords
import string


class Scanner:
    tokens: list
    tokIndex: int

    def __init__(self, input: str):
        lineCount = 0
        colCount = 0
        lines = input.splitlines()
        tokList = []
        for line in lines:
            lineCount += 1
            colCount = 0
            curTok = ""
            for char in line:
                colCount += 1
                if char == "/" and line[colCount] == "/":
                    break
                if colCount > 1 and char.isalpha() and line[colCount - 2].isdigit():
                    # If an INT and ID are not seperated by whitespace
                    tokList, curTok = self.__tokenGen(
                        colCount, lineCount, curTok, tokList
                    )
                    curTok = "" + char
                    continue
                elif char in punctuation or char == "!":
                    # Generate token from before punction
                    tokList, curTok = self.__tokenGen(
                        colCount, lineCount, curTok, tokList
                    )
                    if colCount > 1:
                        chBac = line[colCount - 2]
                    else:
                        chBac = ""
                    if colCount < len(line):
                        chFro = line[colCount]
                    else:
                        chFro = ""
                    if char == "=":
                        # Check char behind
                        if chBac == "!" or chBac == ">" or chBac == "<" or chBac == "=":
                            continue
                        # Check char in front
                        elif chFro == "=":
                            # Create "==" token
                            tokList, curTok = self.__tokenGen(
                                colCount + 2, lineCount, "==", tokList
                            )
                        # If this is just an =, create token
                        else:
                            tokList, curTok = self.__tokenGen(
                                colCount + 1, lineCount, "=", tokList
                            )
                    elif char == "!":
                        # Check char in front
                        if chFro == "=":
                            tokList, curTok = self.__tokenGen(
                                colCount + 2, lineCount, "!=", tokList
                            )
                    elif char == ">":
                        # Check char in front
                        if chFro == "=":
                            tokList, curTok = self.__tokenGen(
                                colCount + 2, lineCount, ">=", tokList
                            )
                        else:
                            tokList, curTok = self.__tokenGen(
                                colCount + 1, lineCount, ">", tokList
                            )
                    elif char == "<":
                        # Check char in front
                        if chFro == "=":
                            tokList, curTok = self.__tokenGen(
                                colCount + 2, lineCount, "<=", tokList
                            )
                        else:
                            tokList, curTok = self.__tokenGen(
                                colCount + 1, lineCount, "<", tokList
                            )
                    else:
                        tokList, curTok = self.__tokenGen(
                            colCount + 1, lineCount, char, tokList
                        )
                        pass
                elif char not in string.whitespace:
                    curTok += char
                else:
                    # If we have a full token, generate it and append to tokList
                    tokList, curTok = self.__tokenGen(
                        colCount, lineCount, curTok, tokList
                    )
            # Generate and append end of line token to tokList
            tokList, curTok = self.__tokenGen(colCount + 1, lineCount, curTok, tokList)
        # Generate and append end of file token to tokList
        if len(input) == 0:
            # If empty file, set coords of EOF token to 1,1
            lineCount += 1
            colCount += 1
        elif len(input) > 0 and input[-1] == "\n":
            # If not empty file, and last character in file is new line
            colCount = 1
            lineCount += 1
        else:
            colCount += 1
        eofCoord = Coord(col=colCount, line=lineCount)
        eofSpan = Span(start=eofCoord, end=eofCoord)
        eofTok = Token("EOF", "", eofSpan)
        tokList.append(eofTok)
        self.tokens = tokList
        self.tokIndex = 0

    def peek(self) -> Token:
        return self.tokens[self.tokIndex]

    def consume(self) -> Token:
        ret = self.tokens[self.tokIndex]
        self.tokIndex += 1
        return ret

    def __tokenGen(self, colCount, lineCount, curTok, tokList):
        end = Coord(col=colCount, line=lineCount)
        curLen = colCount - len(curTok)
        start = Coord(col=curLen, line=lineCount)
        curSpan = Span(start=start, end=end)
        if curTok == "":
            return tokList, curTok
        elif curTok in keywords:
            newTok = Token(curTok, curTok, curSpan)
            tokList.append(newTok)
            curTok = ""
        elif curTok in punctuation:
            newTok = Token(curTok, curTok, curSpan)
            tokList.append(newTok)
            curTok = ""
        elif curTok.isdigit():
            # Do INT work
            newTok = Token("INT", curTok, curSpan)
            tokList.append(newTok)
            curTok = ""
        elif curTok.isalnum():
            # Do ID work
            newTok = Token("ID", curTok, curSpan)
            tokList.append(newTok)
            curTok = ""
        else:
            error.error("Found token not part of language", curSpan)
        return tokList, curTok


# with open("/Users/ish/Documents/Code/CSC 453/Project Milestone 1/project-ish-anghosh/tau/tests/m4/test2.tau", "r") as file:
#     tc1 = file.read()

# scan = Scanner(tc1)

# print(scan.tokens)

# for tok in scan.tokens:
#     print(tok)
