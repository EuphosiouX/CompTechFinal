from token import Token

# Storing declared variables
var = []

# Parser
class Parse:   
    def __init__ (self, s):
        # string input
        self.s = s 
        # token object
        self.t = Token(self.s)

    
    # Main entry point
    def parsee(self):     
        # checker for blocks
        self.blockChecker = 0
        # block checker flag 
        self.lookahead = self.t.getNextToken('parse')
        return self.program()

    def program(self):
        ast = {
            'type': 'Program',
            'body': self.statementList()
        }
        return ast
    
    def statementList(self, blockStatementStopper = None):
        # If it is one statement
        statementList = []
        
        if self.lookahead.get('type') != 'block':
            statementList = [self.statement()]

        # If checking for block statement
        if blockStatementStopper != None:
        #     while (self.lookahead != None and self.lookahead.get('type') == blockStatementStopper):
        #         self.eat('block')
        #         tempBlockChecker += 1
        #     print(tempBlockChecker, self.blockChecker, self.lookahead)
        #     if tempBlockChecker < self.blockChecker:
        #         return statementList
        #     elif tempBlockChecker == self.blockChecker:
        #         print(self.lookahead)
        #         statementList.append(self.statement()) 
        #     else:
        #         raise SyntaxError("Unmatched Indent")

            # While not reached end of file and there is indentation
            while (self.lookahead != None and self.lookahead.get('type') == blockStatementStopper):
                tempBlockChecker = 0
                # blockChecker is updated everytime a statement that requires
                # indentation is called
                # Loop through the indentation based on the correct indentation
                print("selfblock", self.blockChecker)
                for i in range(self.blockChecker):
                    self.eat("block")
                    # Track how many loop there is currently
                    tempBlockChecker += 1
                    # If next token is not block anymore, break
                    if self.lookahead.get('type') != 'block':
                        break
                # If tempBlockChecker < the correct indentation, there are 2 possibilities
                # 1. Another if statement is called
                # 2. A syntax error
                if tempBlockChecker < self.blockChecker:
                    # If it is if statement
                    if self.lookahead.get('type') == 'special':
                        # Change current indentation to match
                        self.blockChecker = tempBlockChecker
                        return statementList
                    # Else
                    else:
                        raise SyntaxError("Unmatched Indent")
                
                # If there is still block, raise an indentation error
                if self.lookahead.get('type') == "block":
                    raise SyntaxError("Unmatched Indent")
                
                # Add statement to statement list      
                statementList.append(self.statement())    
                
        else:
            # If it is multiple statement
            # While we still have tokens, continue to loop (stop if cursor exceeds token)
            while (self.lookahead != None):
                # Append to list
                statementList.append(self.statement()) 
        return statementList
    
    def statement(self):
        # if self.lookahead.get('type') == "block":
        #     return self.blockStatement()
        if self.lookahead.get('type') == "special":
            return self.ifStatement()
        elif self.lookahead.get('type') == "identifier":
            return self.variableDeclaration()
        else:
            return self.expressionStatement()
    
    def blockStatement(self):
        body = []
        # self.eat('block') is called in statement list as there is a possibility
        # of multiple statements in a block statement
        if self.lookahead != None:
            # Combine the statement list into the body
            body += self.statementList("block")
            ast = {
                'type': 'BlockStatement',
                'body': body
            }
            return ast
        raise SyntaxError("Invalid Syntax")

    def ifStatement(self):
        expr = [] # What to test in the if statement
        body = [] # Content of if statement
        # Add 1 block token to each call of if statement
        self.blockChecker += 1
        
        # if-type Literal/ArithmeticExpr/BinaryExpr/LogicalExpr:
        # BlockStatement
        ifType = self.eat("special").get('value')
        # Syntax for if and elif
        if ifType == 'if' or ifType == 'elif':
            expr.append(self.expression())
            if self.lookahead != None:
                # If next token = ar operators, replace with Arithmetic Expr
                # If next token = com operators, replace with Binary Expr
                if self.lookahead.get('type') == 'ar-operators' or \
                    self.lookahead.get('type') == 'com-operators':
                    expr = self.expression(expr[-1])
                    # If next token is log operators, replace with Logical Expr  
                    if self.lookahead != None and \
                        self.lookahead.get('type') == 'log-operators':
                        expr = self.expression(expr)
                else:
                    raise SyntaxError("Invalid Syntax")

        # Check for :
        if self.lookahead != None and \
            self.lookahead.get('type') == ':':
            # If statement syntax
            self.eat(':')
            self.eat('statement')
        else:
            raise SyntaxError("Invalid Syntax")
        
        # Check for block statement
        if self.lookahead != None and \
            self.lookahead.get('type') == 'block':
            body.append(self.blockStatement())
        else:
            raise SyntaxError("Invalid Syntax")

        ast = {
            'type': 'IfStatement',
            'if-type': ifType,
            'test': expr,
            'body': body
        }
        return ast

    def variableDeclaration(self):
        tempVar = self.identifier(True)
        tempVarValue = tempVar.get('value')
        if self.lookahead != None:
            # Check if it is variable declaration e.g. identifier = value
            if self.lookahead.get('type') == 'asg-operators' and self.lookahead.get('value') == '=':
                
                # Add the variable name to the list
                var.append(tempVarValue)
                self.eat("asg-operators")
                # Get the value
                try:
                    value = self.expressionStatement()

                    ast = {
                        'type': 'VariableDeclaration',
                        'variable' : var[-1],
                        'value': value
                    }
                    return ast
                # If there is no value, raise error
                except:
                    raise SyntaxError("Invalid Syntax")

        # If not variable declaration, check if var exists
        if tempVarValue in var:
            # Call regular expression statement
            return self.expressionStatement(tempVar)
        # If it doesn't exist, raise error
        else:
            raise SyntaxError("Variable doesn't exist")

    
    def expressionStatement(self, identifier=None):
        if identifier != None:
            expr = [identifier]
        else:
            expr = [self.expression()]
        # Loop while hasn't reached end of file or end of statement 
        while self.lookahead != None and self.lookahead.get('type') != "statement":
            # If next token = ar operators, replace with Arithmetic Expr
            # If next token = com operators, replace with Binary Expr
            if self.lookahead.get('type') == 'ar-operators' or \
                self.lookahead.get('type') == 'com-operators':
                expr = self.expression(expr[-1])
                # If next token is log operators, replace with Logical Expr  
                if self.lookahead != None and \
                    self.lookahead.get('type') == 'log-operators':
                    expr = self.expression(expr)
                break

            # Append expression
            expr.append(self.expression())
            # If reached end of file break from loop
            if self.lookahead == None:
                break
            
        ast = {
            'type': 'ExpressionStatement',
            'expression': expr
        }
        # If reached end of file return ast
        if self.lookahead == None:
            return ast
        # Else check for end of statement
        else:
            self.eat("statement")
        return ast
        
    def expression(self, expr=None):
        if self.lookahead.get('type') == 'ar-operators':
            return self.arithmeticExpression(expr)
        elif self.lookahead.get('type') == 'asg-operators':
            return self.operator('asg-operators')
        elif self.lookahead.get('type') == 'com-operators':
            return self.binaryExpression(expr)
        elif self.lookahead.get('type') == 'log-operators':
            return self.logicalExpression(expr)
        elif self.lookahead.get('type') == 'identifier':
            return self.identifier()
        else:
            return self.literal()

    def arithmeticExpression(self, expr):
        tempExpr = []
        # Literal/Identifier <operator> Literal/Identifier
        if expr != None and 'Literal' in expr.get('type') or \
            expr != None and 'Identifier' in expr.get('type'):
            # Append token
            tempExpr.append(expr)
            # While haven't reached end of file and there are still
            # ar op, keep adding to tempExpr
            while self.lookahead != None and \
                self.lookahead.get('type') == 'ar-operators':
                tempExpr.append(self.operator('ar-operators'))
                # If haven't reached end of file
                if self.lookahead != None:
                    tempExpr.append(self.expression())
                    # Arithmetic expression syntax
                    if 'Literal' in tempExpr[-1].get('type') or \
                        'Identifier' in tempExpr[-1].get('type'):
                        pass
                else:
                    # If doesn't fulfill syntax
                    raise SyntaxError("Invalid Syntax")

            ast = {
                'type': 'ArithmeticExpression',
                'expression': tempExpr
            }
            return ast
        # If doesn't fulfill syntax 
        raise SyntaxError("Invalid Syntax")

    def binaryExpression(self, expr):
        tempExpr = []
        # Literal/Identifier <operator> Literal/Identifier
        if expr != None and 'Literal' in expr.get('type') or \
            expr != None and 'Identifier' in expr.get('type'):
            # Append token
            tempExpr.append(expr)
            # While haven't reached end of file and there are still
            # com op, keep adding to tempExpr
            while self.lookahead != None and \
                self.lookahead.get('type') == 'com-operators':
                tempExpr.append(self.operator('com-operators'))
                # If haven't reached end of file
                if self.lookahead != None:
                    tempExpr.append(self.expression())
                    # Binary expression syntax
                    if 'Literal' in tempExpr[-1].get('type') or \
                        'Identifier' in tempExpr[-1].get('type'):
                        pass
                else:
                    # If doesn't fulfill syntax
                    raise SyntaxError("Invalid Syntax")

            ast = {
                'type': 'BinaryExpression',
                'expression': tempExpr
            }
            return ast
        # If doesn't fulfill syntax 
        raise SyntaxError("Invalid Syntax")
        
    def logicalExpression(self, expr):
        tempExpr = []
        # BinaryExpr/ArithmeticExpr <operator> BinaryExpr/ArithmeticExpr
        if expr != None and 'Binary' in expr.get('type') or \
            expr != None and 'Arithmetic' in expr.get('type'):
            tempExpr.append(expr)
            while self.lookahead != None and \
                self.lookahead.get('type') == 'log-operators':
                tempExpr.append(self.eat('log-operators')) # Append logical op
                # While doesn't reach end of file
                if self.lookahead != None:
                    # Call next token to pass to binary expr
                    lastToken = self.expression()
                    # Check if the next token is com op
                    if self.lookahead.get('type') == 'com-operators':
                        # Check for binary expression and pass the last token
                        tempExpr.append(self.binaryExpression(lastToken))
                    # Check if the next token is ar op
                    elif self.lookahead.get('type') == 'ar-operators':
                        # Check for arithmetic expression and pass the last token
                        tempExpr.append(self.arithmeticExpression(lastToken))
                else:
                    raise SyntaxError("Invalid Syntax")
            ast = {
                'type': 'LogicalExpression',
                'expression': tempExpr
            }
            return ast
        # If doesn't fulfill syntax 
        raise SyntaxError("Invalid Syntax")


    def operator(self, operator):
        token = self.eat(operator)
        ast = {
            'type': 'Operator',
            'value': token.get('value')
        }
        return ast
    
    def identifier(self, declaration = False):
        token = self.eat('identifier')
        value = token.get('value')
        if declaration == False:
            if value not in var:
                raise SyntaxError("Variable Not Declared")
        ast = {
            'type': 'Identifier',
            'value': token.get('value')
        }
        return ast
    
    def literal(self):
        # Get token type
        tokenType = self.lookahead.get('type')
        if tokenType == 'NUMBER':
            return self.numericalLiteral()
        elif tokenType == 'STRING':
            return self.stringLiteral()
        elif tokenType == 'BOOLEAN':
            return self.booleanLiteral()
        elif tokenType == 'NONE':
            return self.noneLiteral()
        # If none of the token type matches
        else:
            print(tokenType)
            raise ValueError("Unsupported Literal Type")

    def numericalLiteral(self):
        token = self.eat('NUMBER')   
        ast = {
            'type': 'NumericalLiteral',
            'value': token.get('value')
        }
        return ast
    
    def stringLiteral(self):
        token = self.eat('STRING')
        ast = {
            'type': 'StringLiteral',
            'value': token.get('value')[1:-1] # To not include the ""
        }
        return ast

    def booleanLiteral(self):
        token = self.eat('BOOLEAN')
        ast = {
            'type': 'BooleanLiteral',
            'value': token.get('value')
        }
        return ast

    def noneLiteral(self):
        token = self.eat('NONE')
        ast = {
            'type': 'NoneLiteral',
            'value': token.get('value')
        }
        return ast

    # Function to consume token type and check with the input
    # Then get next token
    def eat(self, tokenType):
        token = self.lookahead
        # If reached end of file
        if token == None:
            raise ValueError("Reached End of File") 
        # Different token type from input
        if token.get('type') != tokenType:
            print(tokenType, token)
            raise ValueError("Unmatched Token Value")
        # Get the next text
        self.lookahead = self.t.getNextToken('eat')
        return token
