# MIT License
# 
# Copyright (c) 2024 Connor-Jay Dunn
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re

sql_errors = {
    "MySQL": (
        r"SQL syntax.*MySQL",
        r"Warning.*mysql_.*",
        r"MySQL Query fail.*",
        r"SQL syntax.*MariaDB server"
    ),
    "PostgreSQL": (
        r"PostgreSQL.*ERROR",
        r"Warning.*\Wpg_.*",
        r"Warning.*PostgreSQL"
    ),
    #"Microsoft SQL Server": (
    #    r"OLE DB.* SQL Server",
    #    r"(\W|\A)SQL Server.*Driver",
    #    r"Warning.*odbc_.*",
    #    r"Warning.*mssql_",
    #    r"Msg \d+, Level \d+, State \d+",
    #    r"Unclosed quotation mark after the character string",
    #    r"Microsoft OLE DB Provider for ODBC Drivers"
    #),
    #"Microsoft Access": (
    #    r"Microsoft Access Driver",
    #    r"Access Database Engine",
    #    r"Microsoft JET Database Engine",
    #    r".*Syntax error.*query expression"
    #),
    #"Oracle": (
    #    r"\bORA-[0-9][0-9][0-9][0-9]",
    #    r"Oracle error",
    #    r"Warning.*oci_.*",
    #    "Microsoft OLE DB Provider for Oracle"
    #),
    #"IBM DB2": (
    #    r"CLI Driver.*DB2",
    #    r"DB2 SQL error"
    #),
    "SQLite": (
        r"SQLite/JDBCDriver",
        r"System.Data.SQLite.SQLiteException"
    ),
    #"Informix": (
    #    r"Warning.*ibase_.*",
    #    r"com.informix.jdbc"
    #),
    #"Sybase": (
    #    r"Warning.*sybase.*",
    #    r"Sybase message"
    #)
}

def detect_dbms_error(response):
    """
    Detects if a response contains any known DBMS error message(s).

    Parameters:
        response (str): The response text to analyse for DBMS error message(s).

    Returns:
        bool: True if an DBMS error message was found, false otherwise.
    """
    for db, errors in sql_errors.items():
        for error in errors:
            if re.compile(error).search(response):
                return True
    return False
